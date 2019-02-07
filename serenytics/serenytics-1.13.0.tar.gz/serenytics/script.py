import json
import logging
from copy import deepcopy

import time

from .helpers import SerenyticsException, make_request
from . import settings

logger = logging.getLogger(__name__)


class UnknownScript(SerenyticsException):
    def __init__(self, uuid_or_name):
        super(UnknownScript, self).__init__(u'Script with uuid or name "{}" does not exist'.format(uuid_or_name))


class ScriptFailure(SerenyticsException):
    def __init__(self, name, log):
        super(ScriptFailure, self).__init__(u'Script execution failed "{name}":\nstdout: {stdout}\nstderr: {stderr}'
                                            .format(name=name,
                                                    stdout=log.stdout,
                                                    stderr=log.stderr))


class Script(object):
    """
    Serenytics script
    """

    def __init__(self, config, headers):
        self._config = config
        self._headers = headers

    @property
    def name(self):
        return self._config['name']

    @property
    def uuid(self):
        return self._config['uuid']

    def run(self, params=None, async=True, raise_on_error=True, log_result=False):
        """
        Run script

        :param params: Parameters to pass to the script execution
        :type params: dict

        :param async: Whether this call waits for the script execution to be finished.

        :param raise_on_error: Whether this call raises an exception if the script execution fails.

        :param log_result: Whether to log the script execution log.

        :return None if async=True. If async=False, returns the log of the execution
        :type: ScriptLog
        """
        run_url = settings.SERENYTICS_API_DOMAIN + '/api/script/' + self.uuid + '/run'
        script_params = deepcopy(params or {})

        # always run with async=True and then poll manually if result is needed synchronously
        # because using async=True on http request is limited to 5 minutes
        script_params['async'] = True
        make_request('post', run_url, data=json.dumps(script_params), headers=self._headers,
                     expected_json_status='ok')

        if not async:
            self.wait()
            logs = self.get_last_logs()
            last_log = logs[0]

            if log_result:
                logger.info('Ran script "{name}": \nstatus: {status}\nstdout: {stdout}\nstderr: {stderr}'
                            .format(name=self.name, status=last_log.status,
                                    stdout=last_log.stdout, stderr=last_log.stderr))

            if raise_on_error and last_log.is_failure:
                raise ScriptFailure(name=self.name, log=last_log)

            return last_log

    def wait(self, time_before_retry_s=1):
        """
        Wait for script execution to be finished
        """
        logger.info('Waiting for script execution to be finished, polling every %s s' % time_before_retry_s)
        while True:
            running = self.is_running()
            if not running:
                break
            time.sleep(time_before_retry_s)

    def is_running(self):
        """
        :return: Whether the current script is running
        """
        state_url = settings.SERENYTICS_API_DOMAIN + '/api/script/' + self.uuid + '/state'
        response = make_request('get', state_url, headers=self._headers, log_request=False)
        return response.json()['running']

    def get_last_logs(self):
        """
        Fetch last 10 logs
        :return:
        """
        logs_url = settings.SERENYTICS_API_DOMAIN + '/api/script/' + self.uuid + '/logs'
        response = make_request('get', logs_url, headers=self._headers)
        return [
            ScriptLog(data['started_at'], data['finished_at'], data['status'],
                      data['stdout'], data['stderr'], data['return_code'])
            for data in response.json()['objects']
        ]


class ScriptLog(object):
    """
    Result of one Script execution
    """

    def __init__(self, started_at, finished_at, status, stdout, stderr, return_code):
        self.started_at = started_at
        self.finished_at = finished_at
        self.status = status
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = return_code

    @property
    def is_failure(self):
        return self.status == 'FAILURE'

    @property
    def is_success(self):
        return self.status == 'SUCCESS'

    def __repr__(self):
        return '<ScriptLog status=%r>' % self.status
