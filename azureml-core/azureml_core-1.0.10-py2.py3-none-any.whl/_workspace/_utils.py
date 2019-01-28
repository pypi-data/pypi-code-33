# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import random
import string
import time
import requests
import colorama
import sys

from azureml._base_sdk_common.user_agent import get_user_agent
from azureml._base_sdk_common import _ClientSessionId
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azureml._base_sdk_common.common import fetch_tenantid_from_aad_token

from azureml.exceptions import ProjectSystemException, UserErrorException

from .arm_template_builder import (
    ArmTemplateBuilder,
    build_storage_account_resource,
    build_acr_resource,
    build_keyvault_account_resource,
    build_application_insights_resource,
    build_workspace_resource
)


def arm_deploy_template_new_resources(auth, resource_group_name,
                                      location, subscription_id,
                                      workspace_name,
                                      deployment_name=None,
                                      storage=None,
                                      keyVault=None,
                                      appInsights=None,
                                      containerRegistry=None):
    """
    Deploys ARM template to create a team account with along with all the underlying dependencies.
    :param auth: auth object.
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param str resource_group_name: The name of resource group
    :param str location: The name of location
    :param subscription_id:
    :type subscription_id: str
    :param str workspace_name:
    :param str deployment_name: The name of the deployment
    """
    from azure.mgmt.resource.resources.models import DeploymentProperties

    master_template = ArmTemplateBuilder()
    workspace_dependencies = []
    vault_name = ''
    storage_name = ''
    acr_name = ''
    insights_name = ''
    if keyVault is None:
        # Vault name must only contain alphanumeric characters and dashes and cannot start with a number.
        # Vault name must be between 3-24 alphanumeric characters.
        # The name must begin with a letter, end with a letter or digit, and not contain consecutive hyphens.
        vault_name = get_name_for_dependent_resource(workspace_name, 'keyvault')
        token = auth._get_arm_token()
        tenantId = fetch_tenantid_from_aad_token(token)
        master_template.add_resource(build_keyvault_account_resource(vault_name, location, tenantId))
        workspace_dependencies.append("[resourceId('{}/{}', '{}')]".format('Microsoft.KeyVault', 'vaults', vault_name))
        keyVault = get_arm_resourceId(subscription_id, resource_group_name, 'Microsoft.KeyVault/vaults', vault_name)
    if storage is None:
        storage_name = get_name_for_dependent_resource(workspace_name, 'storage')

        master_template.add_resource(build_storage_account_resource(storage_name, location))
        workspace_dependencies.append(
            "[resourceId('{}/{}', '{}')]".format('Microsoft.Storage', 'storageAccounts', storage_name))
        storage = get_arm_resourceId(
            subscription_id,
            resource_group_name,
            'Microsoft.Storage/storageAccounts',
            storage_name)

    if containerRegistry is None:
        # ACR Resource names may contain alpha numeric characters only and must be between 5 and 50 characters
        acr_name = get_name_for_dependent_resource(workspace_name, 'acr')

        master_template.add_resource(build_acr_resource(acr_name, location))
        workspace_dependencies.append(
            "[resourceId('{}/{}', '{}')]".format('Microsoft.ContainerRegistry', 'registries', acr_name))
        containerRegistry = get_arm_resourceId(
            subscription_id,
            resource_group_name,
            'Microsoft.ContainerRegistry/registries',
            acr_name)

    if appInsights is None:
        # Application name only allows alphanumeric characters, periods, underscores,
        # hyphens and parenthesis and cannot end in a period
        insights_name = get_name_for_dependent_resource(workspace_name, 'insights')

        # App insights is not in all locations as us. So, create a map
        # update according to https://azure.microsoft.com/en-us/global-infrastructure/services/?products=monitor
        insights_location_dict = {}
        insights_location_dict["eastus2euap"] = "eastus"
        insights_location_dict["eastus"] = "eastus"
        insights_location_dict["centraluseuap"] = "eastus"
        insights_location_dict["australiaeast"] = "southeastasia"
        insights_location_dict["eastus2"] = "eastus"
        insights_location_dict["westus2"] = "westus2"
        insights_location_dict["westcentralus"] = "westus2"
        insights_location_dict["southeastasia"] = "southeastasia"
        insights_location_dict["westeurope"] = "westeurope"
        insights_location_dict["southcentralus"] = "southcentralus"

        normalized_location = location.lower().replace(" ", "")
        if normalized_location in insights_location_dict:
            insights_location = insights_location_dict[normalized_location]
        else:
            # Fallback to eastus in case the region does not exist in dict
            insights_location = 'eastus'
        master_template.add_resource(build_application_insights_resource(insights_name, insights_location))
        workspace_dependencies.append(
            "[resourceId('{}/{}', '{}')]".format('microsoft.insights', 'components', insights_name))
        appInsights = get_arm_resourceId(
            subscription_id,
            resource_group_name,
            'microsoft.insights/components',
            insights_name)

    workspace_resource = build_workspace_resource(
        workspace_name,
        location,
        keyVault,
        containerRegistry,
        storage,
        appInsights)
    workspace_resource['dependsOn'] = workspace_dependencies
    master_template.add_resource(workspace_resource)

    template = master_template.build()
    properties = DeploymentProperties(template=template, parameters={}, mode='incremental')

    lro_poller = _arm_deploy_template(auth._get_service_client(
        ResourceManagementClient, subscription_id).deployments,
        resource_group_name,
        deployment_name,
        properties)

    # The progress poller only works and is needed if sys.stdout is attached to a terminal, as we send
    # ANSI escape characters for the poller. az CLI also has similar poller progress mechanism.
    if sys.stdout.isatty():
        print_progress_output(lro_poller)
    else:
        # We just wait without any progress, as output is not shown on the terminal in this case.
        # Mainly used when this process is called using the subprocess module.
        lro_poller.wait()

    return vault_name, storage_name, acr_name, insights_name


def print_progress_output(lro_poller):
    """
    Prints the progress output on the terminal and removes that output once the workspace creation
    completes.
    :param lro_poller:
    :type lro_poller: msrest.polling.poller.LROPoller
    :return:
    """
    try:
        # az CLI also prints the progress bar using this procedure.
        # For windows to understand ANSI escaping chars.
        colorama.init()
        sys.stdout.flush()
        count = 0
        while not lro_poller.done():
            count = count + 1
            status = "Workspace creation in progress" + "." * count
            # Writes the status and moves the cursor to the beginning of the line.
            sys.stdout.write(status + "\r")
            sys.stdout.flush()
            time.sleep(3)

            # This is the standard ANSI escape sequence that clears the last status line from stdout.
            # Basically, this clears the current line from current position to the end of line
            sys.stdout.write("\033[K")
            sys.stdout.flush()
    finally:
        # Resetting windows mapping of ANSI escaping chars
        colorama.deinit()


def get_name_for_dependent_resource(workspace_name, resource_type):
    alphabets_str = ""
    for char in workspace_name.lower():
        if char.isalpha() or char.isdigit():
            alphabets_str = alphabets_str + char
    rand_str = ''.join(random.choice(string.ascii_lowercase) for i in range(8))
    resource_name = alphabets_str[:8] + resource_type[:8] + rand_str

    return resource_name[:24]


def delete_storage(auth, resource_group_name, storage_name, subscription_id):
    """Deletes storage account"""
    client = auth._get_service_client(StorageManagementClient, subscription_id)
    return client.storage_accounts.delete(resource_group_name, storage_name)


def delete_insights(auth, resource_group_name, insights_name, subscription_id):
    """Deletes application insights"""
    rg_scope = "subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}".format(
        subscriptionId=subscription_id, resourceGroupName=resource_group_name)
    app_insights_id = rg_scope + "/providers/microsoft.Insights/components/{name}".format(
        name=insights_name)
    host = auth._get_cloud_type().endpoints.resource_manager
    header = auth.get_authentication_header()
    url = host + app_insights_id + "?api-version=2015-05-01"
    requests.delete(url, headers=header)


def delete_keyvault(auth, resource_group_name, vault_name, subscription_id):
    """Deletes key vault"""
    client = auth._get_service_client(KeyVaultManagementClient, subscription_id)
    return client.vaults.delete(resource_group_name, vault_name)


def delete_acr(auth, resource_group_name, acr_name, subscription_id):
    """Deletes acr account"""
    client = auth._get_service_client(ContainerRegistryManagementClient, subscription_id)
    return client.registries.delete(resource_group_name, acr_name)


def delete_acr_armId(auth, acr_armid, throw_exception=False):
    """Deletes acr account"""
    try:
        _check_valid_arm_id(acr_armid)
        subcription_id, resource_group, resource_name \
            = _get_subscription_id_resource_group_resource_name_from_arm_id(acr_armid)
        return delete_acr(auth, resource_group, resource_name, subcription_id)
    except Exception:
        if throw_exception:
            raise


def get_acr(auth, subscription_id, resource_group_name, acr_name):
    client = auth._get_service_client(ContainerRegistryManagementClient, subscription_id)
    return client.registries.get(resource_group_name, acr_name)


def delete_kv_armId(auth, kv_armid, throw_exception=False):
    """Deletes kv account"""
    try:
        _check_valid_arm_id(kv_armid)
        subcription_id, resource_group, resource_name \
            = _get_subscription_id_resource_group_resource_name_from_arm_id(kv_armid)
        return delete_keyvault(auth, resource_group, resource_name, subcription_id)
    except Exception:
        if throw_exception:
            raise


def get_keyvault(auth, subscription_id, resource_group_name, keyvault_name):
    client = auth._get_service_client(KeyVaultManagementClient, subscription_id)
    return client.vaults.get(resource_group_name, keyvault_name)


def delete_insights_armId(auth, insights_armid, throw_exception=False):
    """Deletes insights account"""
    try:
        _check_valid_arm_id(insights_armid)
        subcription_id, resource_group, resource_name \
            = _get_subscription_id_resource_group_resource_name_from_arm_id(insights_armid)
        return delete_insights(auth, resource_group, resource_name, subcription_id)
    except Exception:
        if throw_exception:
            raise


def get_insights(auth, subscription_id, resource_group_name, insights_name):
    """Deletes application insights"""
    rg_scope = "subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}".format(
        subscriptionId=subscription_id, resourceGroupName=resource_group_name)
    app_insights_id = rg_scope + "/providers/microsoft.Insights/components/{name}".format(
        name=insights_name)
    host = auth._get_cloud_type().endpoints.resource_manager
    header = auth.get_authentication_header()
    url = host + app_insights_id + "?api-version=2015-05-01"
    return requests.get(url, headers=header)


def delete_storage_armId(auth, storage_armid, throw_exception=False):
    """Deletes storage account"""
    try:
        _check_valid_arm_id(storage_armid)
        subcription_id, resource_group, resource_name \
            = _get_subscription_id_resource_group_resource_name_from_arm_id(storage_armid)
        return delete_storage(auth, resource_group, resource_name, subcription_id)
    except Exception:
        if throw_exception:
            raise


def _get_subscription_id_resource_group_resource_name_from_arm_id(arm_id):
    parts = arm_id.split('/')
    sub_id = parts[2]
    rg_name = parts[4]
    resource_name = parts[-1]
    return sub_id, rg_name, resource_name


def get_storage_account(auth, subscription_id, resource_group_name, storage_name):
    """Get storage account"""
    client = auth._get_service_client(StorageManagementClient, subscription_id)
    return client.storage_accounts.get_properties(resource_group_name, storage_name)


def _check_valid_arm_id(resource_arm_id):
    parts = resource_arm_id.split('/')
    if len(parts) != 9:
        raise UserErrorException("Wrong format of the given arm id={}".format(resource_arm_id))


def get_arm_resourceId(subscription_id,
                       resource_group_name,
                       provider,
                       resource_name):

    return '/subscriptions/{}/resourceGroups/{}/providers/{}/{}'.format(
        subscription_id,
        resource_group_name,
        provider,
        resource_name)


def create_storage_account(auth, resource_group_name, workspace_name,
                           location, subscription_id):
    """
    Creates a storage account.
    :param auth: auth object.
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param resource_group_name:
    :param workspace_name:
    :param location:
    :param subscription_id:
    :return: Returns storage account id.
    :rtype: str
    """
    if 'eastus2euap' == location.replace(' ', '').lower():
        location = 'eastus2'
    body = {'location': location,
            'sku': {'name': 'Standard_LRS'},
            'kind': 'Storage',
            'properties':
                {"encryption":
                    {"keySource": "Microsoft.Storage",
                     "services": {
                         "blob": {
                             "enabled": 'true'
                         }
                     }
                     },
                 "supportsHttpsTrafficOnly": True
                 }
            }
    rg_scope = "subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}".format(
        subscriptionId=subscription_id, resourceGroupName=resource_group_name)

    storage_account_id = rg_scope + "/providers/microsoft.Storage/storageAccounts/{workspaceName}".format(
        workspaceName=workspace_name)
    host = auth._get_cloud_type().endpoints.resource_manager
    header = auth.get_authentication_header()
    url = host + storage_account_id + "?api-version=2016-12-01"

    response = requests.put(url, headers=header, json=body)
    if response.status_code not in [200, 201, 202]:
        # This could mean name conflict or max quota or something else, print the error message
        raise ProjectSystemException("Failed to create the storage account "
                                     "resource_group_name={}, workspace_name={}, "
                                     "subscription_id={}.\n Response={}".format(resource_group_name, workspace_name,
                                                                                subscription_id, response.text))

    return storage_account_id


def get_storage_key(auth, storage_account_id, storage_api_version):
    """

    :param auth:
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param storage_account_id:
    :param storage_api_version:
    :return:
    """
    host = auth._get_cloud_type().endpoints.resource_manager
    header = auth.get_authentication_header()
    url = host + storage_account_id + "/listkeys?api-version=" + storage_api_version
    polling_interval = 3 * 60  # 3 minutes
    start_time = time.time()
    response = None
    while True and (time.time() - start_time < polling_interval):
        time.sleep(0.5)
        response = requests.post(url, headers=header)
        if response.status_code in [200]:
            break
    if storage_api_version == '2016-12-01':
        keys = response.json()
        access_key = keys['keys'][0]['value']
    else:
        keys = response.json()
        access_key = keys['primaryKey']
    return access_key


def _arm_deploy_template(deployments_client,
                         resource_group_name,
                         deployment_name,
                         properties):
    """
    Deploys ARM template to create a container registry.
    :param obj deployments_client: ARM deployments service client
    :param str resource_group_name: The name of resource group
    :param str deployment_name: The name of the deployment
    :param DeploymentProperties properties: The properties of a deployment
    """
    if deployment_name is None:
        import random
        deployment_name = '{0}_{1}'.format('Microsoft.MachineLearningServices', random.randint(100, 999))

    headers = {
        "User-Agent": get_user_agent(),
        "x-ms-client-session-id": _ClientSessionId
    }
    # set the polling frequency to 2 secs so that AzurePoller polls
    # for status of our operation every two seconds rather than the default of 30 secs
    operation_config = {}
    operation_config['long_running_operation_timeout'] = 2
    return deployments_client.create_or_update(resource_group_name, deployment_name, properties,
                                               custom_headers=headers, operation_config=operation_config)


def get_arm_resource_id(resource_group_name, provider, resource_name, subscription_id):

    return '/subscriptions/{}/resourceGroups/{}/providers/{}/{}'.format(
        subscription_id, resource_group_name, provider, resource_name)


def get_location_from_resource_group(auth, resource_group_name, subscription_id):
    """

    :param auth:
    :param resource_group_name:
    :param subscription_id:
    :type subscription_id: str
    :return:
    """
    group = auth._get_service_client(ResourceManagementClient,
                                     subscription_id).resource_groups.get(resource_group_name)
    return group.location
