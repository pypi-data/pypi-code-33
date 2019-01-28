# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Workspace module manages the interactions with Azure Machine Learning Workspaces.

This module provides convenient methods for manipulating workspace resources and enumerating objects within.
The Azure Machine Learning Workspace serves as a container for Azure Machine Learning assets. It provides multiple
functionalities including     access control mechanisms using Azure Resource Manager role-based access control,
region affinity to all ML data saved within the Workspace,     and the primary means for billing.
"""
from random import choice
from string import ascii_lowercase
import collections
import errno
import json
import re
import os
from operator import attrgetter

from azureml._project import _commands
from azureml._file_utils.file_utils import normalize_path, normalize_path_and_join, \
    check_and_create_dir, traverse_up_path_and_find_file, normalize_file_ext

# Az CLI converts the keys to camelCase and our tests assume that behavior,
# so converting for the SDK too.
from azureml.exceptions import WorkspaceException, ProjectSystemException, UserErrorException
from azureml._base_sdk_common.common import convert_dict_keys_to_camel_case
from azureml._base_sdk_common.common import check_valid_resource_name
from azureml.core.authentication import InteractiveLoginAuthentication
from azureml.core.compute import ComputeTarget
from azureml.core.image import Image
from azureml.core.model import Model
from azureml.core.webservice import Webservice
from azureml.data.datastore_client import _DatastoreClient

_WorkspaceScopeInfo = collections.namedtuple("WorkspaceScopeInfo",
                                             "subscription_id resource_group workspace_name")

CONFIG_FILE_NAME = 'config.json'
AML_CONFIG_DIR = 'aml_config'


class Workspace(object):
    """Workspace class manages the interactions with Azure Machine Learning Workspaces.

    This class provides convenient methods for manipulating workspace resources and enumerating objects within.
    To see an example of creating a Workspace, viewing details, and writing a config file, follow the tutorial:
    https://docs.microsoft.com/en-us/azure/machine-learning/service/quickstart-create-workspace-with-python
    """

    def __init__(self, subscription_id, resource_group, workspace_name, auth=None, _location=None,
                 _disable_service_check=False):
        """Class Workspace constructor to load an existing Azure ML Workspace.

        :param subscription_id: The Azure subscription id containing the workspace.
        :type subscription_id: str
        :param resource_group: The resource group containing the workspace.
        :type resource_group: str
        :param workspace_name: The existing workspace name.
        :type workspace_name: str
        :param auth: The auth object.
            If None the default Azure CLI credentials will be used or the API will prompt for credentials.
        :type auth: azureml.core.authentication.ServicePrincipalAuthentication or
            azureml.core.authentication.InteractiveLoginAuthentication
        :param _location:
        :type _location: str
        :param _disable_service_check:
        :type _disable_service_check: bool
        """
        if not auth:
            auth = InteractiveLoginAuthentication()

        self._auth = auth
        self._subscription_id = subscription_id
        self._resource_group = resource_group
        self._workspace_name = workspace_name
        # Used to set the location in remote context.
        self._location = _location
        self._workspace_autorest_object = None

        if not _disable_service_check:
            auto_rest_workspace = _commands.get_workspace(auth, subscription_id, resource_group, workspace_name)
            self._workspace_autorest_object = auto_rest_workspace

    @staticmethod
    def from_config(path=None, auth=None):
        """Return a workspace object for an existing Azure Machine Learning Workspace.

        Reads workspace configuration from a file.

        The method provides a simple way of reusing the same workspace across multiple python notebooks or projects.
        Users can save the workspace ARM properties using the write_config function,
        and use this method to load the same workspace in different python notebooks or projects without
        retyping the workspace ARM properties.

        :param path: Path to the directory where to the save config file.
            The parameter defaults to the current directory.
        :type path: str
        :param auth: The auth object.
            If None the default Azure CLI credentials will be used or the API will prompt for credentials.
        :type auth: azureml.core.authentication.ServicePrincipalAuthentication or
            azureml.core.authentication.InteractiveLoginAuthentication
        :return: The workspace object for an existing Azure ML Workspace
        :rtype: azureml.core.workspace.Workspace
        """
        if path is not None:
            normalized_path = normalize_path(path)
            # We assume that path points to a config file
            if not os.path.isfile(normalized_path):
                raise UserErrorException('The provided path: {} does not point to a file. Please make '
                                         'sure to provide the full path to the config file, including '
                                         'the file name and extension.'.format(normalized_path))
            found_path = normalized_path

        else:
            path = '.'
            normalized_path = normalize_path(path)

            # Looking for /aml_config/config.json first as we expect the config.json file to live in aml_config
            found_path = traverse_up_path_and_find_file(path=normalized_path, file_name=CONFIG_FILE_NAME,
                                                        directory_name=AML_CONFIG_DIR)

            if not found_path:
                # Couldn't find config.json in aml_config, so trying to search for config.json not in aml_config
                found_path = traverse_up_path_and_find_file(path=normalized_path, file_name=CONFIG_FILE_NAME)

            if not found_path:
                raise UserErrorException('We could not find config.json in: {} or in its parent directories. '
                                         'Please provide the full path to the config file or ensure that '
                                         'config.json exists in the parent directories.'.format(normalized_path))

        with open(found_path, 'r') as config_file:
            config = json.load(config_file)

        # Checking the keys in the config.json file to check for required parameters.
        if not all([k in config.keys() for k in ('subscription_id', 'resource_group', 'workspace_name')]):
            raise UserErrorException('The config file found in: {} does not seem to contain the required '
                                     'parameters. Please make sure it contains your subscription_id, '
                                     'resource_group and workspace_name.'.format(found_path))

        # User provided ARM parameters take precedence over values from config.json
        subscription_id_from_config = config['subscription_id']
        resource_group_from_config = config['resource_group']
        workspace_name_from_config = config['workspace_name']

        # TODO: This method is not called by the CLI, so print is fine here until we figure out
        # the sdk logging mechanism.
        print('Found the config file in: {}'.format(found_path))
        return Workspace(subscription_id_from_config, resource_group_from_config, workspace_name_from_config,
                         auth=auth)

    @staticmethod
    def create(name, auth=None, subscription_id=None, resource_group=None,
               location=None, create_resource_group=True, friendly_name=None, storage_account=None,
               key_vault=None, app_insights=None, container_registry=None, exist_ok=False):
        """Create a new Azure Machine Learning Workspace.

        Throws an exception if the workspace already exists or any of the workspace requirement are not satisfied.

        :param name: The new workspace name.
            Workspace name has to be between 2 and 32 characters of letters and numbers.
        :type name: str
        :param auth: The auth object.
            If None the default Azure CLI credentials will be used or the API will prompt for credentials.
        :type auth: azureml.core.authentication.ServicePrincipalAuthentication or
            azureml.core.authentication.InteractiveLoginAuthentication
        :param subscription_id: The subscription id of the containing subscription for the new workspace.
            The parameter is required if the user has access to more than one subscription.
        :type subscription_id: str
        :param resource_group: The azure resource group that is containing the workspace.
            The parameter defaults to a mutation of the workspace name.
        :type resource_group: str
        :param location: The location of the workspace.
            The parameter defaults to the resource group location.
            The location has to be a supported region for Azure Machine Learning Services.
        :type location: str
        :param create_resource_group: When true the resource group will be created if it doesn't exist.
        :type create_resource_group: bool
        :param friendly_name: A friendly name for the workspace that can be displayed in the UI.
        :type friendly_name: str
        :param storage_account: An existing storage account in the azure resource id format.
            The storage will be used by the workspace to save run outputs, code, logs etc.
            If None a new storage will be created.
        :type storage_account: str
        :param key_vault: An existing key vault in the azure resource id format.
            The Key vault will be used by the workspace to store credentials added to the workspace by the users.
            If None a new key vault will be created.
        :type key_vault: str
        :param app_insights: An existing Application Insights in the azure resource id format.
            The Application Insights will be used by the workspace to log webservices events.
            If None a new Application Insights will be created.
        :type app_insights: str
        :param container_registry: An existing Container registery in the azure resource id format.
            The Container registery will be used by the workspace to pull and
            push both experimentation and webservices images.
            If None a new Container registery will be created.
        :type container_registry: str
        :param exist_ok: If True the method will not fail if the workspace already exists.
        :type exist_ok: bool
        :return: The workspace object.
        :rtype: azureml.core.workspace.Workspace
        """
        # Checking the validity of the workspace name.
        check_valid_resource_name(name, "Workspace")
        # TODO: Checks if the workspace already exists.

        if not auth:
            auth = InteractiveLoginAuthentication()

        if not subscription_id:
            subscription_id = Workspace._fetch_subscription(auth)

        if not resource_group:
            # Resource group name should only contains lowercase alphabets.
            resource_group = Workspace._get_resource_name_from_workspace_name(name, "resource_group")

        return Workspace._create_legacy(auth, subscription_id, resource_group, name,
                                        location=location, create_resource_group=create_resource_group,
                                        friendly_name=friendly_name, storage_account=storage_account,
                                        key_vault=key_vault, app_insights=app_insights,
                                        container_registry=container_registry,
                                        exist_ok=exist_ok)

    @staticmethod
    def get(name, auth=None, subscription_id=None, resource_group=None):
        """Return a workspace object for an existing Azure Machine Learning Workspace.

        Throws an exception if the workspace doesn't exist or the required fields doesn't leads to a uniquely
        identifiable workspace.

        :param name: The workspace name to get.
        :type name: str
        :param auth: The auth object.
            If None the default Azure CLI credentials will be used or the API will prompt for credentials.
        :type auth: azureml.core.authentication.ServicePrincipalAuthentication or
            azureml.core.authentication.InteractiveLoginAuthentication
        :param subscription_id: The subscription id to use.
            The parameter is required if the user has access to more than one subscription.
        :type subscription_id: str
        :param resource_group: The resource group to use.
            If None the method will search all resource groups in the subscription.
        :type resource_group: str
        :return: The workspace object.
        :rtype: azureml.core.workspace.Workspace
        """
        if not auth:
            auth = InteractiveLoginAuthentication()

        # If everything is specified then we use the get operation, which is faster than the list
        # operation.
        if subscription_id and resource_group:
            return Workspace(subscription_id, resource_group, name, auth=auth)

        if not subscription_id:
            subscription_id = Workspace._fetch_subscription(auth)

        result_dict = Workspace.list(subscription_id, auth=auth, resource_group=resource_group)
        if name in result_dict:
            workspaces_list = result_dict[name]
            if len(workspaces_list) == 1:
                return workspaces_list[0]
            else:
                workspace_dict_list = []
                for workspace_object in workspaces_list:
                    workspace_dict_list.append(workspace_object._to_dict())

                if len(workspace_dict_list) > 1:
                    raise WorkspaceException("More than 1 workspaces found with name={}.\n"
                                             "Please choose one among these{}".format(name, workspace_dict_list),
                                             found_multiple=True)
                else:
                    raise WorkspaceException("No workspace found with name = {}".format(name))
        else:
            if not subscription_id:
                raise WorkspaceException("No workspaces found with name={} in all the subscriptions "
                                         "that you have access to.".format(name))
            else:
                raise WorkspaceException("No workspaces found with name={} in subscription={}".format(
                    name, subscription_id))

    @staticmethod
    def _get_or_create(name, auth=None, subscription_id=None, resource_group=None,
                       location=None, friendly_name=None, storage_account=None, key_vault=None,
                       app_insights=None, container_registry=None, create_resource_group=True):
        """Get or create a workspace if it doesn't exist.

        Throws an exception if the required fields are not specified.

        :param name: The workspace name.
        :type name: str
        :param auth: The auth object.
        :type auth: azureml.core.authentication.AbstractAuthentication
        :param subscription_id: The subscription id to use.
        :type subscription_id: str
        :param resource_group: The resource group to use.
        :type resource_group: str
        :param location: The workspace location in-case azureml SDK has to create a workspace.
        :type location: str
        :param friendly_name: The friendly name of the workspace.
        :type friendly_name: str
        :param storage_account: The storage account to use for this workspace.
        :type storage_account: str
        :param app_insights: The app insights to use for this workspace.
        :type app_insights: str
        :param key_vault: The keyvault to use for this workspace.
        :type key_vault: str
        :param container_registry: The container registry to use for this workspace.
        :type container_registry: str
        :param create_resource_group: Flag to create resource group or not.
        :type create_resource_group: bool
        :return: The workspace object.
        :rtype: azureml.core.workspace.Workspace
        """
        # Checking the validity of the workspace name.
        check_valid_resource_name(name, "Workspace")

        try:
            return Workspace.get(name, auth=auth, subscription_id=subscription_id,
                                 resource_group=resource_group)

        # Added ProjectSystemException because internally we are throwing
        # ProjectSystemException when a workspace is not found.
        except (WorkspaceException, ProjectSystemException) as e:
            # Distinguishing the case when multiple workspaces with the same name already exists.
            if type(e) == WorkspaceException and e.found_multiple:
                # In this case, we throw the error.
                raise e
            else:
                # Workspace doesn't exist, so we create it.
                return Workspace.create(name, auth=auth, subscription_id=subscription_id,
                                        resource_group=resource_group, location=location,
                                        create_resource_group=create_resource_group,
                                        friendly_name=friendly_name, storage_account=storage_account,
                                        key_vault=key_vault, app_insights=app_insights,
                                        container_registry=container_registry)

    @staticmethod
    def list(subscription_id, auth=None, resource_group=None):
        """List all workspaces that the user has access to in the specified subscription_id parameter.

        The list of workspaces can be filtered based on the resource group.

        :param subscription_id: To list workspaces in the specified subscription id.
        :type subscription_id: str
        :param auth: The auth object.
            If None the default Azure CLI credentials will be used or the API will prompt for credentials.
        :type auth: azureml.core.authentication.ServicePrincipalAuthentication
            or azureml.core.authentication.InteractiveLoginAuthentication
        :param resource_group: To list workspaces in the specified resource group.
            If None the method will list all the workspaces within the specified subscription.
        :type resource_group: str
        :return: A dict, where the key is workspace name, and the value is a list of Workspace objects.
        :rtype: dict
        """
        if not auth:
            auth = InteractiveLoginAuthentication()

        result_dict = dict()
        # All combinations of subscription_id and resource_group specified/unspecified.
        if not subscription_id and not resource_group:
            all_subscriptions = auth._get_all_subscription_ids()
            for subscription_tuple in all_subscriptions:
                subscription_id = subscription_tuple.subscription_id
                # Sometimes, there are subscriptions from which a user cannot read workspaces, so we just
                # ignore those while listing.
                workspaces_list = Workspace._list_legacy(auth, subscription_id=subscription_id, ignore_error=True)
                Workspace._process_autorest_workspace_list(auth, workspaces_list, result_dict)
        elif subscription_id and not resource_group:
            workspaces_list = Workspace._list_legacy(auth, subscription_id=subscription_id)
            Workspace._process_autorest_workspace_list(auth, workspaces_list, result_dict)
        elif not subscription_id and resource_group:
            # TODO: Need to find better ways to just query the workspace with name from ARM.
            all_subscriptions = auth._get_all_subscription_ids()
            for subscription_tuple in all_subscriptions:
                subscription_id = subscription_tuple.subscription_id
                workspaces_list = Workspace._list_legacy(auth, subscription_id=subscription_id,
                                                         resource_group_name=resource_group, ignore_error=True)

                Workspace._process_autorest_workspace_list(auth, workspaces_list, result_dict)
        elif subscription_id and resource_group:
            workspaces_list = Workspace._list_legacy(auth, subscription_id=subscription_id,
                                                     resource_group_name=resource_group)

            Workspace._process_autorest_workspace_list(auth, workspaces_list, result_dict)
        return result_dict

    def _initialize_folder(self, experiment_name, directory="."):
        """Initialize a folder with all files needed for an experiment.

        If the path specified by directory doesn't exist then the SDK creates those directories.

        :param experiment_name: The experiment name.
        :type experiment_name: str
        :param directory: The directory path.
        :type directory: str
        :return: The project object.
        :rtype: azureml.core.project.Project
        """
        # Keeping the import here to prevent the cyclic dependency between Workspace and Project.
        from azureml._project.project import Project
        return Project.attach(self, experiment_name, directory=directory)

    def write_config(self, path=None, file_name=None):
        """Write out the Workspace ARM properties to a config file.

        Worskace ARM properties it can be loaded later using from_config. The path defaults to the current working
        directory and file_name defaults to 'config.json'.

        The method provides a simple way of reusing the same workspace across multiple python notebooks or projects.
        Users can save the workspace ARM properties using this function,
        and use from_config to load the same workspace in different python notebooks or projects without
        retyping the workspace ARM properties.

        :param path: User provided location to write the config.json file.
            The parameter defaults to the current working directory.
        :type path: str
        :param file_name: Name to use for the config file. The parameter defaults to config.json.
        :type file_name: str
        """
        # If path is None, use the current working directory as the path.
        if path is None:
            path = '.'

        normalized_config_path = normalize_path_and_join(path, AML_CONFIG_DIR)
        try:
            check_and_create_dir(normalized_config_path)
        except OSError as e:
            if e.errno in [errno.EPERM, errno.EACCES]:
                raise UserErrorException('You do not have permission to write the config '
                                         'file to: {}\nPlease make sure you have write '
                                         'permissions to the path.'.format(normalized_config_path))
            else:
                raise UserErrorException('Could not write the config file to: '
                                         '{}\n{}'.format(normalized_config_path, str(e)))

        if file_name is None:
            file_name = CONFIG_FILE_NAME
        else:
            file_name = normalize_file_ext(file_name, 'json')

        normalized_file_path = normalize_path_and_join(normalized_config_path, file_name)
        try:
            with open(normalized_file_path, 'w') as config_file:
                json.dump({'subscription_id': self.subscription_id, 'resource_group': self.resource_group,
                           'workspace_name': self.name}, config_file, indent=4)

            # TODO: Print is fine here as this is not called by the CLI.
            print('Wrote the config file {} to: {}'.format(file_name, normalized_file_path))
        except OSError as e:
            raise UserErrorException('Could not write the config file to: '
                                     '{}\n{}'.format(normalized_file_path, str(e)))

    @property
    def name(self):
        """Return the workspace name.

        :return: Workspace name.
        :rtype: str
        """
        return self._workspace_name

    @property
    def subscription_id(self):
        """Return the subscription id for this workspace.

        :return: Subscription id.
        :rtype: str
        """
        return self._subscription_id

    @property
    def resource_group(self):
        """Return the resource group name for this workspace.

        :return: Resource group name.
        :rtype: str
        """
        return self._resource_group

    @property
    def location(self):
        """Return the location of this workspace.

        :return: The location of this workspace.
        :rtype: str
        """
        has_autorest_location = (self._workspace_autorest_object is not None and
                                 self._workspace_autorest_object.location)
        if has_autorest_location:
            return self._workspace_autorest_object.location
        else:
            has_set_location = bool(self._location)
            if has_set_location:
                # Return the hard coded location in the remote context
                return self._location
            else:
                # Sets the workspace autorest object.
                self.get_details()
                return self._workspace_autorest_object.location

    def _sync_keys(self):
        """Sync keys for the current workspace.

        :return:
        :rtype: object
        """
        # TODO: Need to change the return type.
        return _commands.workspace_sync_keys(self._auth, self._resource_group,
                                             self._workspace_name, self._subscription_id)

    def _share(self, user, role):
        """Share the current workspace.

        :param user:
        :type user: str
        :param role:
        :type role: str
        :return:
        :rtype: object
        """
        return _commands.share_workspace(self._auth, self._resource_group,
                                         self._workspace_name, self._subscription_id, user, role)

    def delete(self, delete_dependent_resources=False):
        """Delete the Azure Workspace resource.

        :param delete_dependent_resources: Set delete_dependent_resources=True for deleting
            workspace associated resources, i.e. ACR, storage account, key vault and application insights.
        :type delete_dependent_resources: bool
        :return: None if successful, otherwise throws an error.
        :rtype: None
        """
        _commands.delete_workspace(self._auth, self._resource_group,
                                   self._workspace_name, self._subscription_id, delete_dependent_resources)

    def get_details(self):
        """Return details of this workspace.

        :return: Workspace details in dict format.
        :rtype: dict
        """
        # TODO: Need to change the return type.
        if not self._workspace_autorest_object:
            self._workspace_autorest_object = _commands.show_workspace(
                self._auth, self._resource_group, self._workspace_name,
                self._subscription_id)
        # workspace_autorest is an object of azureml._base_sdk_common.workspace.models.workspace.Workspace
        return convert_dict_keys_to_camel_case(self._workspace_autorest_object.as_dict())

    @property
    def _auth_object(self):
        """Get authentication object.

        :return: Returns the auth object.
        :rtype: azureml.core.authentication.AbstractAuthentication
        """
        return self._auth

    # To be made public in future.
    def _update(self, friendly_name, description, tags=None):
        """Update friendly name, description or tags associated to a workspace.

        :param friendly_name:
        :type friendly_name: str
        :param description:
        :type description: str
        :param tags:
        :type tags: list
        :return: Update information in dict format
        :rtype: dict
        """
        workspace_autorest = _commands.update_workspace(self._auth, self._resource_group,
                                                        self._workspace_name, friendly_name, description,
                                                        self._subscription_id, tags=tags)
        return convert_dict_keys_to_camel_case(workspace_autorest.as_dict())

    def _get_create_status_dict(self):
        """Return the create status in dict format.

        :return:
        :rtype: dict
        """
        # TODO: Will need to remove this function. Adding this to pass tests for now.
        return_dict = convert_dict_keys_to_camel_case(self._workspace_autorest_object.as_dict())
        if "resourceGroup" not in return_dict:
            return_dict["resourceGroup"] = self._resource_group
        return return_dict

    @staticmethod
    def _rand_gen(num_chars):
        """Generate random string.

        :param num_chars:
        :type num_chars: int
        :return: Returns randomly generated string.
        :rtype: str
        """
        return ''.join(choice(ascii_lowercase) for i in range(num_chars))

    @staticmethod
    def _get_resource_name_from_workspace_name(workspace_name, resource_type):
        """Return the resource name.

        :param workspace_name:
        :type workspace_name: str
        :param resource_type:
        :type resource_type: str
        :return: Returns the resource name.
        :rtype: str
        """
        alphabets_str = ""
        for char in workspace_name.lower():
            if char.isalpha():
                alphabets_str = alphabets_str + char

        # Account name should be in lower case.
        # So, getting alphabets from the workspace name
        resource_name = alphabets_str[:8] + resource_type + Workspace._rand_gen(20)

        # Storage account names in azure can only be 24 characters longs.
        if len(resource_name) > 24:
            return resource_name[:24]
        else:
            return resource_name

    @staticmethod
    def _get_scope_details(workspace_arm_scope):
        """Parse the arm scope of a workspace and returns WorkspaceScopeInfo tuple.

        :param workspace_arm_scope:
        :type workspace_arm_scope:
        :return:
        :rtype: _WorkspaceScopeInfo
        """
        subscription_id = re.search(r'/subscriptions/([^/]+)', workspace_arm_scope).group(1)
        resource_group = re.search(r'/resourceGroups/([^/]+)', workspace_arm_scope).group(1)
        workspace_name = re.search(r'/workspaces/([^/]+)', workspace_arm_scope).group(1)
        workspace_scope_info = _WorkspaceScopeInfo(subscription_id, resource_group,
                                                   workspace_name)
        return workspace_scope_info

    @staticmethod
    def _process_autorest_workspace_list(auth, workspace_autorest_list, result_dict):
        """Process a list of workspaces returned by the autorest client and adds those to result_dict.

        Implementation details: key is a  workspace name, value is a list of workspace objects.

        :param auth: The auth object.
        :type auth: azureml.core.authentication.AbstractAuthentication
        :param workspace_autorest_list: list of object of azureml._base_sdk_common.workspace.models.workspace.Workspace
        :type workspace_autorest_list: list
        :param result_dict: A dict to add workspaces.
        :type result_dict: dict
        :return:
        :rtype: None
        """
        if not workspace_autorest_list:
            return

        for workspace_autorest_object in workspace_autorest_list:
            workspace_object = Workspace._get_workspace_from_autorest_workspace(auth, workspace_autorest_object)

            if workspace_object.name in result_dict:
                result_dict[workspace_object.name].append(workspace_object)
            else:
                item_list = list()
                item_list.append(workspace_object)
                result_dict[workspace_object.name] = item_list

    @staticmethod
    def _get_workspace_from_autorest_workspace(auth, auto_rest_workspace):
        """Return workspace.

        :param auth:
        :type auth: azureml.core.authentication.AbstractAuthentication
        :param auto_rest_workspace:
        :type auto_rest_workspace: azureml._base_sdk_common.workspace.models.workspace.Workspace
        :return:
        :rtype: azureml.core.workspace.Workspace
        """
        workspace_scope = Workspace._get_scope_details(auto_rest_workspace.id)
        # Disabling the service check as we just got autorest objects from the service.
        workspace_object = Workspace(workspace_scope.subscription_id, workspace_scope.resource_group,
                                     workspace_scope.workspace_name, auth=auth, _disable_service_check=True)
        workspace_object._workspace_autorest_object = auto_rest_workspace
        return workspace_object

    def _to_dict(self):
        """Serialize this workspace information into a dictionary.

        :return:
        :rtype: dict
        """
        result_dict = dict()
        result_dict["subscriptionId"] = self._subscription_id
        result_dict["resourceGroup"] = self._resource_group
        result_dict["workspaceName"] = self._workspace_name
        return result_dict

    @staticmethod
    def _create_legacy(auth, subscription_id, resource_group_name, workspace_name,
                       location=None, create_resource_group=None, friendly_name=None,
                       storage_account=None, key_vault=None, app_insights=None, container_registry=None,
                       exist_ok=False):
        """Create a workspace.

        :param auth: The auth object.
        :type auth: azureml.core.authentication.AbstractAuthentication
        :param subscription_id: The subscription id to use.
        :type subscription_id: str
        :param resource_group_name: The resource group to use.
        :type resource_group_name: str
        :param workspace_name: The workspace name to use.
        :type workspace_name: str
        :param location: The workspace location in-case azureml SDK has to create a workspace.
        :type location: str
        :param create_resource_group: Flag to create resource group or not.
        :type create_resource_group: bool
        :param friendly_name: The friendly name of the workspace.
        :type friendly_name: str
        :param storage_account: The storage account to use for this workspace.
        :type storage_account: str
        :param key_vault: The keyvault to use for this workspace.
        :type key_vault: str
        :param app_insights: The app insights to use for this workspace.
        :type app_insights: str
        :param container_registry: The container registry to use for this workspace.
        :type container_registry: str
        :param exist_ok: Flag for accepting if the workspace exists.
        :type exist_ok: bool
        :return: The created workspace
        :rtype: azureml.core.workspace.Workspace
        """
        workspace_object_autorest = _commands.create_workspace(auth, resource_group_name,
                                                               workspace_name, subscription_id, location=location,
                                                               create_resource_group=create_resource_group,
                                                               friendly_name=friendly_name,
                                                               storage_account=storage_account,
                                                               key_vault=key_vault,
                                                               app_insights=app_insights,
                                                               containerRegistry=container_registry,
                                                               exist_ok=exist_ok)
        if not workspace_object_autorest:
            raise WorkspaceException("Couldn't create the workspace.")

        # Disabling service check as we just created the workspace.
        workspace_object = Workspace(subscription_id, resource_group_name, workspace_name,
                                     auth=auth, _disable_service_check=True)

        # workspace_object_autorest is an object of class azureml._base_sdk_common.workspace.models.workspace.Workspace
        workspace_object._workspace_autorest_object = workspace_object_autorest
        return workspace_object

    @staticmethod
    def _list_legacy(auth, subscription_id=None, resource_group_name=None, ignore_error=False):
        """List workspaces.

        :param auth:
        :type auth: azureml.core.authentication.AbstractAuthentication
        :param subscription_id:
        :type subscription_id: str
        :param resource_group_name:
        :type resource_group_name: str
        :param ignore_error: ignore_error=True, ignores any errors and returns an empty list.
        :type ignore_error: bool
        :return: list of object of azureml._base_sdk_common.workspace.models.workspace.Workspace
        :rtype: list
        """
        try:
            # A list of object of azureml._base_sdk_common.workspace.models.workspace.Workspace
            workspace_autorest_list = _commands.list_workspace(auth, subscription_id=subscription_id,
                                                               resource_group_name=resource_group_name)
            return workspace_autorest_list
        except Exception as e:
            if ignore_error:
                return None
            else:
                raise e

    @property
    def compute_targets(self):
        """List all compute targets in the workspace.

        :return: Dict with key as compute target name and value as a ComputeTarget object.
        :rtype: dict{str:azureml.core.compute.ComputeTarget}
        """
        return {compute_target.name: compute_target for compute_target in ComputeTarget.list(self)}

    @property
    def datastores(self):
        """List all datastores in the workspace. List operation does not return credentials of the datastores.

        :return: Dict with key as datastore name and value as datastore within the workspace.
        :rtype: dict{str:(AzureFileDatastore or AzureBlobDatastore or AzureDataLakeDatastore
        """
        return {datastore.name: datastore for datastore in _DatastoreClient.list(self)}

    def get_default_datastore(self):
        """Get the default datastore for the workspace.

        :return: The default datastore
        :rtype: AzureFileDatastore or AzureBlobDatastore
        """
        return _DatastoreClient.get_default(self)

    def set_default_datastore(self, name):
        """Set the default datastore for the workspace.

        :param name: The name of the datastore to be set as default
        :type name: str
        """
        _DatastoreClient.set_default(self, name)

    @property
    def experiments(self):
        """List all experiments in the workspace.

        :return: Dict with key as experiment name and value as an Experiment object.
        :rtype: dict{str: azureml.core.experiment.Experiment}
        """
        from azureml.core.experiment import Experiment as _Experiment
        return {experiment.name: experiment for experiment in _Experiment.list(self)}

    @property
    def images(self):
        """Return a list of images in the Workspace.

        :return: Dict with key as image name and value as an Image object.
        :rtype: dict{str: azureml.core.image.image.Image}
        :raises: WebserviceException
        """
        images = Image.list(self)
        result = {}
        for name in set([image.name for image in images]):
            result[name] = max([image for image in images if image.name == name],
                               key=attrgetter('version'))

        return result

    @property
    def models(self):
        """Return a dict where the key is model name, and value is a Model object.

        :return: A dict of models.
        :rtype: dict{str: azureml.core.model.Model}
        :raises: WebserviceException
        """
        models = Model.list(self)
        result = {}
        for name in set([model.name for model in models]):
            result[name] = max([model for model in models if model.name == name],
                               key=attrgetter('version'))

        return result

    @property
    def webservices(self):
        """Return a list of webservices in the Workspace.

        :return: A list of Webservices in the Workspace
        :rtype: dict{str: azureml.core.webservice.Webservice}
        :raises: WebserviceException
        """
        return {webservice.name: webservice for webservice in Webservice.list(self)}

    @staticmethod
    def _fetch_subscription(auth):
        """Get all subscriptions a user has access to.

        If a user has access to only one subscription than that is  returned, otherwise an exception is thrown.

        :param auth:
        :type auth: azureml.core.authentication.AbstractAuthentication
        :return: A subscription id
        :rtype: str
        """
        all_subscriptions = auth._get_all_subscription_ids()
        if len(all_subscriptions) == 0:
            raise WorkspaceException("You don't have access to any subscriptions. "
                                     "Workspace operation failed.")

        if len(all_subscriptions) > 1:
            raise WorkspaceException("You have access to more than one subscriptions. "
                                     "Please specify one from this list = {}".format(all_subscriptions))

        if len(all_subscriptions) == 1:
            return all_subscriptions[0].subscription_id

    @property
    def _workspace_id(self):
        """Return workspace id that is uniquely identifies a workspace.

        :return: Returns the workspace id that is uniquely identifies a workspace.
        :rtype: str
        """
        if self._workspace_autorest_object:
            return self._workspace_autorest_object.workspaceid
        else:
            # Sets the workspace autorest object.
            self.get_details()
            return self._workspace_autorest_object.workspaceid
