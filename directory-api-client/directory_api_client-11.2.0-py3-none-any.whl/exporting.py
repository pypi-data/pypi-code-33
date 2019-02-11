from directory_api_client.base import CachedAbstractAPIClient
from directory_api_client.version import __version__


class ExportingAPIClient(CachedAbstractAPIClient):

    endpoints = {
        'lookup-by-postcode': '/exporting/lookup-by-postcode/{postcode}/',
    }
    version = __version__

    def lookup_regional_office_by_postcode(self, postcode):
        url = self.endpoints['lookup-by-postcode'].format(postcode=postcode)
        return self.get(url)
