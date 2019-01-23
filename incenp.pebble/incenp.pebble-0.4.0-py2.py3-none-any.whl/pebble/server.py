# pebble - Passman client
# Copyright (C) 2018,2019 Damien Goutte-Gattat
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import requests

from incenp.pebble.util import Error

class Server:

    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        if hasattr(password, '__call__'):
            self._get_password = password
        else:
            self._get_password = lambda: password
        self._session = None

    def _do_request(self, endpoint, verb='GET', payload=None):
        if not self._session:
            self._session = requests.Session()
            self._session.auth = (self.user, self._get_password())
        url = 'https://{}/index.php/apps/passman/api/v2/{}'.format(
                self.host, endpoint)
        try:
            response = self._session.request(verb, url, json=payload, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            raise Error("Cannot connect to {}".format(self.host))
        except requests.exceptions.HTTPError:
            raise Error("HTTP error when communicating with {}".format(self.host))
        except requests.exceptions.ConnectTimeout:
            raise Error("Timeout when connecting to {}".format(self.host))
        except requests.exceptions.ReadTimeout:
            raise Error("Timeout when communicating with {}".format(self.host))

    def close(self):
        if self._session:
            self._session.close()

    def get_vaults(self):
        return self._do_request('vaults')

    def get_vault(self, guid):
        return self._do_request('vaults/{}'.format(guid))

    def find_vault(self, name):
        vaults = self.get_vaults()
        for v in vaults:
            if v['name'] == name:
                return v

        return None

    def new_cred(self, cred):
        return self._do_request('credentials', verb='POST', payload=cred)

    def update_cred(self, cred):
        endpoint = 'credentials/{}'.format(cred['guid'])
        return self._do_request(endpoint, verb='PATCH', payload=cred)

    def delete_cred(self, cred):
        endpoint = 'credentials/{}'.format(cred['guid'])
        return self._do_request(endpoint, verb='DELETE')

