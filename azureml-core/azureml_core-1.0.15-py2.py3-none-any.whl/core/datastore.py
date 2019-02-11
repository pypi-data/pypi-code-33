# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Datastore class.

Class for accessing Azure datastores, including Azure Blob Storage, Azure Data Lake Storage, and Azure SQL
Database Storage.
"""


class Datastore(object):
    """A class for accessing datastores.

    Provides access to datastores including Azure Blob Storage, Azure Data Lake Storage,
    and Azure SQL Database Storage.
    """

    def __new__(cls, workspace, name=None):
        """Get a datastore by name. This call will make a request to the datastore service.

        :param workspace: The workspace
        :type workspace: Workspace
        :param name: The name of the datastore, defaults to None, which gets the default datastore.
        :type name: str, optional
        :return: The corresponding datastore for that name.
        :rtype: AzureFileDatastore or AzureBlobDatastore or AzureDataLakeDataStore
        """
        if name is None:
            return Datastore._client().get_default(workspace)
        return Datastore._client().get(workspace, name)

    def __init__(self, workspace, name=None):
        """Initialize a datastore.

        :param workspace: The workspace
        :type workspace: Workspace
        :param name: The name of the datastore, defaults to None, which gets the default datastore.
        :type name: str, optional
        :return: The corresponding datastore for that name.
        :rtype: AzureFileDatastore or AzureBlobDatastore
        """
        self.workspace = workspace
        self.name = name

    def set_as_default(self):
        """Set the default datastore.

        :param datastore_name: Name of the datastore
        :type datastore_name: str
        """
        raise NotImplementedError()

    def unregister(self):
        """Unregisters the datastore, the underlying storage account and container/share will not be deleted."""
        raise NotImplementedError()

    @staticmethod
    def get(workspace, datastore_name):
        """Get a datastore by name. This is same as calling the constructor.

        :param workspace: The workspace
        :type workspace: azureml.core.workspace.Workspace
        :param datastore_name: The name of the datastore, defaults to None, which gets the default datastore.
        :type datastore_name: str, optional
        :return: The corresponding datastore for that name.
        :rtype: AzureFileDatastore or AzureBlobDatastore
        """
        return Datastore._client().get(workspace, datastore_name)

    @staticmethod
    def get_default(workspace):
        """Get the default datastore for the workspace.

        :param workspace: The workspace
        :type workspace: azureml.core.workspace.Workspace
        :return: The default datastore for the workspace
        :rtype: AzureFileDatastore or AzureBlobDatastore
        """
        return Datastore._client().get_default(workspace)

    @staticmethod
    def register_azure_blob_container(workspace, datastore_name, container_name, account_name, sas_token=None,
                                      account_key=None, protocol=None, endpoint=None, overwrite=False,
                                      create_if_not_exists=False, skip_validation=False):
        """Register an Azure Blob Container to the datastore.

        You can choose to use SAS Token or Storage Account Key

        :param workspace: The workspace
        :type workspace: azureml.core.workspace.Workspace
        :param datastore_name: The name of the datastore, case insensitive, can only contain alphanumeric characters
            and _
        :type datastore_name: str
        :param container_name: The name of the azure blob container.
        :type container_name: str
        :param account_name: The storage account name.
        :type account_name: str
        :param sas_token: An account SAS token, defaults to None.
        :type sas_token: str, optional
        :param account_key: A storage account key, defaults to None.
        :type account_key: str, optional
        :param protocol: Protocol to use to connect to the blob container. If None, defaults to https.
        :type protocol: str, optional
        :param endpoint: The endpoint of the blob container. If None, defaults to core.windows.net.
        :type endpoint: str, optional
        :param overwrite: overwrites an existing datastore. If the datastore does not exist,
            it will create one, defaults to False
        :type overwrite: bool, optional
        :param create_if_not_exists: create the file share if it does not exists, defaults to False
        :type create_if_not_exists: bool, optional
        :param skip_validation: skips validation of storage keys, defaults to False
        :type skip_validation: bool, optional
        :return: The blob datastore.
        :rtype: AzureBlobDatastore
        """
        return Datastore._client().register_azure_blob_container(workspace, datastore_name, container_name,
                                                                 account_name, sas_token, account_key, protocol,
                                                                 endpoint, overwrite, create_if_not_exists,
                                                                 skip_validation)

    @staticmethod
    def register_azure_file_share(workspace, datastore_name, file_share_name, account_name, sas_token=None,
                                  account_key=None, protocol=None, endpoint=None, overwrite=False,
                                  create_if_not_exists=False, skip_validation=False):
        """Register an Azure File Share to the datastore.

        You can choose to use SAS Token or Storage Account Key

        :param workspace: The workspace
        :type workspace: azureml.core.workspace.Workspace
        :param datastore_name: The name of the datastore, case insensitive, can only contain alphanumeric characters
            and _
        :type datastore_name: str
        :param file_share_name: The name of the azure file container.
        :type file_share_name: str
        :param account_name: The storage account name.
        :type account_name: str
        :param sas_token: An account SAS token, defaults to None.
        :type sas_token: str, optional
        :param account_key: A storage account key, defaults to None.
        :type account_key: str, optional
        :param protocol: Protocol to use to connect to the file share. If None, defaults to https.
        :type protocol: str, optional
        :param endpoint: The endpoint of the file share. If None, defaults to core.windows.net.
        :type endpoint: str, optional
        :param overwrite: overwrites an existing datastore. If the datastore does not exist,
            it will create one, defaults to False
        :type overwrite: bool, optional
        :param create_if_not_exists: create the file share if it does not exists, defaults to False
        :type create_if_not_exists: bool, optional
        :param skip_validation: skips validation of storage keys, defaults to False
        :type skip_validation: bool, optional
        :return: The file datastore.
        :rtype: AzureFileDatastore
        """
        return Datastore._client().register_azure_file_share(workspace, datastore_name, file_share_name, account_name,
                                                             sas_token, account_key, protocol, endpoint, overwrite,
                                                             create_if_not_exists, skip_validation)

    @staticmethod
    def register_azure_data_lake(workspace, datastore_name, store_name, tenant_id, client_id, client_secret,
                                 resource_url=None, authority_url=None, subscription_id=None, resource_group=None,
                                 overwrite=False):
        """Initialize a new Azure Data Lake Datastore.

        .. remarks::

            .. note::

                Azure Data Lake Datastore supports data transfer and running U-Sql jobs using AML Pipelines.
                It does not provide upload and download through the SDK.

        :param workspace: the workspace this datastore belongs to
        :type workspace: str
        :param datastore_name: the datastore name
        :type datastore_name: str
        :param store_name: the ADLS store name
        :type store_name: str
        :param tenant_id: the Directory ID/Tenant ID of the service principal
        :type tenant_id: str
        :param client_id: the Client ID/Application ID of the service principal
        :type client_id: str
        :param client_secret: the secret of the service principal
        :type client_secret: str
        :param resource_url: the resource url, which determines what operations will be performed on the data lake
            store, if None, defaults to https://datalake.azure.net/ which allows us to perform filesystem operations
        :type resource_url: str, optional
        :param authority_url: the authority url used to authenticate the user, defaults to
            https://login.microsoftonline.com
        :type authority_url: str, optional
        :param subscription_id: the ID of the subscription the ADLS store belongs to
        :type subscription_id: str, optional
        :param resource_group: the resource group the ADLS store belongs to
        :type resource_group: str, optional
        :param overwrite: overwrites an existing datastore. If the datastore does not exist,
            it will create one, defaults to False
        :type overwrite: bool, optional
        :return: Returns the data lake Datastore.
        :rtype: AzureDataLakeDatastore
        """
        return Datastore._client().register_azure_data_lake(
            workspace, datastore_name, store_name, tenant_id, client_id, client_secret,
            resource_url, authority_url, subscription_id, resource_group, overwrite)

    @staticmethod
    def register_azure_sql_database(workspace, datastore_name, server_name, database_name, tenant_id, client_id,
                                    client_secret, resource_url=None, authority_url=None, endpoint=None,
                                    overwrite=False):
        """Initialize a new Azure SQL database Datastore.

        :param workspace: the workspace this datastore belongs to
        :type workspace: str
        :param datastore_name: the datastore name
        :type datastore_name: str
        :param server_name: the SQL server name
        :type server_name: str
        :param database_name: the SQL database name
        :type database_name: str
        :param tenant_id: the Directory ID/Tenant ID of the service principal
        :type tenant_id: str
        :param client_id: the Client ID/Application ID of the service principal
        :type client_id: str
        :param client_secret: the secret of the service principal
        :type client_secret: str
        :param resource_url: the resource url, which determines what operations will be performed on
            the SQL database store, if None, defaults to https://database.windows.net/
        :type resource_url: str, optional
        :param authority_url: the authority url used to authenticate the user, defaults to
            https://login.microsoftonline.com
        :type authority_url: str, optional
        :param endpoint: The endpoint of the SQL server. If None, defaults to database.windows.net.
        :type endpoint: str, optional
        :param overwrite: overwrites an existing datastore. If the datastore does not exist,
            it will create one, defaults to False
        :type overwrite: bool, optional
        :return: Returns the SQL database Datastore.
        :rtype: AzureSqlDatabaseDatastore
        """
        return Datastore._client().register_azure_sql_database(
            workspace, datastore_name, server_name, database_name, tenant_id, client_id, client_secret,
            resource_url, authority_url, endpoint, overwrite)

    @ staticmethod
    def register_azure_postgre_sql(workspace, datastore_name, server_name, database_name, user_id, user_password,
                                   port_number=None, endpoint=None,
                                   overwrite=False):
        """Initialize a new Azure PostgreSQL Datastore.

        :param workspace: the workspace this datastore belongs to
        :type workspace: str
        :param datastore_name: the datastore name
        :type datastore_name: str
        :param server_name: the PostgreSQL server name
        :type server_name: str
        :param database_name: the PostgreSQL database name
        :type database_name: str
        :param user_id: the User ID of the PostgreSQL server
        :type user_id: str
        :param user_password: the User Password of the PostgreSQL server
        :type user_password: str
        :param port_number: the Port Number of the PostgreSQL server
        :type port_number: str
        :param endpoint: The endpoint of the PostgreSQL server. If None, defaults to postgres.database.azure.com.
        :type endpoint: str, optional
        :param overwrite: overwrites an existing datastore. If the datastore does not exist,
            it will create one, defaults to False
        :type overwrite: bool, optional
        :return: Returns the PostgreSQL database Datastore.
        :rtype: AzurePostgreSqlDatastore
        """
        return Datastore._client().register_azure_postgre_sql(
            workspace, datastore_name, server_name, database_name, user_id, user_password,
            port_number, endpoint, overwrite)

    @staticmethod
    def _client():
        """Get a client.

        :return: Returns the client
        :rtype: DatastoreClient
        """
        from azureml.data.datastore_client import _DatastoreClient
        return _DatastoreClient
