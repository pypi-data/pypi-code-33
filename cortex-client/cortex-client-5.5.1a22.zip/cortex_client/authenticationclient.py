"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import json
from functools import lru_cache

from .client import _Client
from .utils import get_logger

log = get_logger(__name__)

class AuthenticationClient(_Client):
    """
    Client authentication.
    """

    URIs = {'authenticate': 'admin/{}/users/authenticate',
            'register':     'admin/tenants/register',
            'upgrade':      'accounts/token/upgrade',
            'refresh':      'accounts/tokens/refresh',
            'user-details': 'tenants/current-user-details'
           }

    def __init__(self, url, version, token=None):
        super().__init__(url, version, token)

    def refresh_token(self) -> str:
        uri = self.URIs['refresh']
        body = {}
        body_s = json.dumps(body)
        headers = {'Content-Type': 'application/json'}
        res = self._serviceconnector.request('POST', uri, body_s, headers)
        res.raise_for_status()
        return res.json()['jwt']

    def fetch_auth_token(self, tenant_id, username, password):
        """
        Retrieves the JWT token for a given user in a given tenant.

        :param tenant_id: the ID of the tenant/account to authenticate to
        :param username: the name of the user
        :param password: the user's password
        :return: a JWT string
        """
        uri = self.URIs['authenticate'].format(tenant_id)
        body = {'username': username,
                'password': password}
        body_s = json.dumps(body)
        headers = {'Content-Type': 'application/json'}
        res = self._serviceconnector.request('POST', uri, body_s, headers)
        res.raise_for_status()
        return res.json()['jwt']

    def register(self, tenant_info, invitation_code):
        """
        Registers a client with an invitation code.

        :param tenant_info: the tenant to register
        :param invitation_code: the invitation code for the registration requset
        """
        uri = self.URIs['register']
        body_s = json.dumps(tenant_info)
        headers = {'Content-Type': 'application/json'}
        params = {'invitationCode': invitation_code}
        res = self._serviceconnector.request('POST', uri, body_s, headers, params=params)
        res.raise_for_status()
        return res.json()

    # @lru_cache(maxsize=100)
    def fetch_current_user_details(self) -> dict:
        return self._get_json(self.URIs['user-details'])
