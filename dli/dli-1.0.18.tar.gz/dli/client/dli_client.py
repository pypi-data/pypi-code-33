import requests
from requests_toolbelt.adapters import host_header_ssl

from dli.client.collection_functions import CollectionFunctions
from dli.client.context import Context
from dli.client.datafile_functions import DatafileFunctions
from dli.client.dataset_functions import DatasetFunctions
from dli.client.me_functions import MeFunctions
from dli.client.package_functions import PackageFunctions
from dli.client.search_functions import SearchFunctions

class AuthenticationFailure(Exception):
    """
    An exception wrapping an authentication failure response. If the response
    had a payload, that payload is reported as the exception message, otherwise
    a generic error message is returned.
    """
    GENERIC_ERROR_MESSAGE = (
        'API key is not valid or has expired. Please generate a new key in the Catalogue UI and try again.'
    )

    def __init__(self, response=None, message=None):
        self.response = response
        self.message = message

    def __str__(self):
        if self.response and self.response.text:
            return self.response.text
        elif self.message:
            return self.message

        return AuthenticationFailure.GENERIC_ERROR_MESSAGE


class DliClient(CollectionFunctions, PackageFunctions, DatasetFunctions, DatafileFunctions, MeFunctions, SearchFunctions):
    """
    Definition of a client. This client mixes in utility functions for
    manipulating collections, packages, datasets and datafiles.
    """
    def __init__(self, api_key, api_root, host=None):
        self.api_key = api_key
        self.api_root = api_root
        self.host = host
        self._ctx = self._init_ctx()

    def _init_ctx(self):
        auth_key = _get_auth_key(
            self.api_key,
            self.api_root,
            self.host
        )

        return Context(
            self.api_key,
            self.api_root,
            self.host,
            auth_key
        )

    @property
    def ctx(self):
        # if the session expired, then reauth
        # and create a new context
        if self._ctx.session_expired:
            self._ctx = self._init_ctx()

        return self._ctx

    def get_root_siren(self):
        return self.ctx.memoized(self.ctx.get_root_siren)


def _get_auth_key(api_key, api_root, host=None):
    key = api_key
    auth_header = "Bearer {}".format(key)
    start_session_url = "{}/start-session".format(api_root)  # TODO: Siren

    session = requests.Session()
    headers = {"Authorization": auth_header}

    # if a host has been provided, then we need to set it on the header
    # and activate the certificate check against the header itself
    # rather than the ip address
    if host:
        session.mount('https://', host_header_ssl.HostHeaderSSLAdapter())
        headers["Host"] = host

    r = session.post(start_session_url, headers=headers)
    if r.status_code == 403:
        api_key_url = api_root.replace('__api', 'dashboard/my-api-keys')
        error_message = "%s Catalog API Key URL: %s" % (AuthenticationFailure.GENERIC_ERROR_MESSAGE, api_key_url)
        raise AuthenticationFailure(message=error_message)
    elif r.status_code != 200:
        raise AuthenticationFailure(response=r)
    
    return r.text
