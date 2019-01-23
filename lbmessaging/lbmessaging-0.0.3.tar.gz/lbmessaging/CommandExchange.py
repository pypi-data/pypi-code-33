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
from Common import Sender, Receiver, Message
from collections import namedtuple

__author__ = 'Ben Couturier <ben.couturier@cern.ch>'


# Utility class to ease the use of the messages
CommandMessage = namedtuple('CommandBody', sorted(
    ['command', 'arguments',
     'trigger_date']))


def _message_to_command(message):
    """ Trivial utility that converts the command from JSON"""
    ret = None
    if message and message.body:
        try:
            msg = json.loads(message.body)
        except:
            msg = message.body
        body = CommandMessage(**msg)
        ret = Message(body, message.method_frame, message.header_frame)
    return ret


def _command_to_message(command):
    """ Trivial utility that converts the command from JSON"""
    ret = None
    if command and command.body is not None:
        msg = json.dumps(command.body._asdict())
        ret = Message(msg, command.method_frame, command.header_frame)
    return ret


def command_retry_count(command):
    """ returns the retry_count kepts in the headers """
    return command.header_frame.headers.get('max_retry', None)


class CommandExchange(object):
    """
    Class in charge of dealing with messages to and from the CvmfsDevExchange
    """

    def __init__(self, connection, exchange, error_exchange):
        self._connection = connection
        self._exchange = exchange
        self._error_exchange = error_exchange

    def send_command(self, command, arguments, priority=10, max_retry=3):
        """ Formats and sends the command as JSON """
        message = {
            'command': command,
            'arguments': arguments,
            'trigger_date': datetime.datetime.utcnow().isoformat()
        }
        s = Sender(self._exchange, connection=self._connection)
        s.send_message(command, message, priority,
                       max_retry=max_retry)

    def receive_command(self, queue_name):
        """ Receive one message from the queue"""
        r = Receiver(self._exchange, queue_name,
                     connection=self._connection)
        message = r.receive_message()

        return _message_to_command(message)

    def receive_all(self, queue_name):
        """ Receive all messages from the queue"""
        r = Receiver(self._exchange, queue_name,
                     connection=self._connection)
        msglist = r.receive_messages()
        return [_message_to_command(m) for m in msglist]

    def handle_processing_error(self, command):
        """ Handles the processing error, i.e. resend if retry_count > 0,
        forward to the error queue otherwise """
        retry_count = command_retry_count(command)
        if retry_count > 0:
            s = Sender(self._exchange, connection=self._connection)
            s.resend_message(_command_to_message(command))
        else:
            s = Sender(self._error_exchange, connection=self._connection)
            s.resend_message(_command_to_message(command),
                             keep_retry_count=True)
