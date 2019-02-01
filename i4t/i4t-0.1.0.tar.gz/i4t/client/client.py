## @file client.py
# @brief I4T Client
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

from i4t import I4TException

from i4t.core.instancing import InstancingToken, InstancingWarrant
from i4t.core.provisioning import ProvisioningToken, ProvisioningWarrant

import paho.mqtt.client as mqtt

class Client(object):

  def on_init(self):
    pass

  def register_applets(self):
    pass

  ##############################################################################
  # public
  ##############################################################################

  def __init__(self, iwarrant):
    self._ptokens = {}
    self._applets = {}
    self._applets_registered = {}
    self._user = {}
    self.iwarrant = iwarrant
    self.on_init()
    self.register_applets()

  def user(self, var, val=None):
    if val is None:
      # get user var
      return self._user[var]
    else:
      # set user var
      self._user[var] = val
      return val

  def applet(self, applet_name, applet_cls=None):
    # register an applet
    if applet_cls is not None:
      self._applets.pop(applet_name, None)
      # TODO properly close the applet
      self._applets_registered[applet_name] = applet_cls
    # get the applet instance
    else:
      if applet_name in self._applets:
        return self._applets[applet_name]
      elif applet_name in self._applets_registered:
        if applet_name in self._ptokens:
          applet_cls = self._applets_registered[applet_name]
          self._applets[applet_name] = applet_cls(self, self._ptokens[applet_name])
          return self._applets[applet_name]
        else:
          raise I4TException("Applet: {} has not been provisioned. Check ProvisioningWarrant.".format(applet_name))
      else:
        raise I4TException("Applet: {} has not been registered. Pass applet_cls=Applet".format(applet_name))

  def provision(self, pwarrant=None):
    if pwarrant is None:
      # TODO: fetch from provisioning server
      pass
    else:
      # set as the provisioning warrant
      self.pwarrant = pwarrant
    return self

  @property
  def iwarrant(self):
    return self._iwarrant

  @iwarrant.setter
  def iwarrant(self, iwarrant):
    self._iwarrant = InstancingWarrant(iwarrant)

  @property
  def pwarrant(self):
    return self._pwarrant

  @pwarrant.setter
  def pwarrant(self, pwarrant):
    self._ptokens = {}
    # TODO properly close each applet
    self._applets = {}
    self._pwarrant = ProvisioningWarrant(pwarrant)
    for token in self._pwarrant.tokens:
      self._ptokens[token.application_name] = token

  ##############################################################################
  # private
  ##############################################################################
