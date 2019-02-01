## @file PbWT.py
# @brief Protobuf Web Token
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

from pbose.protobuf import PbWT_pb2

from pbose.PbWS import PbWS

import bitstring

class PbWT(PbWS):

  @classmethod
  def with_claims(cls, iss='', sub='', aud='', exp="1970-01-01T00:00:00Z", nbf="1970-01-01T00:00:00Z", iat="1970-01-01T00:00:00Z", pti='', public_claims=b'', private_claims=b''):
    # PbWT Claims
    pbwt_claims_pb = PbWT_pb2.PbWTClaims()
    pbwt_claims_pb.iss = iss
    pbwt_claims_pb.sub = sub
    pbwt_claims_pb.aud = aud
    pbwt_claims_pb.exp.FromJsonString(exp)
    pbwt_claims_pb.nbf.FromJsonString(nbf)
    pbwt_claims_pb.iat.FromJsonString(iat)
    pbwt_claims_pb.pti = pti
    pbwt_claims_pb.public_claims = public_claims
    pbwt_claims_pb.private_claims = private_claims
    log.debug(pbwt_claims_pb)
    # bytes
    pbwt_claims_bytes = pbwt_claims_pb.SerializeToString()
    log.debug(pbwt_claims_bytes)
    # PbWT obj
    pbwt_obj = cls.with_fields(payload=pbwt_claims_bytes)
    return pbwt_obj

  @property
  def claims(self):
    claims_pb = PbWT_pb2.PbWTClaims()
    claims_pb.ParseFromString(self.payload)
    return claims_pb

  @property
  def public_claims(self):
    return self.claims.public_claims

  @property
  def private_claims(self):
    return self.claims.private_claims
