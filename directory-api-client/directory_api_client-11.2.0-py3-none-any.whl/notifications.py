from directory_api_client.base import CachedAbstractAPIClient
from directory_api_client.version import __version__


class NotificationsAPIClient(CachedAbstractAPIClient):

    endpoints = {
        'anonymous-unsubscribe': '/notifications/anonymous-unsubscribe/',
    }
    version = __version__

    def anonymous_unsubscribe(self, signed_email_address):
        url = self.endpoints['anonymous-unsubscribe']
        return self.post(url, {'email': signed_email_address})
