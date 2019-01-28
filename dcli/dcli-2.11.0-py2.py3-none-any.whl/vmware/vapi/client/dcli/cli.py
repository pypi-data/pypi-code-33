#!/usr/bin/env python
"""
CLI client
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright (c) 2015-2018 VMware, Inc.  All rights reserved. '
__license__ = 'SPDX-License-Identifier: MIT'
__docformat__ = 'epytext en'

import importlib
import json
import logging
import os
import sys
import six
import requests

from vmware.vapi.client.dcli.__version__ import __version__ as dcli_version
from vmware.vapi.client.dcli.connection import CliConnection
from vmware.vapi.client.dcli.command import CliCommand
from vmware.vapi.client.dcli.credstore import (
    CredentialsStore, VapiCredentialsStore, CSPCredentialsStore
)
from vmware.vapi.client.dcli import exceptions
from vmware.vapi.client.dcli.exceptions import (
    handle_error, extract_error_msg, CliArgumentException,
    handle_connection_error, handle_ssl_error)
from vmware.vapi.client.dcli.internal_commands.about import About
from vmware.vapi.client.dcli.internal_commands.options import Options
from vmware.vapi.client.dcli.metadata.local_metadata_provider import \
    LocalMetadataProvider
from vmware.vapi.client.dcli.namespace import CliNamespace
from vmware.vapi.client.dcli.options import CliOptions
from vmware.vapi.client.dcli.shell import CliShell
from vmware.vapi.client.dcli.util import (
    CliHelper, StatusCode, show_default_options_warning,
    have_pyprompt, calculate_time, save_report_to_file,
    ServerTypes, DcliContext,
    prompt_for_credentials, print_top_level_help)
from vmware.vapi.client.lib.formatter import Formatter
from vmware.vapi.core import MethodResult
from vmware.vapi.data.serializers.cleanjson import DataValueConverter

# Change terminal to handle readline issue of displaying weird characters
os.environ['TERM'] = 'vt100'


"""
Disable the InsecurePlatform warning due to the use of Python 2.7 that has
older version of ssl compiled with it
"""  # pylint: disable=W0105
try:
    requests.packages.urllib3.disable_warnings()  # pylint: disable=E1101
except AttributeError:
    # Not present in older versions of requests so ignore the error
    pass

# keeps track of CliMain instance; used for testing purposes
cli_main = None

logger = logging.getLogger(__name__)


class CliMain(object):
    """
    Main class to manage CLI
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        self.connections = []
        self.interactive = False
        self.current_dcli_command = None
        self.internal_commands_provider = None
        self.default_options = None
        self.shell = None
        self.revert_temp_values_delegate = []
        self.specified_servers = []

        # used to preserve state in interactive session
        self.username = None
        self.password = None
        self.cacert_file = None
        self.credstore_file = None
        self.credstore_add = None
        self.configuration_file = None
        self.more = None
        self.formatter = None
        self.verbose = None
        self.loglevel = None

        # command scope options only
        self.filter = None

        # cache related data structures
        self.cmd_list = None
        self.ns_list = None
        self.ns_cmd_info = None
        self.cmd_map = None
        self.hidden_cmd_map = None

    def process_input(self, cmd_input, parser, parsed_args=None, fp=sys.stdout):
        """
        Method to split input arguments into vapi and dcli arguments and execute command

        :type cmd_input: :class:`list` of `str`
        :param cmd_input: List of space separated dcli command input
        :type  parser: :class:`CliArgParser`
        :param parser: CliArgParser object
        :type  parsed_args: :class:`list` of parsed input argument options
        :param parsed_args: Parsed input arguments list

        :rtype:  :class:`StatusCode`
        :return: StatusCode
        """
        self.specified_servers = []

        if not parsed_args:
            parsed_args = parser.parse_known_args(cmd_input)

        cli_client_args = parsed_args[0]
        self.filter = cli_client_args.filter if hasattr(cli_client_args, 'filter') else None

        # is_first_call keeps track of whether the process_input method is called for the first time
        # or from interactive session
        is_first_call = not self.interactive

        self.collect_specified_servers(cli_client_args, is_first_call)

        status_code = self.handle_basic_params(cli_client_args, parser, fp)
        if status_code is not None:
            return status_code

        self.set_plus_options(cli_client_args, is_first_call)
        if not is_first_call:
            self.update_sessions_options(cli_client_args)

        if cli_client_args.credstore_remove:
            return self.remove_credstore_entry(cli_client_args.session_manager)

        connections = self.get_connections(cli_client_args, is_first_call)

        arg_list = cli_client_args.args + parsed_args[1]
        vapi_cmd, vapi_cmd_args = CliMain.break_command_from_args(arg_list)

        if is_first_call:
            try:
                if connections:
                    self.add_connections(connections)
                else:
                    # set default options instance for usage of internal commands
                    # with no server provided
                    self.set_default_options(configuration_file=cli_client_args.configuration_file)
                self.log_command_securely(parsed_args, cmd_input)
            except Exception as e:
                msg = extract_error_msg(e)
                handle_error(msg, print_usage=True, exception=e)
                return StatusCode.INVALID_ARGUMENT
            if have_pyprompt and cli_client_args.interactive:
                return self.enter_interactive_mode(cli_client_args, arg_list)
        else:  # Interactive mode handling
            if connections:
                self.add_connections(connections)
                calculate_time(self.cache_cli_metadata,
                               'shell cache')

            CliHelper.configure_logging(self.loglevel, self.verbose)

        if not vapi_cmd and vapi_cmd_args:
            error_msg = 'unrecognized arguments: %s' % ' '.join(vapi_cmd_args)
            handle_error(error_msg)
            return StatusCode.INVALID_COMMAND

        try:
            status = self.execute_command(vapi_cmd, vapi_cmd_args, fp)
        finally:
            if self.interactive:
                self.revert_temp_sessions_values()

        return status

    def handle_basic_params(self, cli_client_args, parser, fp):
        """
        Handle cases where options does not need connection or session options

        :type  cli_client_args: :class:`list` of input argument options
        :param cli_client_args: Parsed input arguments list
        :type  parser: :class:`CliArgParser`
        :param parser: CliArgParser object
        """
        if cli_client_args.args and \
                cli_client_args.args[0] in ('-h', '--help'):
            parser.print_help()
            return StatusCode.SUCCESS

        if cli_client_args.args and \
                cli_client_args.args[0] in ('-v', '--version'):
            print(About(None).get())
            return StatusCode.SUCCESS

        if (cli_client_args.session_manager
                and not cli_client_args.credstore_remove):
            handle_error('session-manager option only available with credstore-remove option')
            return StatusCode.INVALID_ARGUMENT

        if cli_client_args.credstore_list:
            explicit_servers = self.get_explicitly_specified_servers()
            if explicit_servers:
                for server in explicit_servers:
                    if server["type"] in (ServerTypes.VMC, ServerTypes.NSX):
                        CSPCredentialsStore(cli_client_args.credstore_file).list(self.formatter, fp=fp)
                        print()
                    else:
                        VapiCredentialsStore(cli_client_args.credstore_file).list(server=server["address"], formatter=self.formatter, fp=fp)
                        print()
                return StatusCode.SUCCESS
            credstore = CredentialsStore(cli_client_args.credstore_file)
            return credstore.list_all(self.formatter, fp=fp)

        return None

    def set_plus_options(self, cli_client_args, is_first_call):
        """
        Initializes values for interactive session plus options.

        :type  cli_client_args: :class:`list` of input argument options
        :param cli_client_args: Parsed input arguments list
        :type  is_first_call: :class:`bool`
        :param is_first_call: Specifies if command is from non-interactive mode or
            from call before entering interactive session
        """
        if not is_first_call:
            return

        self.interactive = self.interactive or cli_client_args.interactive
        for option in CliOptions.interactive_session_plus_options:
            # saved for non-intearctive calls and preserved as interactive session defaults
            setattr(self, option, getattr(cli_client_args, option))

    def update_sessions_options(self, cli_client_args):
        """
        Manages to set correct values for plus options based on user input and
        interactive and connection sessions logic

        :type  cli_client_args: :class:`list` of input argument options
        :param cli_client_args: Parsed input arguments list
        """
        options = CliOptions.interactive_session_plus_options + CliOptions.connection_session_plus_options_only
        for option in options:
            # if option not provided explicitly - do nothing
            if getattr(cli_client_args, option) is None:
                continue

            # first check options in interactive session
            if option in CliOptions.interactive_session_plus_options \
                    and getattr(cli_client_args, option) != getattr(self, option):
                old_value = getattr(self, option)
                setattr(self, option, getattr(cli_client_args, option))
                # revert back previous value in interactive session;
                # delegate executed right after execute_command
                self.revert_temp_values_delegate.append(
                    lambda option=option, prev_value=old_value: setattr(self, option, prev_value))

            # then in all connections

            # skip options unavailable to connection session
            if option in CliOptions.interactive_session_plus_options_only:
                continue

            for connection in self.connections:
                if getattr(cli_client_args, option) != getattr(connection, option):
                    old_value = getattr(connection, option)
                    setattr(connection, option, getattr(cli_client_args, option))
                    # revert back previous value in connection session;
                    # only if no server provided explicitly, otherwise
                    # it is preserved as new value for connection session
                    # and we don't want to revert that
                    if CliMain.is_new_connection(cli_client_args, connection):
                        continue

                    self.revert_temp_values_delegate.append(
                        lambda connection=connection, option=option, prev_value=old_value: setattr(connection, option, prev_value))

    def revert_temp_sessions_values(self):
        """
        Reverts temporary set values for interactive and connections session properties
        Executed right after execute_command
        """
        for func in self.revert_temp_values_delegate:
            func()
        self.revert_temp_values_delegate = []

    def collect_specified_servers(self, cli_client_args, is_first_call):
        """
        From given input parameters and environment variables collect information for provided servers

        :type  cli_client_args: :class:`list` of input argument options
        :param cli_client_args: Parsed input arguments list
        :type  is_first_call: :class:`bool`
        :param is_first_call: Is this first call or it's coming from interactive mode
        """
        if cli_client_args.server is not None:
            server_info = {'address': cli_client_args.server, 'type': ServerTypes.VSPHERE, 'explicit': True}
            self.specified_servers.append(server_info)
        elif CliOptions.DCLI_SERVER:
            # to deduce explicitly set +server option,
            # cli_client_args.server default value is not set to DCLI_SERVER env var
            # we set it here if env var is specified
            self.specified_servers.append({'address': CliOptions.DCLI_SERVER, 'type': ServerTypes.VSPHERE, 'explicit': False})

        if cli_client_args.nsx_server is not None:
            server_info = {'address': cli_client_args.nsx_server, 'type': ServerTypes.NSX, 'explicit': True}
            self.specified_servers.append(server_info)
        elif CliOptions.DCLI_NSX_SERVER and is_first_call:
            # to deduce explicitly set +nsx-server option,
            # cli_client_args.nsx_server default value is not set to DCLI_NSX_SERVER env var
            # we set it here if env var is specified
            self.specified_servers.append({'address': CliOptions.DCLI_NSX_SERVER, 'type': ServerTypes.NSX, 'explicit': False})

        if cli_client_args.vmc_server:
            server_info = {'address': cli_client_args.vmc_server, 'type': ServerTypes.VMC, 'explicit': True}
            self.specified_servers.append(server_info)

    def get_explicitly_specified_servers(self):
        """
        Returns only explicitly specified servers

        :rtype:  :class:`list` of :class:`dict`
        :return: Returns only map of explicitly specified servers
        """
        return [server for server in self.specified_servers if server['explicit'] is True]

    def get_connections(self, cli_client_args, is_first_call):
        """
        Prepare cli connections objects from specified + server parameters
        Currently dcli supports only one connection in non-interactive mode
        and more than one in interactive mode but only one from specific type

        :type  cli_client_args: :class:`list` of input argument options
        :param cli_client_args: Parsed input arguments list
        :type  is_first_call: :class:`bool`
        :param is_first_call: Is this first call or it's coming from interactive mode

        :rtype:  :class:`CliConnection` or :class:`list` of :class:`CliConnection`
        :return: Empty list if no connections specified; single
            connection in non-interactive mode, list of connections in interactive mode
        """
        if not self.specified_servers:
            return []

        if not self.interactive:
            # verify only one server set in non-interactive
            if len(self.get_explicitly_specified_servers()) == 1:
                server = self.get_explicitly_specified_servers()[0]
            elif len(self.specified_servers) == 1:
                server = self.specified_servers[0]
            elif not self.specified_servers:
                return []
            else:
                error_msg = ('Error: Multiple servers provided.\n'
                             'Error: In non-interactive mode provide only one of the +server, +vmc-server, or +nsx-server parameters explicitly '
                             'or set only one of the environment variables: DCLI_SERVER, DCLI_NSX_SERVER')
                handle_error(error_msg)
                raise CliArgumentException(error_msg, StatusCode.INVALID_ENV, print_error=False)

            return [self.get_connection(server, cli_client_args, is_first_call)]
        else:
            connections = []

            if is_first_call:
                servers = self.specified_servers
            else:
                servers = self.get_explicitly_specified_servers()

            for server in servers:
                connections.append(self.get_connection(server, cli_client_args, is_first_call))
            return connections

    def get_connection(self, server, cli_client_args, is_first_call):
        """
        Verify and set credential information for cli connection

        :type  server: :class:`dcit` of :class:`str` and :class:`str` or :class:`ServerType`
        :param server: Dict containing server address and server type
        :type  cli_client_args: :class:`list` of input argument options
        :param cli_client_args: Parsed input arguments list
        :type  is_first_call: :class:`bool`
        :param is_first_call: Is this first call or it's coming from interactive mode

        :rtype:  :class:`CliConnection` or :class:`list` of :class:`CliConnection`
        :return: None or empty list if no connections specified; single
            connection in non-interactive mode, list of connections if in interactive mode
        """
        if self.password and not self.username:
            error_msg = 'Missing username argument'
            handle_error(error_msg)
            raise CliArgumentException(error_msg, StatusCode.NOT_AUTHENTICATED)

        if self.should_prompt_for_password(cli_client_args, is_first_call):
            _, self.password, credstore_flag = \
                prompt_for_credentials(server['type'],
                                       username=self.username,
                                       credstore_add=self.credstore_add)
            self.credstore_add = credstore_flag

        if server['type'] in (ServerTypes.VMC, ServerTypes.NSX):
            if self.username or self.password:
                module_name = CliHelper.get_module_name(server['type'])
                error_msg = ('When connected to {} server you need to provide '
                             'refresh token instead of username/password '
                             'credentials. You will be prompted when +{}-server '
                             'option is provided.').format(module_name.upper(),
                                                           module_name)
                handle_error(error_msg)
                raise CliArgumentException(error_msg, StatusCode.INVALID_ARGUMENT)

        return CliConnection(server=server['address'],
                             server_type=server['type'],
                             username=self.username,
                             password=self.password,
                             skip_server_verification=cli_client_args.skip_server_verification,
                             cacert_file=self.cacert_file,
                             credstore_file=self.credstore_file,
                             credstore_add=self.credstore_add,
                             configuration_file=self.configuration_file,
                             show_unreleased_apis=cli_client_args.show_unreleased_apis,
                             more=self.more,
                             interactive=self.interactive,
                             formatter=self.formatter)

    def should_prompt_for_password(self, cli_client_args, is_first_call):
        """
        Verifies whether dcli should prompt for password

        :type  cli_client_args: :class:`list` of input argument options
        :param cli_client_args: Parsed input arguments list
        :type  is_first_call: :class:`bool`
        :param is_first_call: Is this first call or it's coming from interactive mode

        :rtype:  :class:`bool`
        :return: True or False depending on whether user should be prompted for password
        """
        if is_first_call and self.interactive:
            return False

        if self.username and not self.password and not cli_client_args.credstore_remove:
            return True

        return False

    def enter_interactive_mode(self, cli_client_args, arg_list):
        """
        Initializes and runs shell object which is responsible for handling
        interactive mode

        :type  cli_client_args: :class:`list` of input argument options
        :param cli_client_args: Parsed input arguments list
        :type  arg_list: :class:`list` of :class:`str`
        :param arg_list: dcli clean command (no plus options) tokens list

        :rtype:  :class:`StatusCode`
        :return: StatusCode
        """
        calculate_time(self.cache_cli_metadata,
                       'initialize shell cache')

        self.shell = CliShell(self, prompt=cli_client_args.prompt)
        logger.info('Starting interactive mode')
        self.shell.run_shell(' '.join(arg_list))
        return StatusCode.SUCCESS

    def add_connections(self, connections):
        """
        Adds connection to current connections list

        :type  connections: :class:`list` of :class:`CliConnection`
        :param connections: Connections to be added to current connections list
        """
        if not self.interactive:
            # in non-interactive mode there's only one connection
            self.connections = connections
        else:
            # interactive mode
            for specified_connection in connections:
                for idx, current_connection in enumerate(self.connections):
                    # overrides connection if server type already connected
                    if current_connection.server_type == specified_connection.server_type:
                        self.connections[idx] = specified_connection
                        logger.info("Connection of type '%s' got overriden", CliHelper.get_module_name(specified_connection.server_type))
                        break
                else:
                    # new connection; add it to rest of connections
                    self.connections.append(specified_connection)

        # reset default option to update it's configuration_file and
        # server values according to new connection
        self.set_default_options()

    def set_default_options(self, configuration_file=None):
        """
        Sets default options instance based on whether connection is already
        initialized or not.

        :type  configuration_file: :class:`str`
        :param configuration_file: Configuration file path to set to default options instance
        """
        if self.connections and len(self.connections) == 1:
            if configuration_file is None:
                configuration_file = self.connections[0].configuration_file
            dcli_context = DcliContext(configuration_path=configuration_file,
                                       server=self.connections[0].server,
                                       server_type=self.connections[0].server_type)
        else:
            if configuration_file is None:
                configuration_file = self.configuration_file
            dcli_context = DcliContext(configuration_path=configuration_file,
                                       server=None,
                                       server_type=None)

        try:
            self.default_options = Options(dcli_context)
        except ValueError:
            show_default_options_warning(dcli_context.configuration_path)

    def get_internal_commands_provider(self):
        """
        Used to get internal commands provider.
        Manages only one instance of interanl commands provider is used

        :rtype:  :class:`vmware.vapi.client.dcli.metadata.local_metadata_provider.LocalMetadataProvider`
        :return: Instance internal commands provider
        """
        if not self.internal_commands_provider:
            self.internal_commands_provider = LocalMetadataProvider(server_type='internal')
        return self.internal_commands_provider

    def cache_cli_metadata(self):
        """
        Caches cli metadata based on given connections and internal commands provider
        Each call reloads cached data.
        """
        # since currently cache is not based on connection level
        # we need to reload the cache in case already added connection is
        # reconnected
        self.cmd_list = []
        self.ns_list = []
        # ns_cmd_info key is full path to command or namespace; value is tuple with two values:
        # (cmd or namespace description, True if namespace otherwise False)
        self.ns_cmd_info = {}
        # cmd_map key is command or namespace path; value is command or namespace name
        self.cmd_map = {}
        # hidden_cmd_map key is command or namespace path; value is command or namespace name
        self.hidden_cmd_map = {}

        try:
            for connection in self.connections:
                self.cache_namespaces(connection.get_namespaces())
                self.cache_commands(connection.get_commands())

            self.cache_namespaces(self.get_internal_commands_provider().get_namespaces())
            self.cache_commands(self.get_internal_commands_provider().get_commands())

        except requests.exceptions.SSLError as e:
            handle_ssl_error(e)
            raise CliArgumentException(e.message, status_code=StatusCode.INVALID_ARGUMENT)
        except requests.exceptions.RequestException as e:
            handle_connection_error(e)
            raise CliArgumentException(e.message, status_code=StatusCode.INVALID_ARGUMENT)
        except Exception as e:
            e_msg = extract_error_msg(e)
            msg = "Couldn't connect to the server"
            if e_msg:
                msg = "%s. %s" % (msg, e_msg)
            logger.error(msg)
            raise CliArgumentException(msg, status_code=StatusCode.INVALID_ARGUMENT)

    def cache_namespaces(self, namespaces):
        """
        Cache namespaces from metadata for autocompletion and command invocation
        """
        for ns in namespaces:
            if ns.name and ns.path:
                full_path = '%s.%s' % (ns.path, ns.name)
                self.ns_list.append(full_path)
                if full_path in self.ns_cmd_info and self.ns_cmd_info[full_path][0] != ns.short_description:
                    # namespace already added by another connection; clear description
                    self.ns_cmd_info[full_path] = ('', True)
                else:
                    self.ns_cmd_info[full_path] = (ns.short_description, True)

            for hidden_ns in CliOptions.DCLI_HIDDEN_NAMESPACES:
                if (not hidden_ns['name'] and ns.path.startswith(hidden_ns['path'])) or \
                        ns.path.startswith('%s.%s' % (hidden_ns['path'], hidden_ns['name'])):
                    self.hidden_cmd_map.setdefault(ns.path, []).append(ns.name)
                    break
                elif ns.path == hidden_ns['path'] and ns.name == hidden_ns['name']:
                    break
            else:  # executed if no break or Exception occur in the loop
                self.cmd_map.setdefault(ns.path, []) if not ns.name else self.cmd_map.setdefault(ns.path, []).append(ns.name)  # pylint: disable=W0106

    def cache_commands(self, commands):
        """
        Cache commands from metadata for autocompletion and command invocation
        """
        for cmd in commands:
            full_cmd_name = '%s.%s' % (cmd.path, cmd.name)
            self.cmd_list.append(full_cmd_name)
            self.ns_cmd_info[full_cmd_name] = (cmd.short_description, False)

            for hidden_ns in CliOptions.DCLI_HIDDEN_NAMESPACES:
                if (not hidden_ns['name'] and cmd.path.startswith(hidden_ns['path'])) or \
                        cmd.path.startswith('%s.%s' % (hidden_ns["path"], hidden_ns["name"])):
                    self.hidden_cmd_map.setdefault(cmd.path, []).append(cmd.name)
                    break
            else:  # executed if no break or Exception occur in the loop
                self.cmd_map.setdefault(cmd.path, []).append(cmd.name)

    @staticmethod
    def is_new_connection(cli_client_args, connection):
        """
        Verifies whether provided connection is newly initialized by current command
        or it was initialized from different command in interactive mode

        :type  cli_client_args: :class:`list` of input argument options
        :param cli_client_args: Parsed input arguments list
        :type  connection: :class:`CliConnection`
        :param connection: Connection to check against whether to revert session options

        :rtype:  :class:`bool`
        :return: Whether session options should be reverted after command execution
        """
        return (cli_client_args.server and connection.server_type == ServerTypes.VSPHERE)\
            or (cli_client_args.vmc_server and connection.server_type == ServerTypes.VMC)\
            or (cli_client_args.nsx_server and connection.server_type == ServerTypes.NSX)

    @staticmethod
    def break_command_from_args(args_list):
        """
        Splits given args into cmd args and options args

        :type  args_list: :class:`list` of :class:`str`
        :param args_list: dcli clean command (no plus options) tokens list

        :rtype:  :class:`tuple` of :class:`list` of :class: `str` and :class:`list` of :class:`str`
        :return: Tuple of list of command tokens with no -- options and list of -- options
        """
        # break command path and args
        if args_list:
            arg_index = [i for i, x in enumerate(args_list) if x.startswith('-')]
            index = len(args_list) if not arg_index else arg_index[0]
            cmd = args_list[0:index]
            cmd_args = args_list[index:]
        else:
            cmd = ''
            cmd_args = None
        return cmd, cmd_args

    def remove_credstore_entry(self, session_manager):
        """
        Removes item from credstore
        If in interactive mode, needs either explicitly provided connection
        or being connected to one connecition only
        In non-interactive mode only one connection is expected

        :type  session_manager: :class:`str`
        :param session_manager: Session manager provided by user

        :rtype:  :class:`StatusCode`
        :return: StatusCode
        """
        logger.info('Removing credstore entry')

        throw_error = False
        error_msg = None
        if self.get_explicitly_specified_servers():
            # explicitly provided single connection
            if len(self.get_explicitly_specified_servers()) == 1:
                remove_from_connection = self.get_explicitly_specified_servers()[0]
            else:
                throw_error = True
        else:
            # no explicitly provided connection; check current connection if any
            if not self.connections:
                remove_from_connection = {'address': None,
                                          'type': None}
            elif len(self.connections) > 1:
                throw_error = True
            else:
                remove_from_connection = {'address': self.connections[0].server,
                                          'type': self.connections[0].server_type}

            # no need to check in self.specified_connections as this looks
            # like implicit action and might not be expected from the user

        if throw_error:
            error_msg = error_msg or ('More than one servers to choose from. '
                                      'Specify explicit server to remove user from.')
            handle_error(error_msg)
            raise CliArgumentException(error_msg, StatusCode.INVALID_ENV, print_error=False)

        if remove_from_connection['type'] in (ServerTypes.NSX, ServerTypes.VMC):
            credstore = CSPCredentialsStore(self.credstore_file)
            return credstore.remove(CliOptions.DCLI_VMC_SERVER, self.username)

        credstore = VapiCredentialsStore(self.credstore_file)
        return credstore.remove(remove_from_connection['address'],
                                self.username,
                                session_manager)

    def get_command_secret_map(self, input_args):
        """
        From given input arguments returns whether they form dcli command,
        and the secret map for it
        """
        result = False, None
        old_ignore_error = exceptions.ignore_error
        exceptions.ignore_error = True
        try:
            cmd, _ = CliMain.break_command_from_args(input_args)
            path, name = CliMain.get_command_path(cmd)
            try:
                cli_cmd_instance = self.get_cmd_instance(path, name)
            except CliArgumentException:
                cli_cmd_instance = None
            if cli_cmd_instance and cli_cmd_instance.is_a_command():
                if cli_cmd_instance.secret_map is None:
                    try:
                        cli_cmd_instance.get_parser_arguments()
                    except Exception as e:
                        handle_error('Error occured while trying to build command instance', exception=e, print_error=False)
                        return False, None
                result = True, cli_cmd_instance.secret_map
        finally:
            exceptions.ignore_error = old_ignore_error
        return result

    @staticmethod
    def represents_number(val):
        """
        Verifies whether a given string represents a number (float or integer)
        """
        try:
            float(val)
            return True
        except ValueError:
            return False

    def get_secure_command(self, all_args, secret_map, substitute='*****'):  # pylint: disable=R0201
        """
        From given command string produces new one with escaped values for
        secure options
        """
        next_is_secure = False
        secured_args = []
        for i, arg in enumerate(all_args):
            if next_is_secure:
                if substitute != '':
                    secured_args.append(substitute)
            else:
                secured_args.append(arg)

            next_is_secure = \
                bool(len(all_args) > i + 1
                     and (arg.startswith('+pass')  # if it's password, next should be secured
                          or (arg.startswith('-')  # if it's argument
                              and not CliMain.represents_number(arg)     # but it's not number
                              and arg.lstrip('-') in secret_map          # and is part of secret argument
                              and not (all_args[i + 1].startswith('--')  # and next arg is not cli option
                                       or all_args[i + 1].startswith('+')
                                       or (all_args[i + 1].startswith('-')
                                           and not CliMain.represents_number(all_args[i + 1]))))))

        return ' '.join(secured_args)

    def log_command_securely(self, parser_args, all_input_args):
        """
        Logs command which starts dcli securely without
        exposing actual dcli command which might contain secret values
        """
        input_ = all_input_args

        if parser_args[0].args or parser_args[1]:
            dcli_command_args = parser_args[0].args + parser_args[1]
            is_command, secret_map = self.get_command_secret_map(dcli_command_args)
            if is_command and secret_map:
                secure_cmd = self.get_secure_command(input_, secret_map)
            else:
                secure_cmd = ' '.join(input_)
        else:
            secure_cmd = ' '.join(input_)

        logger.info('Running command: dcli %s', secure_cmd)

    @staticmethod
    def get_command_path(args):
        """
        Break the argument list into command path and name

        :type  args: :class:`list` of :class:`str`
        :param args: dcli clean command argument list with no -- options

        :rtype:  :class:`str` and :class:`str`
        :return: Command path and name
        """
        if args:
            path = '.'.join(args[:-1])
            name = args[-1]
        else:
            path = ''
            name = ''
        return path, name

    def deduce_connection(self, path, name, get_first_occurence=False):
        """
        From given path and name of command deduce connection to be used
        for command execution

        :type  path: :class:`str`
        :param path: dcli command path
        :type  name: :class:`str`
        :param name: dcli command name
        :type  get_first_occurence: :class:`bool`
        :param get_first_occurence: If set to True and connection collisions found
            returns first connection found, otherwise throws error

        :rtype: :class:`CliConnection`
        :return: CliConnection instance selected by given path and name
        """
        # get_first_occurence is meant to be used for cases like colliding namespaces
        selected_connection = None
        if not self.interactive or len(self.connections) == 1:
            return self.connections[0]
        else:
            full_name = '{}.{}'.format(path, name)
            for connection in self.connections:
                if (full_name in connection.get_namespaces_names()
                        or full_name in connection.get_commands_names()):
                    if get_first_occurence:
                        return connection

                    # This should never occur at the moment but let's have this
                    # for completeness
                    if selected_connection:
                        error_msg = ('Dcli can not deduce between two connections.'
                                     'Try connecting to only one instead and try again.')
                        raise CliArgumentException(error_msg, status_code=StatusCode.INVALID_ENV)

                    selected_connection = connection

        return selected_connection

    def get_cmd_instance(self, path, name):
        """
        Method to get CLICommand instance

        :type  path: :class:`str`
        :param path: CLI namespace path
        :type  name: :class:`str`
        :param name: CLI command name

        :rtype: :class:`CliCommand`
        :return: CliCommand instance
        """
        if not path and not name:
            return None

        if path.startswith('env') \
           or (not path and name.startswith('env')):
            # internal command; no connection needed
            return CliCommand('internal',
                              None,
                              self.get_internal_commands_provider(),
                              self.default_options,
                              path=path,
                              name=name)
        elif self.connections:
            active_connection = self.deduce_connection(path, name)
            if active_connection is not None:
                return active_connection.get_cmd_instance(path, name)

        return None

    def get_namespace_instance(self, path, name):
        """
        Method to get CLINamespace instance

        :type  path: :class:`str`
        :param path: CLI namespace path
        :type  name: :class:`str`
        :param name: CLI namespace name

        :rtype: :class:`CLINamespace`
        :return: CLINamespace instance
        """
        if path.startswith('env') \
           or (not path and name.startswith('env')):
            # internal namespace; no connection needed
            return CliNamespace(self.get_internal_commands_provider(), path, name)
        elif self.connections:
            active_connection = self.deduce_connection(path, name, get_first_occurence=True)
            if active_connection is None:
                return None
            return active_connection.get_namespace_instance(path, name)
        else:
            command_name = name if not path else '%s %s' % (path.replace('.', ' '), name)
            raise Exception("No connection specified or unknown command: '%s'" % command_name)

    def execute_command(self, cmd, args_, fp=sys.stdout, interactive_mode=False):
        """
        Main method to handle a vCLI command

        :type  cmd:  :class:`list` of :class:`str`
        :param cmd:  Clean dcli command tokens list with no -- options
        :type  args_: :class:`list` of :class:`str`
        :param args_: Command arguments

        :rtype:  :class:`StatusCode`
        :return: Return code
        """
        path, name = CliMain.get_command_path(cmd)

        if not path and not name:
            if not self.interactive and not self.connections:
                print_top_level_help(False, None)
                return StatusCode.SUCCESS
            elif self.interactive:
                return StatusCode.INVALID_COMMAND

        # todo: in interactive mode we can search in cash instead of calling to see
        # whether namespace was found from metadata
        try:
            cli_ns_instance = self.get_namespace_instance(path, name)
        except Exception as e:
            msg = extract_error_msg(e)
            handle_error(msg, print_usage=True, exception=e)
            return StatusCode.INVALID_ARGUMENT

        if cli_ns_instance and cli_ns_instance.is_a_namespace():
            if len(self.connections) > 1:
                self.extend_namespace(cli_ns_instance)
            cli_ns_instance.print_namespace_help(interactive_mode, fp=fp)
            return StatusCode.INVALID_COMMAND
        else:
            if path.startswith('env') \
                    or (not path and name.startswith('env')):
                # internal command; no connection needed
                cmd_instance = self.get_cmd_instance(path, name)
                if cmd_instance.is_a_command():
                    cmd_input = cmd_instance.collect_command_input(args_)
                    result = calculate_time(lambda:
                                            self.execute_internal_command(cmd_instance,
                                                                          cmd_input,
                                                                          self.default_options.dcli_context),
                                            'interanl command call execution time')

                    formatter_instance = Formatter(cmd_instance.cmd_info.formatter
                                                   if not self.formatter else self.formatter, fp)

                    return calculate_time(lambda: cmd_instance.display_result(result,
                                                                              formatter_instance,
                                                                              self.more,
                                                                              cmd_filter=self.filter),
                                          'display interanl command output time')
                else:
                    command_name = name if not path else '{} {}'.format(path.replace('.', ' '), name)
                    error_msg = "Unknown command: '{}'".format(command_name)
                    handle_error(error_msg)
                    raise CliArgumentException(error_msg, status_code=StatusCode.INVALID_COMMAND, print_error=False)
            elif self.connections:
                active_connection = self.deduce_connection(path, name)
                if active_connection is None:
                    # if command not in cache, that should be invalid command
                    if self.interactive and '.'.join(cmd) not in self.ns_cmd_info:
                        error_msg = "Unknown command: '{}'".format(' '.join(cmd))
                        handle_error(error_msg)
                        raise CliArgumentException(error_msg, StatusCode.INVALID_COMMAND, print_error=False)

                    # this should actually never occur
                    # but let's have it for better recognition of where is the problem
                    # in case users hit it for whatever reason
                    error_msg = "From given context and specified parameters can not deduce connection."
                    handle_error(error_msg)
                    raise CliArgumentException(error_msg, StatusCode.INVALID_COMMAND)
                return active_connection.execute_command(path, name, args_, fp, cmd_filter=self.filter)
            else:
                command_name = name if not path else '%s %s' % (path.replace('.', ' '), name)
                error_msg = "No connection specified or unknown command: '%s'" % command_name
                handle_error(error_msg)
                raise CliArgumentException(error_msg, StatusCode.INVALID_COMMAND)

    def extend_namespace(self, dcli_namespace):
        """
        Updates given dcli namespaces in case of collisions found

        :type  dcli_namespace: :class:`vmware.vapi.client.dcli.namespace.CliNamespace`
        :param dcli_namespace: dcli namespace to check against for collisions
        """
        full_name = '{}.{}'.format(dcli_namespace.path, dcli_namespace.name)
        for connection in self.connections:
            if full_name in connection.get_namespaces_names() and connection.metadata_provider != dcli_namespace.metadata_provider:
                collided_namespace = CliNamespace(connection.metadata_provider,
                                                  dcli_namespace.path,
                                                  dcli_namespace.name)
                dcli_namespace.add_colliding_namespaces(collided_namespace)

    def execute_internal_command(self, cmd_instance, cmd_input, dcli_ctx):
        """
        Method to execute internal dcli operation

        :type  cmd_instance: :class:`CliCommand`
        :param cmd_instance: CliCommand instance
        :type  cmd_input: :class:`argparse.Namespace
        :param cmd_input: Command input dict
        :type  dcli_ctx: :class:`vmware.vapi.client.dcli.util.DcliContext`
        :param dcli_ctx: Dcli context object

        :rtype:  :class:`vmware.vapi.core.MethodResult`
        :return: MethodResult for the internal operation executed
        """
        service_id = cmd_instance.cmd_info.service_id
        operation_id = cmd_instance.cmd_info.operation_id
        class_name = service_id.split('.')[-1].capitalize()
        module_name = 'vmware.vapi.client.dcli.internal_commands.%s' % \
                      service_id[(service_id.index('.') + 1):]
        module = importlib.import_module(module_name)
        class_instance = getattr(module, class_name)(dcli_ctx)

        # replace long_option param name with field_name
        for option in cmd_instance.cmd_info.options:
            long_option_name = option.long_option.replace('-', '_')
            if long_option_name in cmd_input and \
                    option.field_name != long_option_name:
                cmd_input[option.field_name] = \
                    cmd_input[long_option_name]
                del cmd_input[long_option_name]

        result = getattr(class_instance, operation_id)(**vars(cmd_input))

        self.update_default_options(service_id, operation_id)

        data_value_result = DataValueConverter.convert_to_data_value(
            json.dumps(result))
        return MethodResult(output=data_value_result)

    def update_default_options(self, service_id, operation_id):
        """
        Method which reloads default options from configuration file
        if needed

        :type  service_id: :class:`str`
        :param service_id: service id of the operation
        :type  operation_id: :class:`str`
        :param operation_id: operation id
        """
        if self.default_options and \
                CliMain.internal_command_needs_update(service_id, operation_id):
            self.default_options.load_configuration_file()
            for connection in self.connections:
                connection.default_options.load_configuration_file()

    @staticmethod
    def internal_command_needs_update(service_id, operation_id):
        """
        Returns True if operation needs update after execution of
        another internal command

        :type  service_id: :class:`str`
        :param service_id: service id of the operation
        :type  operation_id: :class:`str`
        :param operation_id: operation id
        """
        return \
            (service_id == 'env.options' and operation_id in ('set', 'delete')) or \
            (service_id == 'env.profiles' and operation_id == 'delete') or \
            (service_id == 'env.profiles.default' and operation_id == 'set')


def main(argv=None, fp=sys.stdout):
    """
    CLI client entry point
    """
    if argv is None:
        argv = sys.argv

    CliOptions.setup_dcli_options()

    status = StatusCode.SUCCESS
    CliHelper.configure_logging('info')
    parser = CliHelper.get_parser(False)
    try:
        if six.PY2:
            input_ = [i.decode('utf-8') for i in argv[1:]]
        else:
            input_ = argv[1:]
        input_args = parser.parse_known_args(input_)

        try:
            is_interactive_call = input_args[0].interactive
        except Exception:
            is_interactive_call = False

        if input_args[0].loglevel != 'info' or input_args[0].verbose:
            CliHelper.configure_logging(input_args[0].loglevel, verbose=input_args[0].verbose)

        # global variable used for testing purposes
        global cli_main  # pylint: disable=W0603
        cli_main = CliMain()
        if six.PY2:
            cli_main.current_dcli_command = ' '.join(item.decode('utf-8') for item in argv)
        else:
            cli_main.current_dcli_command = ' '.join(argv)
        status = calculate_time(
            lambda: cli_main.process_input(input_,
                                           parser,
                                           parsed_args=input_args,
                                           fp=fp),
            'dcli process execution time' if is_interactive_call else 'full command execution time',
            cli_main.current_dcli_command)
    except CliArgumentException as e:
        status = e.status_code
        print_usage = False
        if e.print_error:
            msg = extract_error_msg(e)
            handle_error(msg, print_usage=print_usage, exception=e)
    except Exception as e:
        status = StatusCode.INVALID_COMMAND
        parser.print_usage()
        print_usage = True
        msg = extract_error_msg(e)
        handle_error(msg, print_usage=print_usage, exception=e)
    finally:
        save_report_to_file()

    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv))
