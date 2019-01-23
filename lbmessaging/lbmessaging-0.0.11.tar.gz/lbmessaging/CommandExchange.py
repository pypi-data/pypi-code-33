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
import json
from lbmessaging.Common import Sender, Receiver, Message, check_channel
from collections import namedtuple

__author__ = 'Ben Couturier <ben.couturier@cern.ch>'


# Utility class to ease the use of the messages
CommandMessage = namedtuple('CommandBody',
                            ['command', 'arguments', 'trigger_date'])


def _message_to_command(message):
    """ Trivial utility that converts the command from JSON"""
    ret = None
    if message and message.body:
        body = CommandMessage(*message.body)
        ret = Message(body, message.method_frame, message.header_frame)
    return ret


def command_retry_count(command):
    """ returns the retry_count kepts in the headers """
    return command.header_frame.headers.get('max_retry', None)


class CommandExchange(object):
    """
    Class in charge of dealing with messages to and from the CvmfsDevExchange
    """

    def __init__(self, channel, exchange, error_exchange, connection=None):
        """
        Specify the exchange to be used
        """
        self._channel = check_channel(channel, connection)
        self._exchange = exchange
        self._error_exchange = error_exchange

    def send_command(self, command, arguments, priority=10, max_retry=3,
                     expiration=None):
        """ Formats and sends the command as JSON """
        now = datetime.datetime.utcnow().isoformat()
        s = Sender(self._exchange, channel=self._channel)
        s.send_message(command, (command, arguments, now), priority,
                       expiration=expiration,
                       max_retry=max_retry)

    def receive_command(self, queue_name):
        """ Receive one message from the queue"""
        r = Receiver(self._exchange, queue_name,
                     channel=self._channel)
        message = r.receive_message()
        return _message_to_command(message)

    def receive_all(self, queue_name):
        """ Receive all messages from the queue"""
        r = Receiver(self._exchange, queue_name,
                     channel=self._channel)
        msglist = r.receive_messages()
        return [_message_to_command(m) for m in msglist]

    def handle_processing_error(self, command):
        """ Handles the processing error, i.e. resend if retry_count > 0,
        forward to the error queue otherwise """
        retry_count = command_retry_count(command)
        if retry_count > 0:
            s = Sender(self._exchange, channel=self._channel)
            s.resend_message(command)
        else:
            s = Sender(self._error_exchange, channel=self._channel)
            s.resend_message(command, keep_retry_count=True)
