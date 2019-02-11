# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Azure datalake datastore class."""
import azureml.data.constants as constants

from .abstract_datastore import AbstractDatastore


class AzureDataLakeDatastore(AbstractDatastore):
    """Datastore backed by Azure data lake."""

    def __init__(self, workspace, name, store_name, tenant_id, client_id, client_secret,
                 resource_url=None, authority_url=None, subscription_id=None, resource_group=None):
        """Initialize a new Azure Data Lake Datastore.

        :param workspace: the workspace this datastore belongs to
        :type workspace: str
        :param name: the datastore name
        :type name: str
        :param store_name: the ADLS store name
        :type store_name: str
        :param tenant_id: the Directory ID/Tenant ID of the service principal
        :type tenant_id: str
        :param client_id: the Client ID/Application ID of the service principal
        :type client_id: str
        :param client_secret: the secret of the service principal
        :type client_secret: str
        :param resource_url: the resource url, which determines what operations will be performed on
        the data lake store, if None, defaults to https://datalake.azure.net/
        :type resource_url: str, optional
        :param authority_url: the authority url used to authenticate the user, if None, defaults to
        https://login.microsoftonline.com
        :type authority_url: str, optional
        :param subscription_id: the ID of the subscription the ADLS store belongs to
        :type subscription_id: str, optional
        :param resource_group: the resource group the ADLS store belongs to
        :type resource_group: str, optional
        """
        super(AzureDataLakeDatastore, self).__init__(workspace, name, constants.AZURE_DATA_LAKE)
        self.store_name = store_name
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.resource_url = resource_url
        self.authority_url = authority_url
        self.subscription_id = subscription_id
        self.resource_group = resource_group

    def _as_dict(self, hide_secret=True):
        output = super(AzureDataLakeDatastore, self)._as_dict()
        output["store_name"] = self.store_name
        output["tenant_id"] = self.tenant_id
        output["client_id"] = self.client_id
        output["resource_url"] = self.resource_url
        output["authority_url"] = self.authority_url
        output["subscription_id"] = self.subscription_id
        output["resource_group"] = self.resource_group

        if not hide_secret:
            output["client_secret"] = self.client_secret

        return output
