from azure.mgmt.compute import ComputeManagementClient
# from azure.mgmt.resource import ResourceManagementClient
# from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.cosmosdb import CosmosDB
# from azure.mgmt.storage import StorageManagementClient
from msrestazure.azure_active_directory import ServicePrincipalCredentials


class AzureCredentialsProvider:

    def __init__(self, management_resource_group: str, subscription_id: str, application_id: str,
                 application_secret: str, tenant_id: str):
        self.management_resource_group = management_resource_group
        self.subscription_id = subscription_id
        self.application_id = application_id
        self.application_key = application_secret
        self.tenant = tenant_id
        # self.region = region

    def get_service_principal(self):
        return ServicePrincipalCredentials(client_id=self.application_id,
                                           secret=self.application_key,
                                           tenant=self.tenant)


class AzureClientsManager:

    def __init__(self, credentials_provider: AzureCredentialsProvider):
        self._credentials_provider = credentials_provider
        self._service_principal = self._credentials_provider.get_service_principal()
        # self._resource_client = None
        self._cosmos_client = None
        # self._subscription_client = None
        # self._storage_client = None
        self._compute_client = None
        # self._network_client = None

    @property
    def management_resource_group(self):
        return self._credentials_provider.management_resource_group

    # @property
    # def region(self):
    #     return self._credentials_provider.region

    # @property
    # def resource_client(self):
    #     if self._resource_client is None:
    #         self._resource_client = ResourceManagementClient(self._service_principal,
    #                                                          self._credentials_provider.subscription_id)
    #     return self._resource_client

    # @property
    # def storage_client(self):
    #     if self._storage_client is None:
    #         self._storage_client = StorageManagementClient(self._service_principal,
    #                                                        self._credentials_provider.subscription_id)
    #
    #     return self._storage_client

    # @property
    # def subscription_client(self):
    #     if self._subscription_client is None:
    #         self._subscription_client = SubscriptionClient(self._service_principal)
    #     return self._subscription_client

    @property
    def cosmos_db_client(self):
        if self._cosmos_client is None:
            self._cosmos_client = CosmosDB(self._service_principal, self._credentials_provider.subscription_id)
        return self._cosmos_client

    @property
    def compute_client(self):
        if self._compute_client is None:
            self._compute_client = ComputeManagementClient(self._service_principal,
                                                           self._credentials_provider.subscription_id)
        return self._compute_client

    # @property
    # def network_client(self):
    #     if self._network_client is None:
    #         self._network_client = NetworkManagementClient(self._service_credentials, self._subscription_id)
    #     return self._network_client

    # @property
    # def storage_client(self):
    #     if self._storage_client is None:
    #         self._storage_client = StorageManagementClient(self._service_credentials, self._subscription_id)
    #     return self._storage_client