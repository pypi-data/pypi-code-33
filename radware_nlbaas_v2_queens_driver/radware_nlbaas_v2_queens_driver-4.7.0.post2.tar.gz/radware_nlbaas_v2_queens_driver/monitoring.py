# Copyright 2018, Radware LTD. All rights reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import threading
import time
import traceback

from six.moves import queue as Queue

from oslo_log import log as logging
import radware_lbaas_driver

import rest_client as rc

COMPLETION_CHECK_INTERVAL = 3

LOG = logging.getLogger(__name__)


class OperationAttributes(object):
    def __init__(self,
                 operation_url,
                 ctx=None,
                 post_operation_function=None):
        self.ctx = ctx
        self.operation_url = operation_url
        self.post_operation_function = post_operation_function
        self.result = None

    def __repr__(self):
        attrs = self.__dict__
        items = ("%s = %r" % (k, v) for k, v in attrs.items())
        return "<%s: {%s}>" % (self.__class__.__name__, ', '.join(items))


class CRUDOperationAttributes(OperationAttributes):
    def __init__(self,
                 ctx,
                 manager,
                 operation_url,
                 lb,
                 data_model=None,
                 old_data_model=None,
                 delete=False,
                 post_operation_function=None):
        super(CRUDOperationAttributes, self).__init__(
            operation_url, **{'ctx': ctx, 'post_operation_function': post_operation_function})
        self.manager = manager
        self.lb = lb
        self.data_model = data_model
        self.old_data_model = old_data_model
        self.delete = delete


class CompletionMonitor(threading.Thread):
    def __init__(self, rest_client, plugin):
        threading.Thread.__init__(self)
        self.rest_client = rest_client
        self.plugin = plugin
        self.stoprequest = threading.Event()
        self.opers_to_handle_before_rest = 0
        self.name = 'COMPLETION_MONITOR'

    def join(self, timeout=None):
        self.stoprequest.set()
        super(CompletionMonitor, self).join(timeout)

    def run(self):
        while not self.stoprequest.isSet():
            try:
                oper = radware_lbaas_driver.RadwareLBaaSV2Driver.queue.get()

                # Get the current queue size (N) and set the counter with it.
                # Handle N operations with no intermission.
                # Once N operations handles, get the size again and repeat.
                if self.opers_to_handle_before_rest <= 0:
                    self.opers_to_handle_before_rest =\
                        radware_lbaas_driver.RadwareLBaaSV2Driver.queue.qsize() + 1

                radware_lbaas_driver.RadwareLBaaSV2Driver.queue.task_done()
                self.opers_to_handle_before_rest -= 1

                # check the status - if oper is done: update the db ,
                # else push the oper again to the queue
                if not self._handle_operation_completion(oper):
                    LOG.debug('COMPLETION: Operation %s not completed.' % repr(oper.operation_url))
                    radware_lbaas_driver.RadwareLBaaSV2Driver.queuelock.acquire()
                    radware_lbaas_driver.RadwareLBaaSV2Driver.queue.put(oper)
                    radware_lbaas_driver.RadwareLBaaSV2Driver.queuelock.release()
                else:
                    LOG.debug('COMPLETION: Operation %s completed.' % repr(oper.operation_url))


                # Take one second rest before start handling
                # new operations or operations handled before
                if self.opers_to_handle_before_rest <= 0:
                    time.sleep(COMPLETION_CHECK_INTERVAL)

            except Queue.Empty:
                continue
            except Exception as e:
                LOG.error('COMPLETION: Exception was thrown (' + repr(e.message) + ')')

    def _handle_operation_completion(self, oper):
        result = self.rest_client.call('GET',
                                       oper.operation_url,
                                       None,
                                       None)
        res_data = result[rc.RESP_DATA]
        LOG.debug('Operation completion requested %(uri)s and got: %(result)s',
                  {'uri': oper.operation_url, 'result': res_data})
        completed = res_data['complete']
        reason = result[rc.RESP_REASON],
        description = result[rc.RESP_STR]
        if completed:
            LOG.debug('Operation %s is completed after %d seconds '
                      'with success status: %s :' %
                      (oper, result[rc.RESP_DATA]['duration'], res_data['success']))
            if not res_data['success']:
                if reason or description:
                    msg = 'Reason:%s. Description:%s' % (reason, description)
                else:
                    msg = "unknown"
                LOG.error(
                    'Operation %s failed. Reason: %s' % (oper, msg))

            oper.result = res_data
            if oper.post_operation_function:
                oper.post_operation_function(oper)

        return completed


class StatusMonitor(threading.Thread):
    def __init__(self,
                 rest_client, monitoring_pace,
                 status_action_name, stats_action_name,
                 status_feedback=None,
                 stats_feedback=None):
        threading.Thread.__init__(self)

        self.rest_client = rest_client
        self.monitoring_pace = monitoring_pace
        self.status_action_name = status_action_name
        self.stats_action_name = stats_action_name
        self.status_feedback = status_feedback
        self.stats_feedback = stats_feedback

        self.stoprequest = threading.Event()
        self.name = 'STATUS_MONITOR'

    def join(self, timeout=None):
        self.stoprequest.set()
        super(StatusMonitor, self).join(timeout)

    def run(self):
        while not self.stoprequest.isSet():
            time.sleep(self.monitoring_pace)
            result = self.rest_client.call('GET', '/api/runnable/Workflow', None, None)

            if 'names' not in result[rc.RESP_DATA]:
                continue

            names = result[rc.RESP_DATA]['names']
            lb_wf_names = [n for n in names if n.startswith('NLBaaS_LB-')]
            for wf_name in lb_wf_names:
                if self.status_feedback:
                    LOG.debug('STATUS: Running status action on:' + repr(wf_name))
                    response = self._run_action(wf_name, self.status_action_name)
                    oper = OperationAttributes(
                        response['uri'],
                        post_operation_function=self.status_feedback)

                    radware_lbaas_driver.RadwareLBaaSV2Driver.queuelock.acquire()
                    radware_lbaas_driver.RadwareLBaaSV2Driver.queue.put(oper)
                    radware_lbaas_driver.RadwareLBaaSV2Driver.queuelock.release()

                if self.stats_feedback:
                    LOG.debug('STATUS: Running stats action on:' + repr(wf_name))
                    response = self._run_action(wf_name, self.stats_action_name)
                    oper = OperationAttributes(
                        response['uri'],
                        post_operation_function=self.stats_feedback)
                    radware_lbaas_driver.RadwareLBaaSV2Driver.queuelock.acquire()
                    radware_lbaas_driver.RadwareLBaaSV2Driver.queue.put_nowait(oper)
                    radware_lbaas_driver.RadwareLBaaSV2Driver.queuelock.release()

    def _run_action (self, wf_name, action_name):
        resource = '/api/runnable/Workflow/%s/%s' % (
        wf_name, action_name)
        response = rc.rest_wrapper(self.rest_client.call(
            'POST', resource,
            {},
            rc.JSON_HEADER))
        return response
