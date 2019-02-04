"""
This module provides functionality to create standard-compliant red-connector-clis, from python classes, which implement
a subset of the following functions:
 - receive(access, internal)
 - send(access, internal)
 - receive_directory(access, internal, listing)

For additional functionality the given class can implement the following functions:
 - receive_validate(access)
 - send_validate(access)
 - receive_directory_validate(access)
"""
import sys

import argparse
import inspect
import json

CAPABILITIES = 'capabilities'


class ConnectorFunction:
    """
    Represents a function, which can be implemented by a connector.
    """

    def __init__(self, name, params):
        """
        Creates a new ConnectorFunction

        :param name: The name of the function
        :param params: A Description of the function parameters
        """
        self.name = name
        self.params = params


CONNECTOR_FUNCTIONS = [
    ConnectorFunction(name='receive', params=['access', 'internal']),
    ConnectorFunction(name='send', params=['access', 'internal']),
    ConnectorFunction(name='receive_directory', params=['access', 'internal', 'listing']),
    ConnectorFunction(name='receive_validate', params=['access']),
    ConnectorFunction(name='send_validate', params=['access']),
    ConnectorFunction(name='receive_directory_validate', params=['access']),
]


def _function_to_argument_name(func_name):
    """
    Converts a connector function name like 'receive_validate'into an command line argument name like
    'receive-directory'.

    :param func_name: The connector function name.
    :return: The argument name.
    """
    return func_name.replace('_', '-')


def create_connector_description(connector_class):
    """
    Creates a ConnectorDescription describing the given connector class.

    :param connector_class: The connector class to describe.
    :return: A new ConnectorDescription describing the given connector class.
    """
    connector_description = {}
    for f in CONNECTOR_FUNCTIONS:
        key_name = f.name.replace('_', '-')
        connector_description[key_name] = _has_function(connector_class, f)

    return connector_description


def _has_function(connector_class, func):
    """
    Returns True, if connector_class implements a function like func

    :param connector_class: The given ConnectorClass
    :param func: The connector function
    :return: True, if connector_class implements a function with name <func.name>, with the given parameters
    """
    try:
        f = getattr(connector_class, func.name)
        if not callable(f):
            return False
        spec = inspect.getfullargspec(f)
        if not spec.args == func.params:
            return False
    except AttributeError:
        return False
    return True


def add_parser_argument(parser, func_param):
    """
    Adds parameter to a given parser.

    :param parser: The parser to add the argument to.
    :param func_param: A parameter of a connector function
    """
    if func_param == 'access':
        parser.add_argument('access', action='store', type=str,
                            help='A json file with access information.')
    elif func_param == 'internal':
        parser.add_argument('internal', action='store', type=str,
                            help='A json file with internal information.')
    elif func_param == 'listing':
        parser.add_argument('--listing', action='store', type=str,
                            help='A json file with listing information.')
    else:
        raise ValueError('Unknown function argument "{}" for connector function'.format(func_param))


def add_parser_arguments(parser, func_params):
    """
    Adds needed parameters to a given parser.

    :param parser: The parser to add arguments to.
    :param func_params: The parameters of a connector function
    """
    for func_param in func_params:
        add_parser_argument(parser, func_param)


def create_parser(connector_class, version=None):
    """
    Creates an ArgumentParser for the given connector class.

    :param connector_class: The connector class
    :param version: The version string of the connector_class
    :return: An ArgumentParser
    """
    parser = argparse.ArgumentParser()

    if version is not None:
        parser.add_argument(
            '-v', '--version', action='version', version=version
        )

    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    for func in CONNECTOR_FUNCTIONS:
        if _has_function(connector_class, func):
            sub_parser = subparsers.add_parser(_function_to_argument_name(func.name))
            add_parser_arguments(sub_parser, func.params)

    subparsers.add_parser(CAPABILITIES)

    return parser


def _command_to_connector_function(command):
    """
    Converts a command into a corresponding ConnectorFunction.

    :param command: The given command as string
    :return: A ConnectorFunction, None if no corresponding ConnectorFunction is specified in CONNECTOR_FUNCTIONS
    """
    connector_function = None
    for connector_func in CONNECTOR_FUNCTIONS:
        if command == _function_to_argument_name(connector_func.name):
            connector_function = connector_func
    return connector_function


def _load_json_file(path):
    """
    Loads and parses a json file.

    :param path: A path to a json file
    :return: The parsed content of the given file.
    """
    with open(path, 'r') as f:
        content = json.load(f)
        return content


def run_connector_with_args(connector_class, args):
    """
    Runs the desired function of the given connector_class, which is described in the given arguments

    :param connector_class: The connector class to run
    :param args: The arguments describing which function to call
    :return: Returns 0 if everything succeeded, 1 if the executed function failed, 2 if the function to execute is not
    implemented for the given connector_class.
    """
    if args.command == CAPABILITIES:
        connector_description = create_connector_description(connector_class)
        print(json.dumps(connector_description))
    else:
        # command -> connector function -> parameter -> arguments -> needed files
        connector_function = _command_to_connector_function(args.command)
        assert(connector_function is not None)

        # load needed files
        file_contents = []
        for p in connector_function.params:
            file_path = args.__dict__[p]
            if file_path:
                file_content = _load_json_file(file_path)
            else:
                file_content = None
            file_contents.append(file_content)

        # execute connector
        try:
            connector_method = getattr(connector_class, connector_function.name)
        except AttributeError:
            print(
                'The given connector class "{}" does not implement the function "{}"'.format(
                    connector_class.__name__,
                    connector_function.name
                ),
                file=sys.stderr
            )
            return 2

        try:
            connector_method(*file_contents)
        except Exception as e:
            print(
                'The "{}" function of the "{}" connector failed.\n[{}]\n{}'.format(
                    connector_function.name,
                    connector_class.__name__,
                    e.__class__.__name__,
                    str(e)
                ),
                file=sys.stderr
            )
            return 1

    return 0


def run_connector(connector_class, version=None):
    """
    Creates a cli wrapper around the given connector_class.

    :param connector_class: The connector class to wrap.
    :param version: The version string of the given connector.
    """
    parser = create_parser(connector_class, version=version)
    args = parser.parse_args()
    exit(run_connector_with_args(connector_class, args))
