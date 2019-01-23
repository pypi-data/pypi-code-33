###############################################################################
# (c) Copyright 2017 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Module in charge of dealing with sending and receiving nightlies information to
RabbitMQ when a project is done: slot, build id, platform and project
'''

import json
from collections import namedtuple

from lbmessaging.exchanges.Common import Sender, Receiver, Message,\
    check_channel
from lbmessaging.services.Common import ExposedIn


__author__ = 'Stefan-Gabriel Chitic <stefan-gabriel.chitic@cern.ch>'


CONTINUOUS_INTEGRATION_EXCHANGE = "topic.build_ready"


# Utility class to ease the use of the messages
ContinuousIntegrationMessage = namedtuple('ContinuousIntegration',
                                          sorted(['slot', 'build_id',
                                                  'platform', 'project',
                                                  'priority',
                                                  'deployment']),
                                          rename=True)


def _message_to_continuous_integration_build(message):
    """ Trivial utility that converts the command from JSON
    :param message: the message that needs to be converted to command
    :returns the converted rabbitMQ message to Message object with payload as
             ContinuousIntegrationMessage """
    ret = None
    if message and message.body:
        try:
            msg = json.loads(message.body)
        except:
            msg = message.body
        if isinstance(msg, list):
            msg = msg[0]
        try:
            body = ContinuousIntegrationMessage(**msg)
        except TypeError:
            # Add missing fields in the body to None
            for field in ContinuousIntegrationMessage._fields:
                if not msg.get(field, None):
                    msg[field] = None
            body = ContinuousIntegrationMessage(**msg)

        ret = Message(body, message.method_frame, message.header_frame)
    return ret


def build_ready_retry_count(build_ready):
    """ returns the retry_count kepts in the headers
    :param build_ready: the message whose retries needs to be counted
    :returns the value of the retry_count from the header
    """
    return build_ready.header_frame.headers.get('max_retry', None)


@ExposedIn('LbCIService', mapping={
        'send_build_ready': 'send_build_ready',
        'consume_build_ready': 'consume_build_ready'
    })
@ExposedIn('CVMFSNightliesService', mapping={
        'send_build_ready': 'send_build_ready',
        'receive_build_ready': 'receive_build_ready',
    })
class ContinuousIntegrationExchange(object):
    """
    Class in charge of dealing with messages to and from the
    ContinuousIntegration Exchange
    """

    def __init__(self, channel, connection=None):
        """
        :param channel: a pikaBlockingConnection channel that should be used in
                        the broker
        :param connection: a pikaBlockingConnection that should be used in
                        the broker"""
        self._channel = check_channel(channel, connection)

    def send_build_ready(self, slot, build_id, platform, project,
                         deployment=[], priority=None):
        """ Formats and sends the a pair of slot-build_id-platform-project
         that was build as JSON
        :param slot: the slot name that was build
        :param build_id: the build id of the slot that was build
        :param platform: the platform of the slot that was build
        :param project: the project of the slot that was build
        :param priority: the priority of the message
        :param max_retry: the max of retries in case of command failure on CVMFS
        :param expiration: the TTL of the message"""
        message = {
            'slot': slot,
            'build_id': build_id,
            'project': project,
            'platform': platform,
            'deployment': deployment,
            'priority': priority
        }
        routing_key = "%s.%s.%s.%s" % (slot, build_id, project, platform)
        s = Sender(CONTINUOUS_INTEGRATION_EXCHANGE,
                   channel=self._channel)
        s.send_message(routing_key, message, priority=0,
                       max_retry=0)

    def receive_build_ready(self, queue_name):
        """ Receive one message from the queue
        :param queue_name: the queue on which the broker listens for messages
        :returns the last message converted to Message object with payload as
                 ContinuousIntegrationMessage
        """
        r = Receiver(CONTINUOUS_INTEGRATION_EXCHANGE, queue_name,
                     channel=self._channel)
        message = r.receive_message(runBeforeAck=None)
        return _message_to_continuous_integration_build(message)

    def receive_all(self, queue_name):
        """ Receive all messages from the queue
        :param queue_name: the queue on which the broker listens for messages
        :returns a list of all the messages converted to Message object with
                 payload as ContinuousIntegrationMessage
        """
        r = Receiver(CONTINUOUS_INTEGRATION_EXCHANGE, queue_name,
                     channel=self._channel)
        msglist = r.receive_messages()
        return [_message_to_continuous_integration_build(m) for m in msglist]

    def consume_build_ready(self, message_processor, queue_name):
        """ Invokes the message_processor on all messages received.
         The message processor should:
         - take (message, channel) as arguments
         - return True to ack the messages

         It can interrupt the loop by calling channel.stop_consuming()

         BEWARE: This is not appropriate for long running calls as the
         acknowledgement of the message is done after the processor call.

        :param message_processor: the function that should be called when a new
                                  message is consumed
        :param queue_name: the queue on which the broker listens for messages
         """
        c = Receiver(CONTINUOUS_INTEGRATION_EXCHANGE, queue_name,
                     channel=self._channel)
        # Adding wrapper to convert the messages before processing
        def convert_and_process(message):
            return message_processor(_message_to_continuous_integration_build(message))
        c.consume_message(convert_and_process)