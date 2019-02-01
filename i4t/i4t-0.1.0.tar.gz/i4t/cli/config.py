## @file config.py
# @brief I4T Config
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

from i4t.core.instancing import InstancingToken, InstancingWarrant
from i4t.core.provisioning import ProvisioningToken, ProvisioningWarrant

import yaml
import time

I4T_CONFIG_DIR = os.path.expanduser("~/.i4t")
I4T_CONFIG_FILE = "{}/.config.yml".format(I4T_CONFIG_DIR)
I4T_PROJECT_CONFIG_FILENAME = ".project.config.yml"
I4T_IWARRANT_FILENAME = "iwarrant.b64"
I4T_PWARRANT_FILENAME = "pwarrant.b64"

# https://stackoverflow.com/a/600612
def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as exc:  # Python >2.5
    import errno
    if exc.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else:
      raise

class Config(object):

  def __init__(self):
    self.read_config()
    self.read_project_config()

  @classmethod
  def default_config(cls):
    return {
      'active': 'dev',
    }

  def set_active(self, active):
    self.config['active'] = active
    self._save_config()

  def get_active(self):
    return self.config['active']

  def read_config(self):
    mkdir_p(I4T_CONFIG_DIR)
    if not os.path.isfile(I4T_CONFIG_FILE):
      config = Config.default_config()
    else:
      with open(I4T_CONFIG_FILE, 'r') as f:
        try:
          config = yaml.load(f)
        except yaml.YAMLError as e:
          log.error(e)
    temp = Config.default_config()
    temp.update(config)
    self.config = temp
    self.save_config()

  def save_config(self):
    with open(I4T_CONFIG_FILE, 'w') as f:
      yaml.dump(self.config, f, default_flow_style=False)

  ##############################################################################
  # Project Config
  ##############################################################################

  @classmethod
  def default_project_config(cls):
    return {
      'mode': 'DEVELOPMENT',
    }

  def _project_config_dir(self):
    _dir = "{}/{}".format(I4T_CONFIG_DIR, self.get_active())
    mkdir_p(_dir)
    return _dir

  def _project_config_file(self):
    return "{}/{}".format(self._project_config_dir(), I4T_PROJECT_CONFIG_FILENAME)

  def read_project_config(self):
    #if not os.path.isfile(self._project_config_file()):
    config = Config.default_project_config()
    with open(self._project_config_file(), 'r+') as f:
      try:
        config = yaml.load(f)
      except yaml.YAMLError as e:
        log.error(e)
    temp = Config.default_project_config()
    temp.update(config)
    self.project_config = temp
    self.save_project_config()

  def save_project_config(self):
    with open(self._project_config_file(), 'w+') as f:
      yaml.dump(self.project_config, f, default_flow_style=False)

  ##############################################################################
  # Project Config - Application
  ##############################################################################

  def _project_config_application_dir(self, application):
    _dir = "{}/applications/{}".format(self._project_config_dir(), application)
    mkdir_p(_dir)
    return _dir

  def _project_config_application_iwarrant(self, application):
    return "{}/{}".format(self._project_config_application_dir(application), I4T_IWARRANT_FILENAME)

  def _project_config_application_pwarrant(self, application):
    return "{}/{}".format(self._project_config_application_dir(application), I4T_PWARRANT_FILENAME)

  def load_project_application(self, application):
    with open(self._project_config_application_iwarrant(application), 'w+') as f:
      iwarrant = InstancingWarrant(f.read())
    with open(self._project_config_application_pwarrant(application), 'w+') as f:
      pwarrant = ProvisioningWarrant(f.read())
    return iwarrant, pwarrant

  def save_project_application(self, application, iwarrant, pwarrant):
    with open(self._project_config_application_iwarrant(application), 'w+') as f:
      f.write(iwarrant.base64)
    with open(self._project_config_application_pwarrant(application), 'w+') as f:
      f.write(pwarrant.base64)

  ##############################################################################
  # Project Config - Client
  ##############################################################################

  def _project_config_client_dir(self, client):
    _dir = "{}/clients/{}".format(self._project_config_dir(), client)
    mkdir_p(_dir)
    return _dir

  def _project_config_client_iwarrant(self, client):
    return "{}/{}".format(self._project_config_client_dir(client), I4T_IWARRANT_FILENAME)

  def _project_config_client_pwarrant(self, client):
    return "{}/{}".format(self._project_config_client_dir(client), I4T_PWARRANT_FILENAME)

  def load_project_client(self, client):
    with open(self._project_config_client_iwarrant(client), 'w+') as f:
      iwarrant = InstancingWarrant(f.read())
    with open(self._project_config_client_pwarrant(client), 'w+') as f:
      pwarrant = ProvisioningWarrant(f.read())
    return iwarrant, pwarrant

  def save_project_client(self, client, iwarrant, pwarrant):
    with open(self._project_config_client_iwarrant(client), 'w+') as f:
      f.write(iwarrant.base64)
    with open(self._project_config_client_pwarrant(client), 'w+') as f:
      f.write(pwarrant.base64)
