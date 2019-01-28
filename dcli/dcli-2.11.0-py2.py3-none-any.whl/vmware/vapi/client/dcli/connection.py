"""
CLI connection specific classes and functions
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright (c) 2018 VMware, Inc.  All rights reserved. '
__license__ = 'SPDX-License-Identifier: MIT'
__docformat__ = 'epytext en'

import logging
import sys
import uuid
import requests

from com.vmware.vapi.std.errors_client import NotFound
from vmware.vapi.client.dcli.__version__ import __version__ as dcli_version
from vmware.vapi.client.dcli.__version__ import __vapi_runtime_version__ as vapi_version
from vmware.vapi.client.dcli.command import CliCommand
from vmware.vapi.client.dcli.credstore import (
    VapiCredentialsStore, CSPCredentialsStore
)
from vmware.vapi.client.dcli.exceptions import (
    handle_error, extract_error_msg, handle_server_error)
from vmware.vapi.client.dcli.internal_commands.options import Options
from vmware.vapi.client.dcli.metadata.local_metadata_provider import \
    LocalMetadataProvider
from vmware.vapi.client.dcli.metadata.remote_metadata_provider import \
    RemoteMetadataProvider
from vmware.vapi.client.dcli.namespace import CliNamespace
from vmware.vapi.client.dcli.options import CliOptions
from vmware.vapi.client.dcli.util import (
    StatusCode, calculate_time,
    ServerTypes, get_vmc_authentication_token, DcliContext,
    prompt_for_credentials, print_top_level_help,
    show_default_options_warning, get_decoded_JWT_token)
from vmware.vapi.client.lib.formatter import Formatter
from vmware.vapi.core import ApplicationContext
from vmware.vapi.lib import connect
from vmware.vapi.lib.constants import (OPID, SHOW_UNRELEASED_APIS)
from vmware.vapi.protocol.client.msg.user_agent_util import init_product_info
from vmware.vapi.security.oauth import create_oauth_security_context
from vmware.vapi.security.session import create_session_security_context
from vmware.vapi.security.sso import (create_saml_bearer_security_context,
                                      SAML_BEARER_SCHEME_ID)
from vmware.vapi.security.user_password import (
    create_user_password_security_context, USER_PASSWORD_SCHEME_ID)

USER_PASS_RETRY_LIMIT = 1

NO_AUTHN_SCHEME = 'com.vmware.vapi.std.security.no_authentication'
SERVER_UNAUTHENTICATED_ERROR = 'com.vmware.vapi.std.errors.unauthenticated'
SERVER_UNAUTHORIZED_ERROR = 'com.vmware.vapi.std.errors.unauthorized'
logger = logging.getLogger(__name__)


class CliConnection(object):  # pylint: disable=R0902
    """
    Class to manage operations related to namespace related commands.
    """
    def __init__(self,
                 server,
                 server_type,
                 username=None,
                 password=None,
                 skip_server_verification=False,
                 cacert_file=None,
                 credstore_file=None,
                 credstore_add=None,
                 configuration_file=None,
                 show_unreleased_apis=None,
                 more=None,
                 formatter=None,
                 interactive=False):
        self.server = CliConnection.get_dcli_server(server, server_type)
        self.server_type = server_type
        self.username = username
        self.password = password
        self.skip_server_verification = skip_server_verification
        self.cacert_file = cacert_file
        self.credstore_file = credstore_file
        self.credstore_add = credstore_add
        self.configuration_file = configuration_file
        self.show_unreleased_apis = show_unreleased_apis
        self.more = more
        self.interactive = interactive
        self.formatter = formatter
        self.session = None
        self.connector = None
        self.auth_connector = None
        self.session_manager = ''
        self.metadata_provider = None
        self.default_options = None
        self.namespaces = None
        self.namespaces_names = None
        self.commands = None
        self.commands_names = None
        self.dcli_context = None
        self.cli_cmd_instance = None
        self.cli_namespace_instance = None

        # set User-Agent information
        user_agent_product_comment = 'i' if self.interactive else None
        init_product_info('DCLI', dcli_version, product_comment=user_agent_product_comment, vapi_version=vapi_version)

        context = self.get_dcli_context()
        try:
            self.default_options = Options(context)
        except ValueError:
            show_default_options_warning(context.configuration_path)

        try:
            self.session = requests.Session()
            self.set_certificates_validation()

            if self.server_type in (ServerTypes.NSX,
                                    ServerTypes.VMC):
                self.connector = connect.get_requests_connector(self.session,
                                                                url=self.server,
                                                                msg_protocol='rest')
                credstore = CSPCredentialsStore(self.credstore_file)
                self.metadata_provider = \
                    LocalMetadataProvider(self.server_type,
                                          self.server,
                                          self.session,
                                          credstore)
            elif self.server_type == ServerTypes.VSPHERE:
                self.connector = connect.get_requests_connector(self.session,
                                                                url=self.server)
                self.metadata_provider = RemoteMetadataProvider(self.connector)
            else:
                self.metadata_provider = None

            if self.server_type == ServerTypes.NSX:
                self.auth_connector = connect.get_requests_connector(self.session,
                                                                     url=CliOptions.DCLI_VMC_SERVER,
                                                                     msg_protocol='rest')
            else:
                self.auth_connector = self.connector

            self.set_application_context()
        except Exception as e:
            error_msg = 'Unable to connect to the server.'
            msg = extract_error_msg(e)
            if msg:
                logger.error('Error: %s', msg)
            logger.exception(e)
            raise Exception(error_msg)

    def set_application_context(self):
        """
        Sets application context for connection's connector
        That is operation id and whether to show unreleased apis
        """
        op_id = str(uuid.uuid4())
        if self.show_unreleased_apis:
            app_ctx = ApplicationContext({OPID: op_id, SHOW_UNRELEASED_APIS: "True"})
        else:
            app_ctx = ApplicationContext({OPID: op_id})
        self.connector.set_application_context(app_ctx)
        self.auth_connector.set_application_context(app_ctx)

    @staticmethod
    def get_dcli_server(server=None, server_type=None):
        """ Get dcli server """
        from six.moves import urllib
        base_url = 'api'
        if server_type in (ServerTypes.NSX, ServerTypes.VMC):
            base_url = ''

        result = server

        if not server:
            result = 'http://localhost/%s' % base_url  # Default server url
        else:
            if server.startswith('http'):
                url = urllib.parse.urlparse(server)
                if not url.scheme or not url.netloc:
                    logger.error('Invalid server url %s. URL must be of format http(s)://ip:port', server)
                    raise Exception('Invalid server url %s. URL must be of format http(s)://ip:port' % server)

                if not url.path or url.path == '/':
                    # If only ip and port are provided append /api
                    result = '%s://%s/%s' % (url.scheme, url.netloc, base_url)
                else:
                    result = server
            else:
                if server_type == ServerTypes.VMC:
                    result = 'http://%s/%s' % (server, base_url)
                else:
                    result = 'https://%s/%s' % (server, base_url)

        if result.endswith('/'):
            result = result[0:len(result) - 1]

        return result

    def get_dcli_context(self):
        """
        Returns dcli context object
        @return: :class:`vmware.vapi.client.dcli.util.DcliContext`
        """
        if self.dcli_context is None:
            self.dcli_context = DcliContext(
                configuration_path=self.configuration_file,
                server=self.server,
                server_type=self.server_type)
        return self.dcli_context

    def set_certificates_validation(self):
        """
        Sets certificates validation options to requests session according to
        users input
        """
        if self.cacert_file:
            self.session.verify = self.cacert_file
        elif self.skip_server_verification:
            self.session.verify = False
        else:
            certs_path = CliOptions.DCLI_CACERTS_BUNDLE
            self.session.verify = certs_path

    def handle_user_and_password_input(self):
        """
        Method to prompt user to enter username, password and
        ask if they want to save credentials in credstore

        :rtype:  :class:`str`, :class:`str`
        :return: username, password
        """
        org_id = CliConnection.get_org_id()
        username, password, should_save = prompt_for_credentials(self.server_type,
                                                                 username=self.username,
                                                                 credstore_add=self.credstore_add,
                                                                 org_id=org_id)

        if self.server_type in (ServerTypes.NSX, ServerTypes.VMC):
            # we just need value different than None or empty string in this case
            username = 'dummy'

        if not self.credstore_add:
            self.credstore_add = should_save

        return username, password

    @staticmethod
    def get_org_id():
        """
        From current entered command returns org id if provided
        Otherwise None is returned

        :rtype:  :class:`str`
        :return: Org id found in the current command
        """
        current_cmd = None
        if '__main__' in sys.modules \
                and hasattr(sys.modules['__main__'], 'cli_main'):
            current_cmd = sys.modules['__main__'].cli_main.current_dcli_command
        elif 'vmware.vapi.client.dcli.cli' in sys.modules:
            current_cmd = sys.modules['vmware.vapi.client.dcli.cli'].cli_main.current_dcli_command
        else:
            logger.info("Module cli which contains CliMain was not found")

        if current_cmd is None:
            return None

        import re
        # searching for '--org GUID' pattern in current command
        match = re.search(r'--org\s([0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})', current_cmd)
        if match is not None:
            return match.group(1)
        return None

    def get_security_context(self, auth_scheme):
        """
        Method to get security context

        :rtype:  :class:`vmware.vapi.core.SecurityContext`
        :return: Security context
        """
        user = self.username
        pwd = self.password
        sec_ctx = None

        if self.server_type in (ServerTypes.VMC, ServerTypes.NSX):
            server = CliOptions.DCLI_VMC_SERVER
        else:
            server = self.server

        if pwd is False:
            # No credentials provided on command line; check credstore
            logger.info('Trying to read credstore for login credentials')
            if self.server_type in (ServerTypes.VMC, ServerTypes.NSX):
                credstore = CSPCredentialsStore(self.credstore_file)
                org_id = CliConnection.get_org_id()
                pwd, creds_info = credstore.get_csp_refresh_token(server, org_id=org_id)
                if creds_info is not None:
                    user = creds_info['user']
            else:
                credstore = VapiCredentialsStore(self.credstore_file)
                user, pwd = credstore.get_vapi_user_and_password(server,
                                                                 self.session_manager,
                                                                 user)

        if auth_scheme == USER_PASSWORD_SCHEME_ID:
            # In case user, pwd weren't provided then prompt for both
            if not user:
                self.username, self.password = self.handle_user_and_password_input()
                return self.get_security_context(auth_scheme)
            else:
                self.username = user
                self.password = pwd

            if self.server_type in (ServerTypes.VMC, ServerTypes.NSX):
                token = get_vmc_authentication_token(self.session, pwd)
                sec_ctx = create_oauth_security_context(token)
            else:
                sec_ctx = create_user_password_security_context(user, pwd)
        elif auth_scheme == SAML_BEARER_SCHEME_ID:  # pylint: disable=too-many-nested-blocks
            token = CliOptions.DCLI_SSO_BEARER_TOKEN

            if not token:
                # Check if user passed STS URL environment variable
                sts_url = CliOptions.STS_URL
                try:
                    try:
                        from vmware.vapi.client.lib import sso
                    except ImportError as e:
                        handle_error('Unable to import SSO libraries', exception=e)
                        sys.exit(StatusCode.INVALID_ENV)

                    auth = sso.SsoAuthenticator(sts_url)

                    # TODO: refactor this authentication code
                    if sts_url:
                        logger.info('Getting SAML bearer token')
                        if not user:
                            self.username, self.password = self.handle_user_and_password_input()

                        token = auth.get_bearer_saml_assertion(self.username,
                                                               self.password,
                                                               delegatable=True)
                    else:
                        # try passthrough authentication
                        logger.info('Using passthrough authentication')
                        token = auth.get_bearer_saml_assertion_gss_api(delegatable=True)
                except Exception as e:
                    msg = extract_error_msg(e)
                    handle_error('Unable to get SAML token for the user. %s' % msg, exception=e)
                    return StatusCode.NOT_AUTHENTICATED
            sec_ctx = create_saml_bearer_security_context(token)

        return sec_ctx

    def authenticate_command(self, service, operation):  # pylint: disable=R0915
        """
        Method to authenticate vAPI command

        :type  service: :class:`str`
        :param service: vAPI service
        :type  operation: :class:`str`
        :param operation: vAPI operation

        :rtype:  :class:`StatusCode`
        :return: Return code of the authentication and whether it is session aware or sessionless
        """
        is_session_aware = False
        curr_auth_scheme = None
        authn_retval = StatusCode.SUCCESS
        auth_schemes = calculate_time(
            lambda: self.metadata_provider.get_authentication_schemes(
                service,
                operation),
            'get authentication schemes time')

        if not auth_schemes:
            return authn_retval, None

        sec_ctx = None
        # If authentication is required check if login credentials (username and password) were provided on the command line
        # If login credentials were provided by the user try to use them to execute the command
        # If login credentials were not provided check if the credstore has credentials for the server and session manager
        # If credstore has credentials for the provided server and session manager use them to execute the command
        # If no credentials were present in credstore try to execute the command using passthrough login

        # get curr auth scheme here and get session manager
        if USER_PASSWORD_SCHEME_ID in auth_schemes:
            logger.info('Using username/password authentication scheme')
            curr_auth_scheme = USER_PASSWORD_SCHEME_ID
        elif SAML_BEARER_SCHEME_ID in auth_schemes:
            logger.info('Using SAML bearer token authentication scheme')
            curr_auth_scheme = SAML_BEARER_SCHEME_ID
        elif NO_AUTHN_SCHEME in auth_schemes:
            logger.info('Using no authentication scheme')
            return StatusCode.SUCCESS, None
        else:
            handle_error('This command does not support login through username/password')
            return StatusCode.NOT_AUTHENTICATED, None

        # pick the first scheme be it session aware or session less
        is_session_aware = curr_auth_scheme and auth_schemes[curr_auth_scheme][0]

        if is_session_aware:
            self.session_manager = auth_schemes[curr_auth_scheme][0]

        user_pass_retry_count = 0
        # breaks when user/pass retry limit reached (for invalid creds) or at script block end(for valid creds)
        while True:
            sec_ctx = calculate_time(
                lambda: self.get_security_context(curr_auth_scheme),
                'get security context time')

            if sec_ctx == StatusCode.NOT_AUTHENTICATED:
                return sec_ctx, None

            if is_session_aware:
                user = self.username
                pwd = self.password
                self.username = None
                self.password = False

                self.auth_connector.set_security_context(sec_ctx)
                logger.info('Doing session login to session manager')
                try:
                    authn_retval, result = calculate_time(
                        self.session_login,
                        'session login time')
                    if result and result.success():
                        session_id = result.output.value
                        # Execute subsequent calls using Session Identifier
                        sec_ctx = create_session_security_context(session_id)

                        if self.credstore_add:
                            authn_retval = self.add_entry_to_credstore(user, pwd)
                    else:
                        raise Exception('Unable to authenticate')
                except Exception as e:
                    if user_pass_retry_count < USER_PASS_RETRY_LIMIT:
                        user_pass_retry_count += 1
                        logger.info('Unsuccessful attempt for authentication. Try entering credentials again.')
                        print("Unable to authenticate user. Please enter the credentials again.")
                        continue
                    else:
                        error_str = 'Unable to authenticate user.'
                        if 'result' in locals() and result and result.error is not None:
                            handle_server_error(result.error)
                        else:
                            handle_error(error_str, exception=e)
                        return StatusCode.NOT_AUTHENTICATED, None

            break

        self.connector.set_security_context(sec_ctx)

        return authn_retval, is_session_aware

    def add_entry_to_credstore(self, user, pwd):
        """
        Adds given credentials entry to the credstore.
        :param user: username
        :param pwd: password
        :return: Status code of the operation
        """
        if self.server_type in (ServerTypes.VMC, ServerTypes.NSX):
            logger.info("Adding credstore entry for provided refresh token")
            credstore = CSPCredentialsStore(self.credstore_file)
            token = get_vmc_authentication_token(self.session, pwd)
            decoded_token = get_decoded_JWT_token(auth_token=token, session=self.session)
            return credstore.add(CliOptions.DCLI_VMC_SERVER, pwd, decoded_token["context_name"], decoded_token["username"])
        logger.info("Adding credstore entry for user '%s'", user)
        credstore = VapiCredentialsStore(self.credstore_file)
        return credstore.add(self.server, user, pwd, self.session_manager)

    def session_login(self):
        """
        Method to login to SessionManager
        """
        return self.invoke_session_manager_method('create')

    def session_logout(self):
        """
        Method to logout from a SessionManager login session
        """
        self.invoke_session_manager_method('delete')
        self.session_manager = ''

    def invoke_session_manager_method(self, method_name):
        """
        Method to invoke session manger

        :type  method_name: :class:`str`
        :param method_name: Name of session manager method

        :rtype: :class:`StatusCode`
        :return: Error code
        :rtype: :class:`vmware.vapi.core.MethodResult`
        :return: Method result
        """
        if not self.session_manager:
            return StatusCode.NOT_AUTHENTICATED, None

        ctx = self.auth_connector.new_context()
        sec_ctx = ctx.security_context
        ctx.security_context = None

        # Check if login method exists
        try:
            input_definition = calculate_time(
                lambda: self.metadata_provider.get_command_input_definition(
                    self.session_manager,
                    method_name),
                'get auth command input definition')
        except NotFound as e:
            # XXX remove this code once everyone moves over to create/delete methods
            if method_name == 'create':
                return self.invoke_session_manager_method('login')
            elif method_name == 'delete':
                return self.invoke_session_manager_method('logout')
            elif method_name == 'logout':
                logger.warning("No logout or delete method found")
                return StatusCode.NOT_AUTHENTICATED, None
            # no login method
            handle_error('Invalid login session manager found', exception=e)
            return StatusCode.NOT_AUTHENTICATED, None

        api_provider = self.auth_connector.get_api_provider()

        ctx.security_context = sec_ctx

        # Method call
        logger.debug('Invoking vAPI operation')
        result = api_provider.invoke(self.session_manager,
                                     method_name,
                                     input_definition.new_value(),
                                     ctx)
        return StatusCode.SUCCESS, result

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
        if self.cli_cmd_instance is None or \
                self.cli_cmd_instance.path != path or \
                self.cli_cmd_instance.name != name:
            self.cli_cmd_instance = CliCommand(self.server_type,
                                               self.connector,
                                               self.metadata_provider,
                                               self.default_options,
                                               path,
                                               name)
        return self.cli_cmd_instance

    def get_namespace_instance(self, path, name):
        """
        Method to get CliNamespace instance

        :type  path: :class:`str`
        :param path: CLI namespace path
        :type  name: :class:`str`
        :param name: CLI namespace name

        :rtype: :class:`CliNamespace`
        :return: CliNamespace instance
        """
        if self.cli_namespace_instance is None or \
                self.cli_namespace_instance.path != path or \
                self.cli_namespace_instance.name != name:
            self.cli_namespace_instance = CliNamespace(self.metadata_provider, path, name)
        return self.cli_namespace_instance

    def execute_command(self, path, name, args_, fp=sys.stdout, cmd_filter=None):
        """
        Main method to handle a vCLI command

        :type  args_: :class:`list` of :class:`str`
        :param args_: Command arguments

        :rtype:  :class:`StatusCode`
        :return: Return code
        """
        cli_cmd_instance = self.get_cmd_instance(path, name)

        if cli_cmd_instance.is_a_command():
            cmd_info = cli_cmd_instance.cmd_info
            user_pass_retry_count = 0
            # breaks when user/pass retry limit reached (for invalid creds) or at script block end(for valid creds)
            while True:
                invalid_credentials = False

                auth_result, is_session_aware = calculate_time(
                    lambda: self.authenticate_command(
                        cmd_info.service_id,
                        cmd_info.operation_id),
                    'full authentication time')

                # clear credentials from memory fast
                # in case of not session aware operation keep them longer in order to verify correct authentication
                # and store valid credentials in credstore
                if not is_session_aware:
                    user = self.username
                    password = self.password
                else:
                    user = None
                    password = False
                self.username = None
                self.password = False

                if auth_result != StatusCode.SUCCESS:
                    return auth_result
                ctx = self.connector.new_context()
                result = calculate_time(lambda:
                                        cli_cmd_instance.execute_command(
                                            ctx,
                                            args_),
                                        'command call to the server time')

                # Reset security context to None
                self.connector.set_security_context(None)

                formatter_instance = Formatter(cmd_info.formatter
                                               if not self.formatter else self.formatter, fp)

                if result.error:
                    if hasattr(result.error, 'name') and \
                            (result.error.name in (SERVER_UNAUTHENTICATED_ERROR,
                                                   SERVER_UNAUTHORIZED_ERROR)) and \
                            not is_session_aware and \
                            user_pass_retry_count < USER_PASS_RETRY_LIMIT and \
                            self.server_type not in (ServerTypes.NSX, ServerTypes.VMC):
                        user_pass_retry_count += 1

                        logger.info('Unsuccessful attempt for authentication. Try entering credentials again.')
                        print("Unable to authenticate user. Please enter the credentials again.")
                        invalid_credentials = True
                        continue
                    else:
                        break

                break

            if self.credstore_add and not is_session_aware and not invalid_credentials:
                self.add_entry_to_credstore(user, password)
                user = None
                password = False

            result = calculate_time(lambda: cli_cmd_instance.display_result(result,
                                                                            formatter_instance,
                                                                            self.more,
                                                                            cmd_filter=cmd_filter),
                                    'display command output time')

            logger.info('Doing session logout from session manager')
            calculate_time(self.session_logout, 'session logout time')

            return result
        else:
            if not name and not path:
                if self.server:
                    error_msg = 'Unable to execute command from the server.\n'
                    error_msg += 'Is server correctly configured?'
                    handle_error(error_msg)
                else:
                    print_top_level_help(self.interactive, self.server_type)
            else:
                command_name = name if not path else '%s %s' % (path.replace('.', ' '), name)
                handle_error("Unknown command: '%s'" % command_name)
            return StatusCode.INVALID_COMMAND
        return StatusCode.INVALID_COMMAND

    def get_namespaces(self):
        """
        Returns list of all connection's namespaces

        :rtype:  :class:`list` of :class:`vmware.vapi.client.dcli.metadata.metadata_info.NamespaceMetadataInfo`
        :return: List of connection's namespaces
        """
        if not self.namespaces:
            self.namespaces = self.metadata_provider.get_namespaces()
        return self.namespaces

    def get_namespaces_names(self):
        """
        Returns list of all connection's namespaces full names

        :rtype:  :class:`list` of :class:`vmware.vapi.client.dcli.metadata.metadata_info.CommandMetadataInfo`
        :return: List of connection's namespaces full names
        """
        if not self.namespaces_names:
            self.namespaces_names = ['{}.{}'.format(ns.path, ns.name) for ns in self.get_namespaces()]
        return self.namespaces_names

    def get_commands(self):
        """
        Returns list of all connection's commands

        :rtype:  :class:`list` of :class:`vmware.vapi.client.dcli.metadata.metadata_info.CommandMetadataInfo`
        :return: List of connection's commands
        """
        if not self.commands:
            self.commands = self.metadata_provider.get_commands()
        return self.commands

    def get_commands_names(self):
        """
        Returns list of all connection's commands full names

        :rtype:  :class:`list` of :class:`vmware.vapi.client.dcli.metadata.metadata_info.CommandMetadataInfo`
        :return: List of connection's commands full names
        """
        if not self.commands_names:
            self.commands_names = ['{}.{}'.format(cmd.path, cmd.name) for cmd in self.get_commands()]
        return self.commands_names
