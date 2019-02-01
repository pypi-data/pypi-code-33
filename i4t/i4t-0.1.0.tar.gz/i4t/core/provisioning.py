## @file provisioning.py
# @brief I4T Provisioning Warrant and Token
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

from i4t.protobuf import Provisioning_pb2
from i4t.protobuf import common_pb2

from i4t.core.common import ApplicationInformation
from i4t.core.common import ConnectionInformation

from pbose import object_pb
from pbose.PbWK import PbWK
from pbose.PbWS import PbWS
from pbose.PbWT import PbWT

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec

from bitstring import BitArray
from base64 import urlsafe_b64encode

class ProvisioningToken(PbWT):

  @classmethod
  def generate_mqtt(cls, applet_name, host, port, channel):
    # TODO: load Provisioning Certificate
    certificate = ec.generate_private_key(ec.SECP384R1(), default_backend())
    # Provisioning Token Claims
    claims_pb = Provisioning_pb2.ProvisioningTokenClaims()
    claims_application_pb = common_pb2.ApplicationInformation()
    claims_application_pb.name = applet_name
    # TODO claims_pb.applet_id = applet_id
    claims_connection_pb = common_pb2.ConnectionInformation()
    claims_connection_pb.type = common_pb2.ConnectionInformationType.MQTT
    claims_connection_pb.host = host
    claims_connection_pb.port = port
    claims_connection_pb.channel = channel
    claims_application_pb.connection.CopyFrom(claims_connection_pb)
    claims_pb.application.CopyFrom(claims_application_pb)
    # TODO: claims_pb.authority.CopyFrom()
    # TODO: claims_pb.client.CopyFrom()
    log.debug("claims_pb")
    log.debug(claims_pb)
    # bytes
    claims_bytes = claims_pb.SerializeToString()
    log.debug(claims_bytes)
    # PbWT
    pbwt_obj = PbWT.with_claims(private_claims=claims_bytes)
    log.debug("PbWT")
    log.debug(pbwt_obj)
    # ProvisioningToken
    token_obj = cls(pbwt_obj)
    log.debug("ProvisioningToken")
    log.debug(token_obj)
    return token_obj

  @property
  def provisioning_claims(self):
    claims_pb = Provisioning_pb2.ProvisioningTokenClaims()
    claims_pb.ParseFromString(self.private_claims)
    return claims_pb

  @property
  def application(self):
    return ApplicationInformation(self.provisioning_claims.application)

  @property
  def application_name(self):
    return self.application.name

  @property
  def connection(self):
    return self.application.connection

class ProvisioningWarrant(object_pb):

  def _wrapped_protobuf(self):
    return Provisioning_pb2.ProvisioningWarrant()

  def add_token(self, ptoken):
    # TODO check type of ptoken
    self.protobuf.tokens.extend([ptoken.protobuf])
    # TODO this is stupid
    self._updated_protobuf()

  def add_token_generate_mqtt(self, applet_name, host, port, channel):
    self.add_token(ProvisioningToken.generate_mqtt(applet_name, host, port, channel))
    return self

  @property
  def tokens(self):
    for token in self.protobuf.tokens:
      yield ProvisioningToken(token)
