## @file PbWK.py
# @brief Protobuf Web Algorithm
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

from pbose.protobuf import PbWA_pb2
from pbose.protobuf import PbWK_pb2

from pbose import object_pb
import bitstring

class PbWK(object_pb):

  def _wrapped_protobuf(self):
    return PbWK_pb2.PbWK()

  @classmethod
  def from_private_key(cls, private_key):
    # TODO: check key type, for now assume P256R1
    # PbWK Type
    kty_ec = PbWA_pb2.PbWKTypeEC()
    kty_ec.crv = PbWA_pb2.PbWKTypeECCurve.P256
    kty_ec.x = bitstring.BitArray(uint=private_key.private_numbers().public_numbers.x, length=32*8).bytes
    kty_ec.y = bitstring.BitArray(uint=private_key.private_numbers().public_numbers.y, length=32*8).bytes
    kty_ec.d = bitstring.BitArray(uint=private_key.private_numbers().private_value, length=32*8).bytes
    log.debug(kty_ec)
    # PbWK
    pbwk = PbWK_pb2.PbWK()
    pbwk.kty = PbWA_pb2.PbWKType.EC
    pbwk.kty_prop_ec.CopyFrom(kty_ec)
    pbwk.kid = "kid"
    log.debug(pbwk)
    # PbWK obj
    pbwk_obj = cls(pbwk)
    return pbwk_obj

  @classmethod
  def from_public_key(cls, public_key):
    # TODO: check key type, for now assume P256R1
    # PbWK Type
    kty_ec = PbWA_pb2.PbWKTypeEC()
    kty_ec.crv = PbWA_pb2.PbWKTypeECCurve.P256
    kty_ec.x = bitstring.BitArray(uint=public_key.public_numbers().x, length=32*8).bytes
    kty_ec.y = bitstring.BitArray(uint=public_key.public_numbers().y, length=32*8).bytes
    log.debug(kty_ec)
    # PbWK
    pbwk = PbWK_pb2.PbWK()
    pbwk.kty = PbWA_pb2.PbWKType.EC
    pbwk.kty_prop_ec.CopyFrom(kty_ec)
    pbwk.kid = "kid"
    log.debug(pbwk)
    # PbWK obj
    pbwk_obj = cls(pbwk)
    return pbwk_obj
