# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml._cli import abstract_subgroup
from azureml._cli import cli_command
from azureml._cli import argument


class ProjectSubGroup(abstract_subgroup.AbstractSubGroup):
    """This class defines the project sub group."""

    def get_subgroup_name(self):
        """Returns the name of the subgroup.
        This name will be used in the cli command."""
        return "project"

    def get_subgroup_title(self):
        """Returns the subgroup title as string. Title is just for informative purposes, not related
        to the command syntax or options. This is used in the help option for the subgroup."""
        return "project subgroup commands"

    def get_nested_subgroups(self):
        """Returns sub-groups of this sub-group."""
        return super(ProjectSubGroup, self).compute_nested_subgroups(__package__)

    def get_commands(self):
        """ Returns commands associated at this sub-group level."""
        # TODO: Adding commands to a list can also be automated, if we assume the
        # command function name to start with a certain prefix, like _command_*
        commands_list = [self._command_project_attach(),
                         self._command_project_detach(),
                         self._command_project_show()
                         ]
        return commands_list

    def _command_project_attach(self):
        function_path = "azureml._base_sdk_common.cli_wrapper.cmd_project#attach_project"
        return cli_command.CliCommand("attach", "Convert a local folder on-disk to an AzureMl project.",
                                      [argument.EXPERIMENT_NAME.get_required_true_copy(),
                                       argument.PROJECT_PATH,
                                       argument.RESOURCE_GROUP_NAME,
                                       argument.WORKSPACE_NAME], function_path)

    def _command_project_detach(self):
        function_path = "azureml._base_sdk_common.cli_wrapper.cmd_project#detach_project"

        return cli_command.CliCommand("detach", "Detach a local folder on-disk from being an AzureMl project.",
                                      [argument.PROJECT_PATH], function_path)

    def _command_project_list(self):
        local_argument = argument.Argument("local", "--local", "-l", help="Show local only.", required=False,
                                           action="store_true")

        function_path = "azureml._base_sdk_common.cli_wrapper.cmd_project#list_project"

        return cli_command.CliCommand("list", "List projects.",
                                      [argument.RESOURCE_GROUP_NAME,
                                       argument.WORKSPACE_NAME, local_argument], function_path)

    def _command_project_update(self):
        friendly_name = argument.Argument("friendly_name", "--friendly-name", "-f",
                                          help="Friendly name for this workspace.", required=False)

        description = argument.Argument("description", "--description", "-d", help="Description of this workspace.",
                                        required=False)

        tags = argument.Argument("tags", "--tags", "", help="Tags associated with this workspace.", required=False)

        function_path = "azureml._base_sdk_common.cli_wrapper.cmd_project#update_project"

        return cli_command.CliCommand("update", "Update a project.",
                                      [argument.WORKSPACE_NAME, argument.PROJECT_NAME,
                                       argument.RESOURCE_GROUP_NAME,
                                       friendly_name, description,
                                       argument.PROJECT_PATH, tags], function_path)

    def _command_project_show(self):
        function_path = "azureml._base_sdk_common.cli_wrapper.cmd_project#show_project"
        return cli_command.CliCommand("show", "Shows details for an AzureMl project.",
                                      [argument.PROJECT_PATH], function_path)
