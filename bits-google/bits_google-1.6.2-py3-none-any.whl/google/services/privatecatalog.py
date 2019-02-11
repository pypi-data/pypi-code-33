"""Private Catalog API class file."""

from bits.google.services.base import Base
from googleapiclient.discovery import build
from google.auth.transport.requests import AuthorizedSession


class PrivateCatalog(Base):
    """PrivateCatalog class."""

    def __init__(self, credentials, api_key):
        """Initialize a class instance."""
        self.api_key = api_key
        self.credentials = credentials
        self.requests = AuthorizedSession(self.credentials)

        self.base_url = 'https://private-catalog.googleapis.com/v1alpha1'

        self.discovery_url = 'https://private-catalog.googleapis.com/$discovery/rest?version=v1alpha1'
        # self.privatecatalog = build(
        #     'private-catalog',
        #     'v1alpha1',
        #     credentials=credentials,
        #     discoveryServiceUrl=self.discovery_url,
        #     developerKey=self.api_key
        # )

    def get_catalogs(self):
        """Return a list of catalogs."""
        url = '%s/catalogs' % (self.base_url)
        print('URL: %s' % (url))
        response = self.requests.get(url)
        print(response)
