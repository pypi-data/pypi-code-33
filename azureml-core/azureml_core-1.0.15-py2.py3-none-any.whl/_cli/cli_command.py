# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class CliCommand:
    def __init__(self, name, title, arguments, handler_function_path):
        self._name = name
        self._title = title
        self._arguments = arguments
        self._handler_function_path = handler_function_path

    def get_command_name(self):
        """Returns the name of the command. This name will be used in the cli command."""
        return self._name

    def get_command_title(self):
        """Returns the command title as string. Title is just for informative purposes, not related
        to the command syntax or options. This is used in the help option for the command."""
        return self._title

    def get_command_arguments(self):
        """An abstract method to return command arguments.
        The arguments are returned as a list of Argument class objects."""
        return self._arguments

    def get_handler_function_path(self):
        """Returns the string representation of the handler function for this amlcli command.
        The function name format is module_name#function_name. The module_name should be
        resolvable based on sys.path.
        An example is azure.cli.command_modules.machinelearning.cmd_experiment#start_run"""
        return self._handler_function_path

    def get_cli_to_function_arg_map(self):
        """
        Returns the cli to handler function argument name mapping.
        :return:
        """
        mapping_dict = {}
        for argument in self._arguments:
            if argument.long_form.startswith("--"):
                arg_name = argument.long_form[2:]
            else:
                arg_name = argument.long_form

            mapping_dict[arg_name.replace("-", "_")] = argument.function_arg_name
        return mapping_dict
