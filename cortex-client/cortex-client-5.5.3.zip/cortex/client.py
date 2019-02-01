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

import jwt
import time
from cortex_client import DatasetsClient, AuthenticationClient, SessionClient, ExperimentClient
from cortex_client.serviceconnector import ServiceConnector
from .agent import Agent
from .skill import Skill
from .dataset import Dataset, LocalDataset
from .session import Session
from .action import Action
from .experiment import Experiment, LocalExperiment
from .exceptions import AuthenticationException, TokenExpiredException
from .builder import Builder, LocalBuilder
from .logger import getLogger
from .utils import log_message
from .env import CortexEnv

_DEFAULT_API_VERSION = 3

_msg_token_exp_no_creds = """
Your Cortex token is expired and the required credentials for auto-refresh have not been provided.  Account, username,
and password must be supplied.  Please login again to retrieve a valid token.
"""

log = getLogger(__name__)


class _Token(object):

    def __init__(self, auth_client: AuthenticationClient, token: str, account: str, username: str, password: str):
        self._auth = auth_client
        self._token = token
        self._account = account
        self._username = username
        self._password = password

        self._jwt = None
        if token:
            self._jwt = jwt.decode(self._token, verify=False)

    def login(self):
        try:
            log_message('Login with user %s/%s' % (self._account, self._username), log)
            self._token = self._auth.fetch_auth_token(self._account, self._username, self._password)
        except Exception as e:
            raise AuthenticationException(str(e))

        self._jwt = jwt.decode(self._token, verify=False)

    def is_expired(self):
        current_time = time.time()
        return not self._jwt or (self._jwt.get('exp', current_time) < current_time)

    @property
    def token(self):
        return self._token


class Client(object):

    """
    API client used to access agents, skills, and datasets.
    """

    def __init__(self, url: str, token: _Token, version: int = 3, verify_ssl_cert: bool = False):
        self._token = token
        self._url = url
        self._version = version
        self._verify_ssl_cert = verify_ssl_cert

    def agent(self, name: str) -> Agent:
        """
        Gets an agent with the specified name.
        """
        return Agent.get_agent(name, self._mk_connector())

    def skill(self, name: str) -> Skill:
        """
        Gets a skill with the specified name.
        """
        return Skill.get_skill(name, self._mk_connector())

    def dataset(self, name: str) -> Dataset:
        """
        Gets a dataset with the specified name.
        """
        ds_client = DatasetsClient(self._url, self._version, self._token.token)
        return Dataset.get_dataset(name, ds_client)

    def session(self, session_id=None, ttl=None, instance_id=None) -> Session:
        """
        Gets a session with the specified identifier.
        """
        session_client = SessionClient(self._url, self._version, self._token.token)
        if not session_id:
            return Session.start(session_client, ttl, instance_id)
        return Session(session_id, session_client)

    def action(self, name: str) -> Action:
        """
        Gets an action with the specified name.
        """
        return Action.get_action(name, self._mk_connector())

    def builder(self):
        """
        Gets a builder.
        """
        return Builder(self)

    def experiment(self, name: str):
        """
        Gets an experiment with the specified name.
        """
        exp_client = ExperimentClient(self._url, 2, self._token.token)
        return Experiment.get_experiment(name, exp_client)

    def _mk_connector(self):
        return ServiceConnector(self._url, self._version, self._token.token)


class Local:

    """
    Provides local, on-disk implementations of Cortex APIs.
    """

    def experiment(self, name: str) -> LocalExperiment:
        return LocalExperiment(name)

    def dataset(self, name: str):
        return LocalDataset(name)

    def action(self, name: str):
        raise NotImplementedError('Local actions are not implemented yet.')

    def builder(self):
        return LocalBuilder()


class Cortex(object):

    """
    Entry point to the Cortex API.
    """

    @staticmethod
    def client(api_endpoint:str=None, api_version:int=_DEFAULT_API_VERSION, verify_ssl_cert:bool=False, token:str=None, account:str=None, username:str=None, password:str=None):
        """
        Gets a client with the provided parameters. All parameters are optional and
        default to environment variable values if not specified.

        :Example:

        >>> from cortex import Cortex
        >>> cortex = Cortex.client()


        :param api_endpoint: the Cortex url
        :param api_version: the version of the API to use with this client
        :param verify_ssl_cert: a boolean to indiciate if the SSL certificate is to be validated
        :param token: an authentication token
        :param account: the Cortex account for this client to connect with
        :param username: the user name for this client
        :param password: the password for this client
        """
        env = CortexEnv()

        if not api_endpoint:
            api_endpoint = env.api_endpoint

        if not token:
            token = env.token

        if not account:
            account = env.account

        if not username:
            username = env.username

        if not password:
            password = env.password

        auth = AuthenticationClient(api_endpoint, version=2)
        t = _Token(auth, token, account, username, password)

        return Client(url=api_endpoint, version=api_version, token=t, verify_ssl_cert=verify_ssl_cert)

    @staticmethod
    def from_message(msg):
        """
        Creates a Cortex client from a message that must incluide an API endpoint and a token.

        :param msg: a message for constructing a Cortex client
        """
        return Cortex.client(api_endpoint=msg.apiEndpoint, token=msg.token)

    @staticmethod
    def local():
        return Local()
