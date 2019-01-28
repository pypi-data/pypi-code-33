# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml._cli import abstract_subgroup
from azureml._cli import cli_command
from azureml._cli import argument

_WORKSPACE_NAME = argument.Argument("workspace_name", "--name", "-n", help="Workspace name.")


class WorkspaceSubGroup(abstract_subgroup.AbstractSubGroup):
    """This class defines the project sub group."""

    def get_subgroup_name(self):
        """Returns the name of the subgroup.
        This name will be used in the cli command."""
        return "workspace"

    def get_subgroup_title(self):
        """Returns the subgroup title as string. Title is just for informative purposes, not related
        to the command syntax or options. This is used in the help option for the subgroup."""
        return "workspace subgroup commands"

    def get_nested_subgroups(self):
        """Returns sub-groups of this sub-group."""
        return super(WorkspaceSubGroup, self).compute_nested_subgroups(__package__)

    def get_commands(self):
        """ Returns commands associated at this sub-group level."""
        # TODO: Adding commands to a list can also be automated, if we assume the
        # command function name to start with a certain prefix, like _command_*
        commands_list = [self._command_workspace_create(),
                         self._command_workspace_list(),
                         self._command_workspace_delete(),
                         self._command_share_workspace(),
                         self._command_workspace_sync_keys(),
                         self._command_workspace_update(),
                         self._command_workspace_show()
                         ]
        return commands_list

    def _command_workspace_create(self):
        function_path = "azureml._base_sdk_common.cli_wrapper.cmd_project#create_workspace"

        workspace_friendly_name = argument.FRIENDLY_NAME.clone()
        workspace_friendly_name.help = "Friendly name for this workspace."

        key_vault = argument.Argument("key_vault",
                                      "--keyvault",
                                      "",
                                      help="Key Vault to be associated with this workspace.")
        storage_argument = argument.Argument("storage_account",
                                             "--storage-account",
                                             "",
                                             help="Storage account to be associated with this workspace.")
        container_registry_argument = argument.Argument(
            "container_registry",
            "--container-registry",
            "",
            help="Container Registry to be associated with this workspace.")
        application_insights_argument = argument.Argument(
            "app_insights",
            "--application-insights",
            "",
            help="Application Insights to be associated with this workspace.")
        create_resource_group_argument = argument.Argument(
            "create_resource_group",
            "--yes",
            "-y",
            action="store_true",
            help="Create a resource group for this workspace.")
        exist_ok_workspace_argument = argument.Argument(
            "exist_ok",
            "--exist-ok",
            "",
            action="store_true",
            help="Do not fail if workspace exists.")

        return cli_command.CliCommand("create", "Create a workspace",
                                      [_WORKSPACE_NAME.get_required_true_copy(),
                                       workspace_friendly_name,
                                       argument.RESOURCE_GROUP_NAME,
                                       argument.LOCATION,
                                       storage_argument,
                                       key_vault,
                                       application_insights_argument,
                                       container_registry_argument,
                                       create_resource_group_argument,
                                       exist_ok_workspace_argument
                                       ], function_path)

    def _command_workspace_list(self):
        function_path = "azureml._base_sdk_common.cli_wrapper.cmd_project#list_workspace"

        return cli_command.CliCommand("list", "List workspaces.",
                                      [argument.RESOURCE_GROUP_NAME], function_path)

    def _command_workspace_sync_keys(self):
        function_path = "azureml._base_sdk_common.cli_wrapper.cmd_project#workspace_sync_keys"

        return cli_command.CliCommand("resync-keys", "Resync keys associated with this workspace.",
                                      [_WORKSPACE_NAME.get_required_true_copy(),
                                       argument.RESOURCE_GROUP_NAME.get_required_true_copy()
                                       ], function_path)

    def _command_share_workspace(self):
        function_path = "azureml._base_sdk_common.cli_wrapper.cmd_project#share_workspace"
        user = argument.Argument("user", "--user", "", help="User with whom to share this workspace.", required=True)
        role = argument.Argument("role", "--role", "", help="Role to assign to this user.", required=True)

        return cli_command.CliCommand("share", "Share this workspace with another user.",
                                      [_WORKSPACE_NAME.get_required_true_copy(),
                                       argument.RESOURCE_GROUP_NAME.get_required_true_copy(),
                                       user, role,
                                       ], function_path)

    def _command_workspace_delete(self):
        function_path = "azureml._base_sdk_common.cli_wrapper.cmd_project#delete_workspace"

        delete_dependent_resources = argument.Argument(
            "delete_dependent_resources",
            "--all-resources", "",
            action="store_true",
            help="Deletes resources which this workspace depends on like storage, acr, kv and app insights.")
        return cli_command.CliCommand("delete", "Delete a workspace.",
                                      [_WORKSPACE_NAME.get_required_true_copy(),
                                       argument.RESOURCE_GROUP_NAME,
                                       delete_dependent_resources
                                       ], function_path)

    def _command_workspace_update(self):
        description = argument.Argument("description", "--description", "-d", help="Description of this workspace.",
                                        required=False)

        tags = argument.Argument("tags", "--tags", "", help="Tags associated with this workspace.", required=False)

        function_path = "azureml._base_sdk_common.cli_wrapper.cmd_project#update_workspace"

        return cli_command.CliCommand("update", "Update a workspace.",
                                      [_WORKSPACE_NAME.get_required_true_copy(),
                                       argument.RESOURCE_GROUP_NAME,
                                       argument.FRIENDLY_NAME.get_required_true_copy(),
                                       description, tags
                                       ], function_path)

    def _command_workspace_show(self):
        function_path = "azureml._base_sdk_common.cli_wrapper.cmd_project#show_workspace"

        return cli_command.CliCommand("show", "Show a workspace.",
                                      [_WORKSPACE_NAME,
                                       argument.RESOURCE_GROUP_NAME
                                       ], function_path)
