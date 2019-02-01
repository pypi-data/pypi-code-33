## @file PbWS.py
# @brief Protobuf Web Signature
#
# @copyright
# Copyright 2018 PbOSE <https://pbose.io>
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

import logging, os
log = logging.getLogger().getChild(__name__)

from pbose.protobuf import PbWS_pb2

from pbose import object_pb

class PbWS(object_pb):

  def _wrapped_protobuf(self):
    return PbWS_pb2.PbWS()

  @classmethod
  def with_fields(cls, protected=b'', header=b'', payload=b'', signature=b''):
    # PbWS
    pbws_pb = PbWS_pb2.PbWS()
    pbws_pb.protected = protected
    pbws_pb.header = header
    pbws_pb.payload = payload
    pbws_pb.signature = signature
    log.debug(pbws_pb)
    # PbWS obj
    pbws_obj = cls(pbws_pb)
    log.debug(pbws_obj)
    return pbws_obj

  @property
  def protected(self):
    return self.protobuf.protected

  @property
  def header(self):
    return self.protobuf.header

  @property
  def payload(self):
    return self.protobuf.payload

  @property
  def signature(self):
    return self.protobuf.signature
