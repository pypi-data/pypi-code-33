from django.conf import settings

from directory_api_client.base import CachedAbstractAPIClient
from directory_api_client.buyer import BuyerAPIClient
from directory_api_client.company import CompanyAPIClient
from directory_api_client.enrolment import EnrolmentAPIClient
from directory_api_client.supplier import SupplierAPIClient
from directory_api_client.notifications import NotificationsAPIClient
from directory_api_client.exportopportunity import ExportOpportunityAPIClient
from directory_api_client.exportreadiness import ExportReadinessAPIClient
from directory_api_client.exporting import ExportingAPIClient

from directory_api_client.version import __version__


class DirectoryAPIClient(CachedAbstractAPIClient):

    endpoints = {
        'ping': 'healthcheck/ping/',
    }
    version = __version__

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enrolment = EnrolmentAPIClient(*args, **kwargs)
        self.company = CompanyAPIClient(*args, **kwargs)
        self.supplier = SupplierAPIClient(*args, **kwargs)
        self.buyer = BuyerAPIClient(*args, **kwargs)
        self.notifications = NotificationsAPIClient(*args, **kwargs)
        self.exportopportunity = ExportOpportunityAPIClient(*args, **kwargs)
        self.exportreadiness = ExportReadinessAPIClient(*args, **kwargs)
        self.exporting = ExportingAPIClient(*args, **kwargs)

    def ping(self):
        return self.get(url=self.endpoints['ping'])


api_client = DirectoryAPIClient(
    base_url=settings.DIRECTORY_API_CLIENT_BASE_URL,
    api_key=settings.DIRECTORY_API_CLIENT_API_KEY,
    sender_id=settings.DIRECTORY_API_CLIENT_SENDER_ID,
    timeout=settings.DIRECTORY_API_CLIENT_DEFAULT_TIMEOUT,
)
