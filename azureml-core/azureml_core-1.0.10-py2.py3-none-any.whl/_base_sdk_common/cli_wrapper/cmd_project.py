# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os

from azureml._base_sdk_common.common import set_correlation_id, CLICommandOutput
from azureml.core import workspace
from azureml._project.project import Project

from ._common import get_cli_specific_auth, get_cli_specific_output, get_default_subscription_id, \
    get_resource_group_or_default_name, get_workspace_or_default_name

""" Modules """


def attach_project(experiment_name, workspace_name=None, resource_group_name=None, path="."):
    """Attaches a machine learning project to a local directory specified by path."""
    # Set correlation id
    set_correlation_id()

    auth = get_cli_specific_auth()
    default_subscription_id = get_default_subscription_id(auth)

    # resource group can be None, as we create on user's behalf.
    resource_group_name = get_resource_group_or_default_name(resource_group_name, auth=auth,
                                                             project_path=path)
    workspace_name = get_workspace_or_default_name(workspace_name, throw_error=True, auth=auth, project_path=path)

    workspace_object = workspace.Workspace.get(workspace_name, auth=auth,
                                               subscription_id=default_subscription_id,
                                               resource_group=resource_group_name)

    project_object = workspace_object._initialize_folder(experiment_name, directory=path)

    output_dict = project_object._serialize_to_dict()
    output_dict["Output"] = "The project attached successfully."

    command_output = CLICommandOutput("")
    command_output.merge_dict(output_dict)
    return get_cli_specific_output(command_output)


def detach_project(path="."):
    """Detaches a local directory, specified by path, from being a machine learning project."""
    # Set correlation id
    set_correlation_id()
    auth = get_cli_specific_auth()

    project_object = Project(auth=auth, directory=path)
    project_object.detach()

    command_output = CLICommandOutput("")
    command_output.append_to_command_output("The project at {} detached successfully.".format(os.path.abspath(path)))
    command_output.set_do_not_print_dict()
    return get_cli_specific_output(command_output)


def show_project(path="."):
    """Show Project"""
    # Set correlation id
    set_correlation_id()
    auth = get_cli_specific_auth()

    project_object = Project(auth=auth, directory=path)
    return project_object.get_details()


def create_workspace(workspace_name, resource_group_name=None, location=None,
                     friendly_name=None, storage_account=None, key_vault=None, app_insights=None,
                     container_registry=None, create_resource_group=None, exist_ok=False):
    """Create workspace"""
    # Set correlation id
    set_correlation_id()

    auth = get_cli_specific_auth()
    default_subscription_id = get_default_subscription_id(auth)

    # resource group can be None, as we create on user's behalf.
    resource_group_name = get_resource_group_or_default_name(resource_group_name, auth=auth)

    workspace_object = workspace.Workspace.create(workspace_name, auth=auth, subscription_id=default_subscription_id,
                                                  resource_group=resource_group_name, location=location,
                                                  create_resource_group=create_resource_group,
                                                  friendly_name=friendly_name, storage_account=storage_account,
                                                  key_vault=key_vault, app_insights=app_insights,
                                                  container_registry=container_registry, exist_ok=exist_ok)

    # TODO: Need to add a message that workspace created successfully.
    return workspace_object._get_create_status_dict()


def list_workspace(resource_group_name=None):
    """List Workspaces"""
    # Set correlation id
    set_correlation_id()

    auth = get_cli_specific_auth()
    default_subscription_id = get_default_subscription_id(auth)

    # resource group can be None, as we create on user's behalf.
    resource_group_name = get_resource_group_or_default_name(resource_group_name, auth=auth)

    workspaces_dict = workspace.Workspace.list(default_subscription_id, auth=auth,
                                               resource_group=resource_group_name)
    serialized_workspace_list = list()
    for workspace_name in workspaces_dict:
        for workspace_object in workspaces_dict[workspace_name]:
            serialized_workspace_list.append(workspace_object._to_dict())

    return serialized_workspace_list


def delete_workspace(workspace_name, resource_group_name=None, delete_dependent_resources=False):
    """Delete a workspace"""
    # Set correlation id
    set_correlation_id()

    auth = get_cli_specific_auth()
    default_subscription_id = get_default_subscription_id(auth)

    resource_group_name = get_resource_group_or_default_name(resource_group_name, throw_error=True, auth=auth)
    workspace_object = workspace.Workspace(default_subscription_id, resource_group_name,
                                           workspace_name, auth=auth)
    return workspace_object.delete(delete_dependent_resources=delete_dependent_resources)


def workspace_sync_keys(resource_group_name, workspace_name):
    """Sync workspace keys like storage,acr, app insights key"""
    # Set correlation id
    set_correlation_id()

    auth = get_cli_specific_auth()
    default_subscription_id = get_default_subscription_id(auth)

    workspace_object = workspace.Workspace(default_subscription_id, resource_group_name,
                                           workspace_name, auth=auth)
    return workspace_object._sync_keys()


def share_workspace(resource_group_name, workspace_name, user, role):
    # Set correlation id
    set_correlation_id()

    auth = get_cli_specific_auth()
    default_subscription_id = get_default_subscription_id(auth)

    workspace_object = workspace.Workspace(default_subscription_id, resource_group_name,
                                           workspace_name, auth=auth)
    return workspace_object._share(user, role)


def update_workspace(resource_group_name, workspace_name, friendly_name, description=None, tags=None):
    """Update Workspace"""
    # Set correlation id
    set_correlation_id()

    auth = get_cli_specific_auth()
    default_subscription_id = get_default_subscription_id(auth)
    workspace_object = workspace.Workspace(default_subscription_id, resource_group_name,
                                           workspace_name, auth=auth)

    # Returns a dict containing the update details.
    return workspace_object._update(friendly_name, description, tags=tags)


def show_workspace(resource_group_name=None, workspace_name=None):
    """Show Workspace"""
    # Set correlation id
    set_correlation_id()

    auth = get_cli_specific_auth()
    default_subscription_id = get_default_subscription_id(auth)

    resource_group_name = get_resource_group_or_default_name(resource_group_name, auth=auth)
    workspace_name = get_workspace_or_default_name(workspace_name, auth=auth)

    workspace_object = workspace.Workspace(default_subscription_id, resource_group_name,
                                           workspace_name, auth=auth)

    # A dict containing the workspace details.
    return workspace_object.get_details()
