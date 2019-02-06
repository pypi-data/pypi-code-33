from directory_client_core.base import AbstractAPIClient

from django.conf import settings

from directory_sso_api_client.user import UserAPIClient
from directory_sso_api_client.version import __version__


class DirectorySSOAPIClient(AbstractAPIClient):

    endpoints = {
        'ping': 'api/v1/healthcheck/ping/',
    }
    version = __version__

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = UserAPIClient(*args, **kwargs)

    def ping(self):
        return self.get(url=self.endpoints['ping'])


sso_api_client = DirectorySSOAPIClient(
    base_url=settings.DIRECTORY_SSO_API_CLIENT_BASE_URL,
    api_key=settings.DIRECTORY_SSO_API_CLIENT_API_KEY,
    sender_id=settings.DIRECTORY_SSO_API_CLIENT_SENDER_ID,
    timeout=settings.DIRECTORY_SSO_API_CLIENT_DEFAULT_TIMEOUT,
)
