# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re

from azureml._base_sdk_common.common import resource_client_factory, check_valid_resource_name, resource_error_handling

from azureml._base_sdk_common.workspace import AzureMachineLearningWorkspaces
from azureml.exceptions import ProjectSystemException, WorkspaceException

from azureml._base_sdk_common.workspace.models import (
    WorkspaceUpdateParameters,
    ErrorResponseWrapperException
)
from azureml._base_sdk_common.workspace.operations import WorkspacesOperations
from ._utils import (
    get_location_from_resource_group,
    arm_deploy_template_new_resources,
    get_arm_resourceId,
    delete_storage_armId,
    delete_insights_armId,
    delete_acr_armId,
    delete_kv_armId
)


def ml_workspace_create_resources(auth, client, resource_group_name, workspace_name,
                                  location, subscription_id, friendly_name=None,
                                  storage_account=None, key_vault=None, app_insights=None,
                                  containerRegistry=None, exist_ok=False):
    """
    Create a new machine learning workspace along with dependent resources.
    :param auth:
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param client:
    :param resource_group_name:
    :param workspace_name:
    :param location:
    :param subscription_id: Subscription id to use.
    :param friendly_name:
    :return:
    """
    check_valid_resource_name(workspace_name, "Workspace")
    # First check if the workspace already exists
    try:
        existing_workspace = client.get(resource_group_name, workspace_name)
        if exist_ok:
            return existing_workspace
        else:
            from azureml._base_sdk_common.common import get_http_exception_response_string
            raise WorkspaceException("Workspace with name '{0}' already exists under"
                                     " resource group with name '{1}'.".format(workspace_name,
                                                                               resource_group_name))
    except ErrorResponseWrapperException as response_exception:
        if response_exception.response.status_code != 404:
            from azureml._base_sdk_common.common import get_http_exception_response_string
            raise WorkspaceException(get_http_exception_response_string(response_exception.response))

    # Workspace does not exist. go ahead and create
    if location is None:
        location = get_location_from_resource_group(auth, resource_group_name, subscription_id)

    if not friendly_name:
        friendly_name = workspace_name

    try:
        # Use this way for deployment until we get our template shipped in PROD to support MSI
        '''Note: az core deploy template spawns a new daemon thread to track the status of a deployment.
        If the operation fails then az throws an exception in the daemon thread. Hence, we catch the exception here
        when trying to fetch the workspace. Workspace get will throw exception when the template deployment fail and
        we would need to roll back in such case'''
        vault_name, storage_name, acr_name, insights_name = arm_deploy_template_new_resources(
            auth,
            resource_group_name,
            location,
            subscription_id,
            workspace_name,
            storage=storage_account,
            keyVault=key_vault,
            appInsights=app_insights,
            containerRegistry=containerRegistry)
        created_workspace = client.get(resource_group_name, workspace_name)
        return created_workspace
    except Exception as e:
        # Deleting sub-resources

        # Checking for storage is None, to identify that it is not bring your own storage case.
        # Deleting using arm id functions, as they don't throw exceptions.
        if storage_account is None:
            try:
                storage_arm_id = get_arm_resourceId(
                    subscription_id, resource_group_name, 'Microsoft.Storage/storageAccounts', storage_name)
                delete_storage_armId(auth, storage_arm_id)
            except Exception:
                pass
        if app_insights is None:
            try:
                app_insights_arm_id = get_arm_resourceId(
                    subscription_id, resource_group_name, 'microsoft.insights/components', insights_name)
                delete_insights_armId(auth, app_insights_arm_id)
            except Exception:
                pass
        if containerRegistry is None:
            try:
                container_registry_arm_id = get_arm_resourceId(
                    subscription_id, resource_group_name, 'Microsoft.ContainerRegistry/registries', acr_name)
                delete_acr_armId(auth, container_registry_arm_id)
            except Exception:
                pass
        if key_vault is None:
            try:
                keyvault_arm_id = get_arm_resourceId(subscription_id, resource_group_name,
                                                     'Microsoft.KeyVault/vaults', vault_name)
                delete_kv_armId(auth, keyvault_arm_id)
            except Exception:
                pass

        # Deleting the actual workspace
        try:
            ml_workspace_delete(auth, subscription_id, resource_group_name, workspace_name)
        except Exception:
            # Catching any exception if workspace deletion fails.
            pass
        raise WorkspaceException("Unable to create the workspace. \n {}".format(e))


def list_resources_odata_filter_builder(
        resource_group_name=None, resource_provider_namespace=None, resource_type=None):
    """
    Build up OData filter string from parameters
    :param resource_group_name:
    :param resource_provider_namespace:
    :param resource_type:
    :return:
    """
    filters = []

    if resource_group_name:
        filters.append("resourceGroup eq '{}'".format(resource_group_name))

    if resource_type:
        if resource_provider_namespace:
            f = "'{}/{}'".format(resource_provider_namespace, resource_type)
        else:
            if not re.match('[^/]+/[^/]+', resource_type):
                raise ProjectSystemException('Malformed resource-type: '
                                             '--resource-type=<namespace>/<resource-type> expected.')
            # assume resource_type is <namespace>/<type>. The worst is to get a server error
            f = "'{}'".format(resource_type)
        filters.append("resourceType eq " + f)
    else:
        if resource_provider_namespace:
            raise ProjectSystemException('--namespace also requires --resource-type')

    return ' and '.join(filters)


def ml_workspace_list(auth, subscription_id, resource_group_name=None):
    """
    :param auth: auth object
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param subscription_id:
    :param resource_group_name:
    :return:
    """
    rcf = resource_client_factory(auth, subscription_id)
    odata_filter = list_resources_odata_filter_builder(
        resource_group_name=resource_group_name,
        resource_provider_namespace='Microsoft.MachineLearningServices',
        resource_type='workspaces')
    resources = rcf.resources.list(filter=odata_filter)
    return list(resources)


def ml_workspace_update(client, resource_group_name, workspace_name, tags, friendly_name,
                        description):
    """
    Update an existing Azure DocumentDB database account.
    :param client:
    :param resource_group_name:
    :param workspace_name:
    :param tags:
    :param friendly_name:
    :param description:
    :return: TODO: return type.
    """
    params = WorkspaceUpdateParameters(
        tags,
        friendly_name,
        description)

    client.update(resource_group_name, workspace_name, params)
    workspace = client.get(resource_group_name, workspace_name)
    return workspace


def ml_workspace_delete(auth, subscription_id, resource_group_name, workspace_name):
    try:
        return WorkspacesOperations.delete(
            auth._get_service_client(AzureMachineLearningWorkspaces, subscription_id).workspaces,
            resource_group_name, workspace_name)
    except ErrorResponseWrapperException as response_exception:
        resource_error_handling(response_exception, "Workspace")
