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
    Message Contents
    ~~~~~~~~~~~~~~~

    Extents from Content
"""

import random

from dkd.content import MessageType, Content, message_content_classes
from dkd.transform import ReliableMessage


def serial_number():
    """
    :return: random integer equals or greater than 1
    """
    return random.randint(1, 2**32)


class TextContent(Content):

    def __init__(self, content: dict):
        super().__init__(content)
        self.text = content['text']

    @classmethod
    def new(cls, text: str='') -> Content:
        content = {
            'type': MessageType.Text,
            'sn': serial_number(),
            'text': text,
        }
        return TextContent(content)


class CommandContent(Content):

    def __init__(self, content: dict):
        super().__init__(content)
        self.command = content['command']

    @classmethod
    def new(cls, command: str='') -> Content:
        content = {
            'type': MessageType.Command,
            'sn': serial_number(),
            'command': command,
        }
        return CommandContent(content)


class ForwardContent(Content):

    def __init__(self, content: dict):
        super().__init__(content)
        if 'forward' in content:
            msg = content['forward']
        else:
            raise ValueError('Forward message not found')
        self.forward = ReliableMessage(msg)

    @classmethod
    def new(cls, message: ReliableMessage):
        content = {
            'type': MessageType.Forward,
            'sn': serial_number(),
            'forward': message,
        }
        return ForwardContent(content)


"""
    Message Content Classes Map
"""

message_content_classes[MessageType.Text] = TextContent
message_content_classes[MessageType.Command] = CommandContent
message_content_classes[MessageType.Forward] = ForwardContent
