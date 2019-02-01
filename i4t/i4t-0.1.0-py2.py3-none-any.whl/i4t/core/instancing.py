## @file instancing.py
# @brief I4T Instancing Token
#
# @copyright
# Copyright 2018 I4T <https://i4t.io>
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

from i4t.protobuf import Instancing_pb2

from pbose import object_pb
from pbose.PbWK import PbWK
from pbose.PbWS import PbWS
from pbose.PbWT import PbWT

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec

from bitstring import BitArray
from base64 import urlsafe_b64encode

class InstancingToken(PbWT):

  @classmethod
  def generate(cls, public_key, serial):
    # TODO: load Instancing Certificate
    certificate = ec.generate_private_key(ec.SECP384R1(), default_backend())
    # Instancing Token Claims
    claims_pb = Instancing_pb2.InstancingTokenClaims()
    claims_pb.public_key.CopyFrom(PbWK.from_public_key(public_key).protobuf)
    claims_pb.serial = serial
    log.debug(claims_pb)
    # bytes
    claims_bytes = claims_pb.SerializeToString()
    log.debug(claims_bytes)
    # PbWT
    pbwt_obj = PbWT.with_claims(private_claims=claims_bytes)
    log.debug("PbWT")
    log.debug(pbwt_obj)
    # InstancingToken
    token_obj = cls(pbwt_obj)
    log.debug("InstancingToken")
    log.debug(token_obj)
    return token_obj

  @property
  def instancing_claims(self):
    claims_pb = Instancing_pb2.InstancingTokenClaims()
    claims_pb.ParseFromString(self.private_claims)
    return claims_pb

  @property
  def serial(self):
    return self.instancing_claims.serial

class InstancingWarrant(object_pb):

  def _wrapped_protobuf(self):
    return Instancing_pb2.InstancingWarrant()

  @classmethod
  def generate(cls, serial):
    # generate private key
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    public_key = private_key.public_key()
    # generate token
    token = InstancingToken.generate(public_key, serial)
    # generate warrant
    warrant_pb = Instancing_pb2.InstancingWarrant()
    warrant_pb.version = 1
    warrant_pb.token.CopyFrom(token.protobuf)
    warrant_pb.private_key.CopyFrom(PbWK.from_private_key(private_key).protobuf)
    log.debug(warrant_pb)
    # InstancingWarrant
    warrant_obj = cls(warrant_pb)
    log.debug("InstancingWarrant")
    log.debug(warrant_obj)
    return warrant_obj

  @property
  def version(self):
    return self.protobuf.version

  @property
  def token(self):
    return InstancingToken(self.protobuf.token)

  @property
  def private_key(self):
    return PbWK(self.protobuf.private_key)
