## @file __init__.py
# @brief pbose - PbOSE
#
# @copyright
# Copyright 2019 pbose <https://pbose.io>
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##

from google.protobuf.message import Message
from google.protobuf.json_format import MessageToJson, Parse

import base64

from abc import ABCMeta, abstractmethod, abstractproperty
from six import add_metaclass, binary_type, text_type

@add_metaclass(ABCMeta)
class object_pb(object):

  @abstractproperty
  def _wrapped_protobuf(self):
    pass

  def __init__(self, bytes_protobuf_base64=None):
    # check if type is obj
    if isinstance(bytes_protobuf_base64, object_pb):
      self.__init__(bytes_protobuf_base64.protobuf)
    # check if type is bytes
    elif isinstance(bytes_protobuf_base64, binary_type):
      self._protobuf = self._wrapped_protobuf()
      self._protobuf.ParseFromString(bytes_protobuf_base64)
    # check if type is protobuf
    elif isinstance(bytes_protobuf_base64, Message):
      self._protobuf = bytes_protobuf_base64
    # check if type is base64
    elif isinstance(bytes_protobuf_base64, text_type):
      base64 = bytes_protobuf_base64
      bytes = base64.urlsafe_b64decode(base64.encode())
      self._protobuf = self._wrapped_protobuf()
      self._protobuf.ParseFromString(bytes)
    # TODO JSON
    # else
    else:
      self._protobuf = self._wrapped_protobuf()

  def _updated_protobuf(self):
    pass # TODO REMOVE

  @property
  def protobuf(self):
    return self._protobuf

  @property
  def bytes(self):
    return self.protobuf.SerializeToString()

  @property
  def base64(self):
    return base64.urlsafe_b64encode(self.bytes).decode('ascii')

  def __str__(self):
    return str(self.protobuf)
