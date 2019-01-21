# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2019 Albert Moky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

"""
    Message with Envelope
    ~~~~~~~~~~~~~~~~~~~~~

    Base classes for messages
"""

from mkm import ID


class Envelope(dict):
    """
        This class is used to create a message envelope
        which contains 'sender', 'receiver' and 'time'
    """

    def __new__(cls, envelope: dict=None,
                sender: ID=None, receiver: ID=None, time: int=0):
        """
        Create message envelope object with env info

        :param envelope: A dictionary as envelope info
        :param sender:   An ID string
        :param receiver: An ID string
        :param time:     A integer number as timestamp
        :return: Envelope object
        """
        if envelope:
            # return Envelope object directly
            if isinstance(envelope, Envelope):
                return envelope
            # get fields from dictionary
            sender = ID(envelope['sender'])
            receiver = ID(envelope['receiver'])
            if 'time' in envelope:
                time = int(envelope['time'])
            else:
                time = 0
        elif sender and receiver:
            envelope = {
                'sender': sender,
                'receiver': receiver,
                'time': time,
            }
        else:
            raise AssertionError('Envelope parameters error')
        # new Envelope(dict)
        self = super().__new__(cls, envelope)
        self.sender = sender
        self.receiver = receiver
        self.time = time
        return self


class Message(dict):
    """
        This class is used to create a message
        with the envelope fields, such as 'sender', 'receiver', and 'time'
    """

    def __new__(cls, msg: dict):
        self = super().__new__(cls, msg)
        env = {
            'sender': msg['sender'],
            'receiver': msg['receiver'],
        }
        if 'time' in msg:
            env['time'] = msg['time']
        self.envelope = Envelope(env)
        return self
