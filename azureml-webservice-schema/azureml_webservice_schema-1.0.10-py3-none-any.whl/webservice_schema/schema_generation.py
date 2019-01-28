# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for managing Webservice Schema generation."""
import inspect
import json
import os
from azureml.webservice_schema._schema_util import _generate_service_schema


def generate_schema(run_func, inputs=None, outputs=None, filepath=None):
    """
    Produce a schema file to use when producing a webservice.

    :param run_func: Function object defining run function for service
    :type run_func: func
    :param inputs: Dictionary mapping input parameters of the provided run function to corresponding SampleDefinition
    :type inputs: dict[str, azureml.webservice_schema.sample_definition.SampleDefinition]
    :param outputs: Dictionary mapping outputs of the provided run function to corresponding SampleDefinition
    :type outputs: dict[str, azureml.webservice_schema.sample_definition.SampleDefinition]
    :param filepath: str path to file for writing schema file
    :type filepath: str
    :return: Schema dictionary. Possible keys: "input", "output"
    :rtype: dict[str, dict]
    :raises: IOError, ValueError
    """
    schema = _generate_service_schema(inputs, outputs)
    _validate_run_func_args(run_func, schema['input'] if 'input' in schema else None)
    if filepath is not None:
        # Try to create the hosting folder if it does not exist
        root_folder = os.path.dirname(filepath)
        if not os.path.exists(root_folder):
            os.makedirs(root_folder)
        with open(filepath, 'w') as schema_file:
            json.dump(schema, schema_file)
    return schema


def _validate_run_func_args(run_func, input_schema):
    """
    Validate the provided run function against the provided schema.

    :param run_func:
    :type run_func:
    :param input_schema:
    :type input_schema:
    :return:
    :rtype:
    """
    run_args = _get_args(run_func)

    has_headers = False
    header_param_index = 0
    if "request_headers" in run_args:
        has_headers = True
        header_param_index = run_args.index("request_headers")
        run_args.remove("request_headers")

    default_values = _get_args_defaults(run_func)
    if len(run_args) > 0 and input_schema is None:
        raise ValueError("Provided run function has arguments, input schema needs to be provided")
    if input_schema is not None:
        if len(run_args) != len(input_schema):
            raise ValueError(
                "Argument mismatch: Provided run function has {0} arguments while {1} inputs "
                "were previously declared for it".format(len(run_args), len(input_schema)))
        for arg in run_args:
            # temporarily replacing the stars in front of arguments for comparison sake
            if "*" in arg:
                arg = arg.replace("*", "")
            if "**" in arg:
                arg = arg.replace("**", "")
            if arg not in input_schema:
                raise ValueError("Argument mismatch: Provided run function argument {0} is not "
                                 "present in input types dictionary which contains: ({1})"
                                 .format(arg, ", ".join(input_schema.keys())))

    if has_headers:
        run_args.insert(header_param_index, "request_headers")

    return run_args, default_values


def _get_args(func):
    """
    Get the arguments for the provided function.

    :param func:
    :type func:
    :return:
    :rtype:
    """
    args = inspect.getargs(func.__code__)
    all_args = args.args
    if args.varargs is not None:
        all_args.append('*' + args.varargs)
    if hasattr(args, 'varkw') and args.varkw is not None:
        all_args.append('**' + args.varkw)
    if hasattr(args, 'keywords') and args.keywords is not None:
        all_args.append('**' + args.keywords)
    return all_args


def _get_args_defaults(func):
    """
    Get the default arguments for the provided function.

    :param func:
    :type func:
    :return:
    :rtype:
    """
    args = inspect.getfullargspec(func)
    if args.defaults is not None:
        return dict(zip(args.args[-len(args.defaults):], args.defaults))
    else:
        return dict()
