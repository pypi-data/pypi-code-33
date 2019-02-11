# Copyright (c) Microsoft Corporation. All rights reserved.
from .datasources import DataLakeDataSource
from ... import dataprep
from typing import TypeVar
import json

DEFAULT_SAS_DURATION = 30  # this aligns with our SAS generation in the UI BlobStorageManager.ts
AML_INSTALLED = True
try:
    from azureml.core import Workspace
    from azureml.core.authentication import ServicePrincipalAuthentication
    from azureml.data.abstract_datastore import AbstractDatastore
    from azureml.data.azure_storage_datastore import AbstractAzureStorageDatastore, AzureFileDatastore, \
                                                     AzureBlobDatastore
    from azureml.data.azure_data_lake_datastore import AzureDataLakeDatastore
    from azureml.data.azure_sql_database_datastore import AzureSqlDatabaseDatastore
    from azureml.data.data_reference import DataReference
    from azureml.data.datapath import DataPath
except ImportError:
    AML_INSTALLED = False


Datastore = TypeVar('Datastore', 'AbstractDatastore', 'DataReference', 'DataPath')


def datastore_to_dataflow(data_source: Datastore) -> 'dataprep.Dataflow':
    from .dataflow import Dataflow
    from .engineapi.api import get_engine_api

    datastore, datastore_value = get_datastore_value(data_source)
    if isinstance(datastore, AzureBlobDatastore) or \
            isinstance(datastore, AzureFileDatastore) or \
            isinstance(datastore, AzureDataLakeDatastore):
        df = Dataflow(get_engine_api())
        return df.add_step('Microsoft.DPrep.GetDatastoreFilesBlock', {
                               'datastore': datastore_value._to_pod()
                           })
    if isinstance(datastore, AzureSqlDatabaseDatastore):
        df = Dataflow(get_engine_api())
        return df.add_step('Microsoft.DPrep.ReadDatastoreSqlBlock', {
                               'datastore': datastore_value._to_pod()
                           })

    raise NotSupportedDatastoreTypeError(datastore)


def get_datastore_value(data_source: Datastore) -> ('AbstractDatastore', 'dataprep.api.dataflow.DatastoreValue'):
    from .dataflow import DatastoreValue
    _ensure_imported()

    datastore = None
    path_on_storage = ''

    if isinstance(data_source, AbstractDatastore):
        datastore = data_source
    elif isinstance(data_source, DataReference):
        datastore = data_source.datastore
        path_on_storage = data_source.path_on_datastore or path_on_storage
    elif isinstance(data_source, DataPath):
        datastore = data_source._datastore
        path_on_storage = data_source.path_on_datastore or path_on_storage

    _ensure_supported(datastore)
    path_on_storage = path_on_storage.lstrip('/')

    workspace = datastore.workspace
    _set_auth_type(workspace)
    return (datastore, DatastoreValue(
        subscription=workspace.subscription_id,
        resource_group=workspace.resource_group,
        workspace_name=workspace.name,
        datastore_name=datastore.name,
        path=path_on_storage
    ))


def login():
    from azureml.core.authentication import InteractiveLoginAuthentication
    auth = InteractiveLoginAuthentication()
    auth.get_authentication_header()


def _ensure_imported():
    if not AML_INSTALLED:
        raise ImportError('Unable to import Azure Machine Learning SDK. In order to use datastore, please make ' \
                          + 'sure the Azure Machine Learning SDK is installed.')


def _ensure_supported(datastore: 'AbstractDatastore'):
    if not isinstance(datastore, AzureBlobDatastore) and \
            not isinstance(datastore, AzureFileDatastore) and \
            not isinstance(datastore, AzureDataLakeDatastore) and \
            not isinstance(datastore, AzureSqlDatabaseDatastore):
        raise NotSupportedDatastoreTypeError(datastore)


def _set_auth_type(workspace: 'Workspace'):
    from .engineapi.api import get_engine_api
    from .engineapi.typedefinitions import SetAmlAuthMessageArgument, AuthType

    if isinstance(workspace._auth, ServicePrincipalAuthentication):
        auth = {
            'tenantId': workspace._auth._tenant_id,
            'username': workspace._auth._username,
            'password': workspace._auth._password
        }
        get_engine_api().set_aml_auth(SetAmlAuthMessageArgument(AuthType.SERVICEPRINCIPAL, json.dumps(auth)))
    else:
        get_engine_api().set_aml_auth(SetAmlAuthMessageArgument(AuthType.DERIVED, ''))


class NotSupportedDatastoreTypeError(Exception):
    def __init__(self, datastore: 'AbstractDatastore'):
        super().__init__('Datastore "{}"\'s type "{}" is not supported.'.format(datastore.name, datastore.datastore_type))
        self.datastore = datastore
