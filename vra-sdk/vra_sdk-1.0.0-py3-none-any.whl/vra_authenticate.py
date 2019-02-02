# -*- coding: utf-8 -*-
import urllib3
import json
import requests
from vra_sdk.vra_config import VraConfig
from vra_sdk.vra_exceptions import VraSdkConfigException, VraSdkRequestException, VraSdkAuthenticateException


class VraAuthenticate():
    """Provide authentication mechanism against vRa and context switching support

    Attributes:
        config (VraConfig): VraConfig object
        login (string): User login
        requestedFor (string): User login + domain
        token (string): vRa token
        domain (string): User ad domain
        environment (string): requested vRa environment
        tenant (string): vRa tenant
    """

    def __init__(self, environment, **kwargs):
        """Init VraAuthenticate
        
        Args:
            environment (string): requested vRa server environment

        Returns:
            VraAuthenticate: self
        """

        urllib3.disable_warnings()
        self.config = VraConfig()
        self.login = None
        self.requestedFor = None
        self.token = None
        self.domain = None
        self.environment = environment

    @property
    def environment(self):
        return self._environment

    @environment.setter
    def environment(self, value):
        """environment property setter

        Will update tenant and vcac_server accordingly
        
        Args:
            value (string): environment as describe in your configuration file
        """

        self.config.vcac_server = self.config.config_file['vcac_servers'][value]
        self.tenant = self.config.config_file['tenant'][value]
        self._environment = value

    def auth_login_password(self, login, password, domain):
        """Managem login/password authentication
        Will update self.token accordingly
        
        Args:
            login (string): vRa login
            password (string): vRa password
            domain (string): AD domain
        
        Raises:
            VraSdkConfigException: Domain requested not declared in configuration file
        
        Returns:
            VraAuthenticate: self
        """

        if domain not in self.config.config_file['domain']:
            raise VraSdkConfigException(f"Domain error. Domain value can be: {str(self.config.config_file['domain'])}")

        self.login = login
        self.domain = domain
        self.requestedFor = self.login + "@" + self.domain
        self.token = self.get_token(login, password)
        self.config.session.headers.update(
            {'content-type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Bearer ' + self.token})

        return self

    def auth_login_token(self, login, token, domain):
        """Manage login/token authentication
        Will update self.token accordingly
        
        Args:
            login (string): vRa login
            token (string): vRa token
            domain (string): AD Domain
        
        Raises:
            VraSdkConfigException: Domain requested not declared in configuration file
        
        Returns:
            VraAuthenticate: self
        """


        if domain not in self.config.config_file['domain']:
            raise VraSdkConfigException(f"Domain error. Domain value can be: {str(self.config.config_file['domain'])}")

        self.login = login
        self.domain = domain
        self.requestedFor = self.login + "@" + self.domain
        self.token = token
        self.config.session.headers.update(
            {'content-type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Bearer ' + self.token})
        return self

    def get_token(self, login, password):
        """Get authentication token against vRa infrastructure
        
        Args:
            login (string): vRa login
            password (string): vRa password
        
        Raises:
            VraSdkRequestException: Raised if any Requests error
            VraSdkAuthenticateException: Raised for unmanged error. Mostly for raise_for_status 4xx or 5xx errors
        
        Returns:
            string: vRa token
        """

        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json'}
        payload = {'username': login,
                   'password': password, 'tenant': self.tenant}
        try:
            req = self.config.session.post(f"https://{self.config.vcac_server}/identity/api/tokens",
                                           data=json.dumps(payload),
                                           verify=self.config.verify, headers=headers, timeout=self.config.timeout)
            req.raise_for_status()
            return json.loads(req.text)['id']
        except requests.exceptions.RequestException as e:
            raise VraSdkRequestException(f"Error during request to get vRa token: {e}")
        except Exception as e:
            raise VraSdkAuthenticateException(f"Unmanaged error during token retrieving: {e}")
