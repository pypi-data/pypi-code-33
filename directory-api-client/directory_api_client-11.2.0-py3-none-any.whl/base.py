from directory_client_core.base import AbstractAPIClient
from directory_client_core.helpers import fallback

from django.core.cache import caches


class CachedAbstractAPIClient(AbstractAPIClient):

    @fallback(cache=caches['api_fallback'])
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)
