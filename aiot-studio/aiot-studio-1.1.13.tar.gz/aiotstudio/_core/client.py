from __future__ import absolute_import
import os
import ast
import base64
from requests.auth import HTTPBasicAuth
import requests

from aiotstudio._core.errors import *
from aiotstudio import __version__
from aiotstudio._core.config import AIOTConfigParser

CONFIGURATION_SECTION = "DEFAULT"

class AuthenticatedClient(object):
    OAUTH_TOKEN_PATH = "/oauth/token?grant_type=client_credentials&scope=ALL"
    DEFAULT_HEADERS = {
        "Content-Type": "application/json",
        "X-MNUBO-SDK": "python/aiotstudio-" + __version__
    }
    DEFAULT_TIMEOUT_SECONDS = 6 * 60

    def __init__(self, client_id, client_secret, api_url):
        self._client_id = client_id
        self._client_secret = client_secret
        self._session = requests.Session()
        self._api_url = api_url
        self._session.headers.update(self.DEFAULT_HEADERS)
        self._token = self.get_token()

        if self._token is None or "access_token" not in self._token:
            raise UnauthorizedError("AuthenticatedClient requires valid 'client_id' and 'client_secret' credentials for the given API URL.")

        self._session.headers.update({"Authorization": "Bearer " + self._token['access_token']})

    def get_token(self):
        if not self._client_id or not self._client_secret:
            return None

        r = self._session.post(self._api_url + self.OAUTH_TOKEN_PATH, auth=HTTPBasicAuth(self._client_id, self._client_secret))
        r.raise_for_status()
        return r.json()

    def get(self, path, params={}):
        return self._session.get(self._api_url+path, params=params, timeout=self.DEFAULT_TIMEOUT_SECONDS)

    def post(self, path, json_body, params={}):
        return self._session.post(self._api_url + path, json=json_body, params=params, timeout=self.DEFAULT_TIMEOUT_SECONDS)


def get_default_client():
    # type: () -> Client

    # special case: we might be building the documentation and trying to evaluate "_client" although not necessary
    if "_" in os.environ and "sphinx" in os.environ["_"]:
        return None

    if all(k in os.environ for k in ("MNUBO_CLIENT_ID", "MNUBO_CLIENT_SECRET", "MNUBO_API_URL")):
        return AuthenticatedClient(
            os.environ["MNUBO_CLIENT_ID"],
            os.environ["MNUBO_CLIENT_SECRET"],
            os.environ["MNUBO_API_URL"]
        )

    config_file = os.environ.get("MNUBO_CONFIG_FILE", "application.conf")
    global_file = os.path.join(os.path.expanduser("~"), ".settings", "mnubo", "application.conf")
    config = AIOTConfigParser()

    config.read([global_file, config_file])
    if all(config.has_option(CONFIGURATION_SECTION, k) for k in ("mnubo_client_id", "mnubo_client_secret", "mnubo_api_url")):
        return AuthenticatedClient(
            config.getQuotedConfig(CONFIGURATION_SECTION, "mnubo_client_id"),
            config.getQuotedConfig(CONFIGURATION_SECTION, "mnubo_client_secret"),
            config.getQuotedConfig(CONFIGURATION_SECTION, "mnubo_api_url")
        )
    else:
        raise ConfigurationError(
            "Could not find the necessary information to connect."
            "Please enter your client id, client secret and api endpoint in a configuration file (%s or ~/.settings/mnubo/application.conf) or"
            "in MNUBO_CLIENT_ID, MNUBO_CLIENT_SECRET MNUBO_API_URL environment variables." % config_file
        )
