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
Module in charge of dealing with sending and receiving commands for the
/cvmfs/lhcbdev.cern.ch
'''

import datetime
from collections import namedtuple

from lbmessaging.exchanges.Common import Sender, Receiver, Message, check_channel

__author__ = 'Ben Couturier <ben.couturier@cern.ch>'


# Utility class to ease the use of the messages
CommandMessage = namedtuple('CommandBody',
                            ['command', 'arguments', 'trigger_date'])


def _message_to_command(message):
    """ Trivial utility that converts the command from JSON
    :param message: the message that needs to be converted to command
    :returns the converted rabbitMQ message to Message object with payload as
             command message
    """
    ret = None
    if message and message.body:
        body = CommandMessage(*message.body)
        ret = Message(body, message.method_frame, message.header_frame)
    return ret


def command_retry_count(command):
    """ returns the retry_count kept in the headers
    :param command: the command message whose retries needs to be counted
    :returns the value of the retry_count from the header
    """
    return command.header_frame.headers.get('max_retry', None)


class CommandExchange(object):
    """
    Class in charge of dealing with messages to and from the CvmfsDevExchange
    """

    def __init__(self, channel, exchange, error_exchange, connection=None):
        """
        Specify the exchange to be used
        :param channel: a pikaBlockingConnection channel that should be used in
                        the broker
        :param exchange: the main exchange name used in the broker
        :param error_exchange: the error exchange that should be used to push
                               a command that failed i.e. the retry_count == 0
        :param connection: a pikaBlockingConnection that should be used in
                        the broker
        """
        self._channel = check_channel(channel, connection)
        self._exchange = exchange
        self._error_exchange = error_exchange

    def send_command(self, command, arguments, priority=10, max_retry=3,
                     expiration=None):
        """ Formats and sends the command as JSON
        :param command: the command that should be executed on a CVMFS instance
        :param arguments: the command arguments
        :param priority: the priority of the message
        :param max_retry: the max of retries in case of command failure on CVMFS
        :param expiration: the TTL of the message
        """
        now = datetime.datetime.utcnow().isoformat()
        s = Sender(self._exchange, channel=self._channel)
        s.send_message(command, (command, arguments, now), priority,
                       expiration=expiration,
                       max_retry=max_retry)

    def receive_command(self, queue_name):
        """ Receive one message from the queue
        :param queue_name: the queue on which the broker listens for messages
        :returns the last message converted to Message object with payload as
                 command message
        """
        r = Receiver(self._exchange, queue_name,
                     channel=self._channel)
        message = r.receive_message()
        return _message_to_command(message)

    def receive_all(self, queue_name):
        """ Receive all messages from the queue
        :param queue_name: the queue on which the broker listens for messages
        :returns a list of all the messages converted to Message object with
                 payload as command message
        """
        r = Receiver(self._exchange, queue_name,
                     channel=self._channel)
        msglist = r.receive_messages()
        return [_message_to_command(m) for m in msglist]

    def handle_processing_error(self, command):
        """ Handles the processing error, i.e. resend if retry_count > 0,
        forward to the error queue otherwise
        :param command: the command that should be executed on a CVMFS instance
        """
        retry_count = command_retry_count(command)
        if retry_count > 0:
            s = Sender(self._exchange, channel=self._channel)
            s.resend_message(command)
        else:
            s = Sender(self._error_exchange, channel=self._channel)
            s.resend_message(command, keep_retry_count=True)
