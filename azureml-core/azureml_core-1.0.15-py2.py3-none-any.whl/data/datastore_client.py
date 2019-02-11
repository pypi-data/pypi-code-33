# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""data store class."""
import logging
import os
import azureml.data.constants as constants

from msrest.authentication import BasicTokenAuthentication
from msrest.exceptions import HttpOperationError
from azureml._base_sdk_common.service_discovery import get_service_url
from azureml._restclient.rest_client import RestClient
from azureml._restclient.models.data_store_dto import DataStoreDto
from azureml._restclient.models.azure_storage_dto import AzureStorageDto
from azureml._restclient.models.azure_data_lake_dto import AzureDataLakeDto
from azureml._restclient.models.azure_sql_database_dto import AzureSqlDatabaseDto
from azureml._restclient.models.azure_postgre_sql_dto import AzurePostgreSqlDto
from .azure_storage_datastore import AzureBlobDatastore, AzureFileDatastore
from .azure_data_lake_datastore import AzureDataLakeDatastore
from .azure_sql_database_datastore import AzureSqlDatabaseDatastore
from .azure_postgre_sql_datastore import AzurePostgreSqlDatastore


module_logger = logging.getLogger(__name__)


class _DatastoreClient:
    """A client that provides methods to communicate with the datastore service."""

    # the auth token received from _auth.get_authentication_header is prefixed
    # with 'Bearer '. This is used to remove that prefix.
    _bearer_prefix_len = 7

    # list does not include the credential, we use this to substitute a fake account key
    # so we can create an azure storage sdk service object
    _account_key_substitute = "null"

    @staticmethod
    def get(workspace, datastore_name):
        """Get a datastore by name.

        :param workspace: The workspace.
        :type workspace: Workspace
        :param datastore_name: The name of the datastore.
        :type datastore_name: str
        :return: The corresponding datastore for that name.
        :rtype: AzureFileDatastore or AzureBlobDatastore
        """
        return _DatastoreClient._get(workspace, datastore_name)

    @staticmethod
    def register_azure_blob_container(workspace, datastore_name, container_name, account_name, sas_token=None,
                                      account_key=None, protocol=None, endpoint=None, overwrite=False,
                                      create_if_not_exists=False, skip_validation=False):
        """Register an Azure Blob Container to the datastore.

        You can choose to use SAS Token or Storage Account Key

        :param workspace: The workspace.
        :type workspace: Workspace
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
        :param create_if_not_exists: create the blob container if it does not exists, defaults to False
        :type create_if_not_exists: bool, optional
        :param skip_validation: skips validation of storage keys, defaults to False
        :type skip_validation: bool, optional
        :return: The blob datastore.
        :rtype: AzureBlobDatastore
        """
        credential_type = _DatastoreClient._get_credential_type(account_key, sas_token)
        return _DatastoreClient._register_azure_storage(
            workspace, datastore_name, constants.AZURE_BLOB, container_name, account_name, credential_type,
            sas_token or account_key, protocol, endpoint, overwrite, create_if_not_exists, skip_validation)

    @staticmethod
    def register_azure_file_share(workspace, datastore_name, file_share_name, account_name, sas_token=None,
                                  account_key=None, protocol=None, endpoint=None, overwrite=False,
                                  create_if_not_exists=False, skip_validation=False):
        """Register an Azure File Share to the datastore.

        You can choose to use SAS Token or Storage Account Key

        :param workspace: The workspace.
        :type workspace: Workspace
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
        :param endpoint: The endpoint of the blob container. If None, defaults to core.windows.net.
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
        credential_type = _DatastoreClient._get_credential_type(account_key, sas_token)
        return _DatastoreClient._register_azure_storage(
            workspace, datastore_name, constants.AZURE_FILE, file_share_name, account_name, credential_type,
            sas_token or account_key, protocol, endpoint, overwrite, create_if_not_exists, skip_validation)

    @staticmethod
    def register_azure_data_lake(workspace, datastore_name, store_name, tenant_id, client_id, client_secret,
                                 resource_url=None, authority_url=None, subscription_id=None, resource_group=None,
                                 overwrite=False):
        """Initialize a new Azure Data Lake Datastore.

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
        :param resource_url: the resource url, which determines what operations will be performed on
        the data lake store, defaults to https://datalake.azure.net/ which allows us to perform filesystem
        operations
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
        """
        return _DatastoreClient._register_azure_data_lake(
            workspace, datastore_name, store_name, tenant_id, client_id, client_secret, resource_url,
            authority_url, subscription_id, resource_group, overwrite)

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
        """
        return _DatastoreClient._register_azure_sql_database(
            workspace, datastore_name, server_name, database_name, tenant_id, client_id, client_secret,
            resource_url, authority_url, endpoint, overwrite)

    @staticmethod
    def register_azure_postgre_sql(workspace, datastore_name, server_name, database_name,
                                   user_id, user_password, port_number=None, endpoint=None,
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
        :param user_id: the User Id of the PostgreSQL server
        :type user_id: str
        :param user_password: the User Password of the PostgreSQL server
        :type user_password: str
        :param port_number: the Port Number of the PostgreSQL server
        :type port_number: str
        :param endpoint: The endpoint of the PostgreSQL server. If None, defaults to database.windows.net.
        :type endpoint: str, optional
        :param overwrite: overwrites an existing datastore. If the datastore does not exist,
        it will create one, defaults to False
        :type overwrite: bool, optional
        """
        return _DatastoreClient._register_azure_postgre_sql(
            workspace, datastore_name, server_name, database_name, user_id, user_password,
            port_number, endpoint, overwrite)

    @staticmethod
    def list(workspace):
        """List all of the datastores in the workspace. List operation does not return credentials of the datastores.

        :return: List of datastores
        :rtype: list[AzureFileDatastore] or list[AzureBlobDatastore] or list[AzureDataLakeDatastore]
        or list[AzureSqlDatabaseDatastore] or list[AzurePostgreSqlDatastore]
        """
        datastores = []
        ct = None

        while True:
            dss, ct = _DatastoreClient._list(workspace, ct, 100)
            datastores += dss

            if not ct:
                break

        return datastores

    @staticmethod
    def delete(workspace, datastore_name):
        """Delete a datastore.

        :param workspace: The workspace
        :type workspace: Workspace
        :param datastore_name: The datastore name to delete
        :type datastore_name: str
        """
        _DatastoreClient._delete(workspace, datastore_name)

    @staticmethod
    def get_default(workspace):
        """Get the default datastore for the workspace.

        :param workspace: The workspace
        :type workspace: Workspace
        :return: The default datastore for the workspace
        :rtype: AzureFileDatastore or AzureBlobDatastore
        """
        return _DatastoreClient._get_default(workspace)

    @staticmethod
    def set_default(workspace, datastore_name):
        """Set the default datastore for the workspace.

        :param workspace: The workspace
        :type workspace: Workspace
        :param datastore_name: The name of the datastore to be set as the default
        :type datastore_name: str
        """
        _DatastoreClient._set_default(workspace, datastore_name)

    @staticmethod
    def _get(ws, name, auth=None, host=None):
        module_logger.debug("Getting datastore: {}".format(name))

        client = _DatastoreClient._get_client(ws, auth, host)
        datastore = client.data_store.get(name, ws._subscription_id, ws._resource_group, ws._workspace_name)

        module_logger.debug("Received DTO from the datastore service")
        return _DatastoreClient._dto_to_datastore(ws, datastore)

    @staticmethod
    def _register_azure_storage(ws, datastore_name, storage_type, container_name, account_name,
                                credential_type, credential, protocol, endpoint, overwrite,
                                create_if_not_exists, skip_validation, auth=None, host=None):
        module_logger.debug("Registering {} datastore".format(storage_type))
        storage_dto = AzureStorageDto(account_name, container_name, endpoint, protocol, credential_type, credential)
        datastore = DataStoreDto(name=datastore_name, data_store_type=storage_type, azure_storage_section=storage_dto)
        module_logger.debug("Converted data into DTO")
        return _DatastoreClient._register(ws=ws, dto=datastore, create_if_not_exists=create_if_not_exists,
                                          skip_validation=skip_validation, overwrite=overwrite, auth=auth, host=host)

    @staticmethod
    def _register_azure_data_lake(ws, datastore_name, store_name, tenant_id, client_id, client_secret,
                                  resource_url=None, authority_url=None, subscription_id=None, resource_group=None,
                                  overwrite=False, auth=None, host=None):
        module_logger.debug("Registering {} datastore".format(constants.AZURE_DATA_LAKE))
        storage_dto = AzureDataLakeDto(store_name, authority_url=authority_url, resource_uri=resource_url,
                                       tenant_id=tenant_id, client_id=client_id, is_cert_auth=False,
                                       client_secret=client_secret, subscription_id=subscription_id,
                                       resource_group=resource_group)
        datastore = DataStoreDto(name=datastore_name, data_store_type=constants.AZURE_DATA_LAKE,
                                 azure_data_lake_section=storage_dto)
        module_logger.debug("Converted data into DTO")
        return _DatastoreClient._register(ws=ws, dto=datastore, create_if_not_exists=False,
                                          skip_validation=False, overwrite=overwrite, auth=auth, host=host)

    @staticmethod
    def _register_azure_sql_database(ws, datastore_name, server_name, database_name, tenant_id, client_id,
                                     client_secret, resource_url=None, authority_url=None, endpoint=None,
                                     overwrite=False, auth=None, host=None):
        module_logger.debug("Registering {} datastore".format(constants.AZURE_SQL_DATABASE))
        storage_dto = AzureSqlDatabaseDto(server_name=server_name, database_name=database_name,
                                          authority_url=authority_url, resource_uri=resource_url,
                                          tenant_id=tenant_id, client_id=client_id, is_cert_auth=False,
                                          client_secret=client_secret, endpoint=endpoint)
        datastore = DataStoreDto(name=datastore_name, data_store_type=constants.AZURE_SQL_DATABASE,
                                 azure_sql_database_section=storage_dto)
        module_logger.debug("Converted data into DTO")
        return _DatastoreClient._register(ws=ws, dto=datastore, create_if_not_exists=False, skip_validation=False,
                                          overwrite=overwrite, auth=auth, host=host)

    @staticmethod
    def _register_azure_postgre_sql(ws, datastore_name, server_name, database_name, user_id, user_password,
                                    port_number=None, endpoint=None,
                                    overwrite=False, auth=None, host=None):
        module_logger.debug("Registering {} datastore".format(constants.AZURE_POSTGRESQL))
        storage_dto = AzurePostgreSqlDto(server_name=server_name, database_name=database_name,
                                         user_id=user_id, user_password=user_password,
                                         port_number=port_number, endpoint=endpoint)
        datastore = DataStoreDto(name=datastore_name, data_store_type=constants.AZURE_POSTGRESQL,
                                 azure_postgre_sql_section=storage_dto)
        module_logger.debug("Converted data into DTO")
        return _DatastoreClient._register(ws=ws, dto=datastore, create_if_not_exists=False, skip_validation=False,
                                          overwrite=overwrite, auth=auth, host=host)

    @staticmethod
    def _register(ws, dto, create_if_not_exists, skip_validation, overwrite, auth, host):
        try:
            client = _DatastoreClient._get_client(ws, auth, host)
            module_logger.debug("Posting DTO to datastore service")
            client.data_store.create(ws._subscription_id, ws._resource_group, ws._workspace_name,
                                     dto, create_if_not_exists, skip_validation)
        except HttpOperationError as e:
            if e.response.status_code == 400 and overwrite:
                module_logger.info("Failed to create due to datastore already exists, updating instead")
                client = _DatastoreClient._get_client(ws, auth, host)
                client.data_store.update(dto.name, ws._subscription_id, ws._resource_group,
                                         ws._workspace_name, dto, create_if_not_exists, skip_validation)
            else:
                module_logger.error("Registering datastore failed with {} error code and error message\n{}"
                                    .format(e.response.status_code, e.response.content))
                raise e

        return _DatastoreClient._get(ws, dto.name, auth, host)

    @staticmethod
    def _list(ws, continuation_token, count, auth=None, host=None):
        def to_datastore(dto):
            # We cannot create an Azure Blob/File Service object unless either account key or sas token is present,
            # since list doesn't have credential, we create a null key so we can actually create a service object.
            # When the user try to access the blob/file, we will throw
            try:
                module_logger.debug("Trying to convert DTO to Datastore")
                if dto.azure_storage_section is not None:
                    dto.azure_storage_section.account_key = _DatastoreClient._account_key_substitute
                return _DatastoreClient._dto_to_datastore(ws, dto)
            except TypeError as e:
                module_logger.warning("Received an unsupported datastore type: {}. This might be caused by an " +
                                      "outdated SDK.".format(dto.data_store_type))

        module_logger.debug("Listing datastores with continuation token: {}".format(continuation_token or ""))
        client = _DatastoreClient._get_client(ws, auth, host)
        datastore_dtos = client.data_store.list(ws._subscription_id, ws._resource_group, ws._workspace_name,
                                                continuation_token=continuation_token, count=count)
        datastores = filter(lambda ds: ds is not None, map(to_datastore, datastore_dtos.value))
        return (list(datastores), datastore_dtos.continuation_token)

    @staticmethod
    def _delete(ws, name, auth=None, host=None):
        module_logger.debug("Deleting datastore: {}".format(name))
        client = _DatastoreClient._get_client(ws, auth, host)
        client.data_store.delete(name, ws._subscription_id, ws._resource_group, ws._workspace_name)

    @staticmethod
    def _get_default(ws, auth=None, host=None):
        module_logger.debug("Getting default datastore for provided workspace")
        client = _DatastoreClient._get_client(ws, auth, host)
        ds = client.data_store.get_default(ws._subscription_id, ws._resource_group, ws._workspace_name)
        return _DatastoreClient._dto_to_datastore(ws, ds)

    @staticmethod
    def _set_default(ws, name, auth=None, host=None):
        module_logger.debug("Setting default datastore for provided workspace to: {}".format(name))
        client = _DatastoreClient._get_client(ws, auth, host)
        client.data_store.set_default(name, ws._subscription_id, ws._resource_group, ws._workspace_name)

    @staticmethod
    def _get_client(ws, auth, host):
        host_env = os.environ.get('AZUREML_SERVICE_ENDPOINT')
        auth = auth or ws._auth
        host = host or host_env or get_service_url(
            auth, _DatastoreClient._get_workspace_uri_path(
                ws._subscription_id, ws._resource_group, ws._workspace_name), ws._workspace_id)

        return RestClient(credentials=_DatastoreClient._get_basic_token_auth(auth), base_url=host)

    @staticmethod
    def _get_basic_token_auth(auth):
        return BasicTokenAuthentication({
            "access_token": _DatastoreClient._get_access_token(auth)
        })

    @staticmethod
    def _get_access_token(auth):
        header = auth.get_authentication_header()
        bearer_token = header["Authorization"]

        return bearer_token[_DatastoreClient._bearer_prefix_len:]

    @staticmethod
    def _get_workspace_uri_path(subscription_id, resource_group, workspace_name):
        return ("/subscriptions/{}/resourceGroups/{}/providers"
                "/Microsoft.MachineLearningServices"
                "/workspaces/{}").format(subscription_id, resource_group, workspace_name)

    @staticmethod
    def _dto_to_datastore(ws, datastore):
        if datastore.data_store_type == constants.AZURE_BLOB:
            as_section = datastore.azure_storage_section
            return AzureBlobDatastore(
                ws, datastore.name, as_section.container_name, as_section.account_name,
                as_section.sas_token, as_section.account_key, as_section.protocol, as_section.endpoint)
        if datastore.data_store_type == constants.AZURE_FILE:
            as_section = datastore.azure_storage_section
            return AzureFileDatastore(
                ws, datastore.name, as_section.container_name, as_section.account_name,
                as_section.sas_token, as_section.account_key, as_section.protocol, as_section.endpoint)
        if datastore.data_store_type == constants.AZURE_DATA_LAKE:
            ad_section = datastore.azure_data_lake_section
            return AzureDataLakeDatastore(
                ws, datastore.name, ad_section.store_name, ad_section.tenant_id, ad_section.client_id,
                ad_section.client_secret, ad_section.resource_uri, ad_section.authority_url,
                ad_section.subscription_id, ad_section.resource_group)
        if datastore.data_store_type == constants.AZURE_SQL_DATABASE:
            ad_section = datastore.azure_sql_database_section
            return AzureSqlDatabaseDatastore(
                ws, datastore.name, ad_section.server_name, ad_section.database_name,
                ad_section.tenant_id, ad_section.client_id, ad_section.client_secret,
                ad_section.resource_uri, ad_section.authority_url)
        if datastore.data_store_type == constants.AZURE_POSTGRESQL:
            psql_section = datastore.azure_postgre_sql_section
            return AzurePostgreSqlDatastore(
                ws, datastore.name, psql_section.server_name, psql_section.database_name,
                psql_section.user_id, psql_section.user_password, psql_section.port_number)
        raise TypeError("Unsupported Datastore Type: {}".format(datastore.data_store_type))

    @staticmethod
    def _get_credential_type(account_key, sas_token):
        if account_key:
            return constants.ACCOUNT_KEY
        if sas_token:
            return constants.SAS
        return constants.NONE
