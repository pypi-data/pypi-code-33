"""
CLI options responsible classes and functions
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright (c) 2015-2018 VMware, Inc.  All rights reserved. '
__license__ = 'SPDX-License-Identifier: MIT'
__docformat__ = 'epytext en'

import argparse
import logging
import os
import sys

logger = logging.getLogger(__name__)


class ArgumentInfo(object):
    """
    ArgumentInfo class to store details of a CLI input argument

    :type  short_name: :class:`str`
    :ivar  short_name: Short name of the CLI command argument
    :type  name: :class:`str`
    :ivar  name: Full name of the CLI command argument
    :type  arg_action: :class:`str`
    :ivar  arg_action: Argument action
    :type  const: :class:`bool`
    :ivar  const: Const or not
    :type  description: :class:`str`
    :ivar  description: Command description
    :type  required: :class:`bool`
    :ivar  required: Required argument or not
    :type  type_: :class:`str`
    :ivar  type_: Argument type
    :type  choices: :class:`tuple`
    :ivar  choices: Possible values for the command argument
    :type  default: :class:`bool`
    :ivar  default: Default value for flag
    :type  nargs: :class:`str`
    :ivar  nargs: nargs for the command argument
    """
    def __init__(self, short_name=None, name=None, arg_action=None, const=None,
                 description=None, required=None, type_=None, choices=None,
                 default=None, nargs=None, mutex_group=None):
        self.short_name = short_name
        self.name = name
        self.arg_action = arg_action
        self.const = const
        self.description = description
        self.required = required
        self.type_ = type_
        self.choices = choices
        self.default = default
        self.nargs = nargs
        self.mutex_group = mutex_group

    def __str__(self):
        return 'short_name=%s name=%s arg_action=%s const=%s description=%s'\
               'required=%s type=%s choices=%s default=%s nargs=%s mutex_group=%s'\
               % (self.short_name, self.name, self.arg_action, self.const,
                  self.description, self.required, self.type_, self.choices,
                  self.default, self.nargs, self.mutex_group)


class CliOptions(object):
    """
    Class to manage operations related to namespace related commands.
    """
    FORMATTERS = ['simple', 'table', 'xml', 'json', 'html', 'csv']
    LOGLEVELS = ['debug', 'info', 'warning', 'error']

    CLI_CLIENT_NAME = None

    DCLI_LOGFILE = None
    DCLI_PROFILE_FILE = None

    # dcli plus options related
    DCLI_SERVER = None
    DCLI_NSX_SERVER = None
    DCLI_VMC_SERVER = None
    DCLI_VMC_STAGING_SERVER = None
    USERNAME_DEFAULT_VALUE = None
    PASSWORD_DEFAULT_VALUE = None
    SKIP_SERVER_VERIFICATION_DEFAULT_VALUE = None
    CACERTFILE_DEFAULT_VALUE = None
    CREDSTORE_FILE_OPTION_DEFAULT_VALUE = None
    CREDSTORE_ADD_DEFAULT_VALUE = None
    CREDSTORE_LIST_DEFAULT_VALUE = None
    CREDSTORE_REMOVE_DEFAULT_VALUE = None
    CONFIGURATION_FILE_OPTION_DEFAULT_VALUE = None
    SHOW_UNRELEASED_APIS_DEFAULT_VALUE = None
    LOG_LEVEL_DEFAULT_VALUE = None
    MORE_OPTION_DEFAULT_VALUE = None
    FORMATTER_OPTION_DEFAULT_VALUE = None
    VERBOSE_DEFAULT_VALUE = None
    PROMPT_DEFAULT_VALUE = None
    INTERACTIVE_DEFAULT_VALUE = None

    DCLI_HISTORY_FILE_PATH = None
    DCLI_CACERTS_BUNDLE = None
    DCLI_SSO_BEARER_TOKEN = None
    STS_URL = None
    DCLI_COLOR_THEME = None

    # specify namespaces that should not appear in dcli below (still callable though)
    DCLI_HIDDEN_NAMESPACES = []

    # internal commands
    DCLI_INTERNAL_COMMANDS_METADATA_FILE = None

    # VMC releated options
    GET_VMC_ACCESS_TOKEN_PATH = None
    VMC_DUMMY_CREDSTORE_USER = None
    DCLI_VMC_CSP_URL = None
    DCLI_VMC_STAGING_CSP_URL = None
    DCLI_METADATA_CACHE_DIR = None
    DCLI_VMC_METADATA_URL = None
    DCLI_VMC_METADATA_FILE = None
    DCLI_NSX_METADATA_URL = None
    DCLI_NSX_METADATA_FILE = None

    interactive_session_plus_options = \
        ['username',
         'password',
         'cacert_file',
         'credstore_file',
         'credstore_add',
         'configuration_file',
         'more',
         'formatter',
         'verbose',
         'loglevel']
    connection_session_plus_options_only = \
        ['skip_server_verification',
         'show_unreleased_apis']
    interactive_session_plus_options_only = \
        ['verbose',
         'loglevel']

    @classmethod
    def setup_dcli_options(cls):
        """
        Reads information from environment variables
        to specify default values for various dcli purposes
        """
        cls.CLI_CLIENT_NAME = 'dcli'

        cls.DCLI_LOGFILE = os.environ.get('DCLI_LOGFILE', '')
        cls.DCLI_PROFILE_FILE = os.environ.get('DCLI_PROFILE_FILE', '')

        cls.DCLI_SERVER = os.environ.get('DCLI_SERVER', None)
        cls.DCLI_NSX_SERVER = os.environ.get('DCLI_NSX_SERVER', None)
        cls.DCLI_VMC_SERVER = os.environ.get('DCLI_VMC_SERVER', 'https://vmc.vmware.com')
        cls.DCLI_VMC_STAGING_SERVER = os.environ.get('DCLI_VMC_STAGING_SERVER', 'https://stg.skyscraper.vmware.com')
        cls.USERNAME_DEFAULT_VALUE = os.environ.get('DCLI_USERNAME', '')
        cls.PASSWORD_DEFAULT_VALUE = False
        cls.SKIP_SERVER_VERIFICATION_DEFAULT_VALUE = False
        cls.CACERTFILE_DEFAULT_VALUE = os.environ.get('DCLI_CACERTFILE', '')
        cls.CREDSTORE_FILE_OPTION_DEFAULT_VALUE = os.environ.get('DCLI_CREDFILE',
                                                                 os.path.join(CliOptions.get_dcli_dir_path(), '.dcli_credstore'))
        cls.CREDSTORE_ADD_DEFAULT_VALUE = False
        cls.CREDSTORE_LIST_DEFAULT_VALUE = False
        cls.CREDSTORE_REMOVE_DEFAULT_VALUE = False
        cls.CONFIGURATION_FILE_OPTION_DEFAULT_VALUE = os.environ.get('DCLI_CONFIGFILE',
                                                                     os.path.join(CliOptions.get_dcli_dir_path(), '.dcli_configuration'))
        cls.SHOW_UNRELEASED_APIS_DEFAULT_VALUE = os.environ.get('DCLI_SHOW_UNRELEASED_APIS', 'false').lower() == 'true'
        cls.LOG_LEVEL_DEFAULT_VALUE = 'info'
        cls.MORE_OPTION_DEFAULT_VALUE = False
        cls.FORMATTER_OPTION_DEFAULT_VALUE = None
        cls.VERBOSE_DEFAULT_VALUE = False
        cls.PROMPT_DEFAULT_VALUE = '{}> '.format('dcli')
        cls.INTERACTIVE_DEFAULT_VALUE = False

        cls.DCLI_HISTORY_FILE_PATH = os.path.expanduser(os.environ.get('DCLI_HISTFILE',
                                                                       os.path.join(CliOptions.get_dcli_dir_path(),
                                                                                    '.dcli_history')))
        # if this is binary get trust store from binary's folder else get it from requests
        if getattr(sys, 'frozen', False):
            # The application is frozen
            certs_path = os.path.join(os.path.dirname(sys.executable),
                                      'cacert.pem')
        else:
            import requests
            certs_path = requests.certs.where()
        cls.DCLI_CACERTS_BUNDLE = os.environ.get('DCLI_CACERTS_BUNDLE', certs_path)
        cls.DCLI_SSO_BEARER_TOKEN = os.environ.get('DCLI_SSO_BEARER_TOKEN', '')
        cls.STS_URL = os.environ.get('STS_URL')
        cls.DCLI_COLOR_THEME = os.environ.get('DCLI_COLOR_THEME', '')

        # specify namespaces that should not appear in dcli below (still callable though)
        cls.DCLI_HIDDEN_NAMESPACES = CliOptions.get_dcli_hidden_namespaces()

        cls.DCLI_INTERNAL_COMMANDS_METADATA_FILE = os.environ.get('DCLI_INTERNAL_COMMANDS_METADATA_FILE', None)

        # VMC related
        cls.GET_VMC_ACCESS_TOKEN_PATH = '{}/csp/gateway/am/api/auth/api-tokens/authorize'
        cls.VMC_DUMMY_CREDSTORE_USER = 'vmc_user'
        cls.DCLI_VMC_CSP_URL = os.getenv('DCLI_VMC_CSP_URL', 'https://console.cloud.vmware.com')
        cls.DCLI_VMC_STAGING_CSP_URL = os.getenv('DCLI_VMC_CSP_URL', 'https://console-stg.cloud.vmware.com/')
        default_metadata_cache = os.path.join(CliOptions.get_dcli_dir_path(), '.metadata_cache')
        cls.DCLI_METADATA_CACHE_DIR = os.environ.get('DCLI_METADATA_CACHE_DIR', default_metadata_cache)
        metadata_url = "{}/rest/com/vmware/vapi/metadata.json"
        cls.DCLI_VMC_METADATA_URL = os.environ.get('DCLI_VMC_METADATA_URL', metadata_url)
        cls.DCLI_VMC_METADATA_FILE = os.environ.get('DCLI_VMC_METADATA_FILE', None)
        cls.DCLI_NSX_METADATA_URL = os.environ.get('DCLI_NSX_METADATA_URL', metadata_url)
        cls.DCLI_NSX_METADATA_FILE = os.environ.get('DCLI_NSX_METADATA_FILE', None)

    @staticmethod
    def get_dcli_dir_path():
        """ Get dcli dir path """
        home = os.path.expanduser('~')
        dcli = '.dcli'
        if home:
            dir_path = os.path.join(home, dcli)
        else:
            logger.error("Unable to find user's home directory")
            raise Exception("Unable to find user's home directory")

        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        return dir_path

    @staticmethod
    def get_dcli_hidden_namespaces():
        """
        Helper function to populate DCLI_HIDDEN_NAMESPACES variable
        :rtype:  :class:`list` of :class:`dict`
        :return: array of dictionaries for the specified namespaces in env variable
        """
        hidden_namespaces = \
            os.environ.get('DCLI_HIDDEN_NAMESPACES', 'com vmware vapi, com vmware vmc model')
        hidden_namespaces = [item.rstrip().lstrip().replace(' ', '.') for item in hidden_namespaces.split(',')]
        for idx, item in enumerate(hidden_namespaces):
            split_item = item.rsplit('.', 1)
            hidden_namespaces[idx] = {'path': split_item[0],
                                      'name': split_item[1] if len(split_item) == 2 else ''}
        return hidden_namespaces

    @classmethod
    def get_interactive_parser_plus_options(cls):
        """ Initialize dcli interactive options """
        options = []

        # server options
        options.append(ArgumentInfo(name='+server',
                                    default=None,
                                    arg_action='store',
                                    description="Specify VAPI Server IP address/DNS name (default: '{}')".format(CliOptions.DCLI_SERVER)))
        options.append(ArgumentInfo(name='+vmc-server',
                                    const=CliOptions.DCLI_VMC_SERVER,
                                    arg_action='store_const',
                                    description="Switch to indicate connection to VMC server (default VMC URL: '{}')".format(CliOptions.DCLI_VMC_SERVER)))
        options.append(ArgumentInfo(name='+nsx-server',
                                    default=None,
                                    arg_action='store',
                                    description="Specify NSX Server IP address/DNS name (default: '{}')".format(CliOptions.DCLI_NSX_SERVER)))

        # ssl options
        options.append(ArgumentInfo(name='+skip-server-verification',
                                    mutex_group='ssl',
                                    default=CliOptions.SKIP_SERVER_VERIFICATION_DEFAULT_VALUE,
                                    arg_action='store_true',
                                    description="Skip server SSL verification process (default: {})".format(CliOptions.SKIP_SERVER_VERIFICATION_DEFAULT_VALUE)))
        options.append(ArgumentInfo(name='+cacert-file',
                                    mutex_group='ssl',
                                    default=CliOptions.CACERTFILE_DEFAULT_VALUE,
                                    arg_action='store',
                                    description="Specify the certificate authority certificates "
                                                "for validating SSL connections (format: PEM) (default: '{}')".format(CliOptions.CACERTFILE_DEFAULT_VALUE)))

        # credentials options
        options.append(ArgumentInfo(name='+username',
                                    arg_action='store',
                                    default=CliOptions.USERNAME_DEFAULT_VALUE,
                                    description="Specify the username for login (default: '{}')".format(CliOptions.USERNAME_DEFAULT_VALUE)))
        options.append(ArgumentInfo(name='+password',
                                    arg_action='store',
                                    default=CliOptions.PASSWORD_DEFAULT_VALUE,
                                    description="Specify password explicitly (default: {})".format(CliOptions.PASSWORD_DEFAULT_VALUE)))

        # filter option
        try:
            # have +filter option only if jmespath is importable
            import jmespath  # pylint: disable=W0612
            options.append(ArgumentInfo(name='+filter',
                                        arg_action='store',
                                        nargs='+',
                                        default=None,
                                        description='Provide JMESPath expression to filter command output. More info on JMESPath here: http://jmespath.org'))
        except ImportError:
            pass

        # loglevel, formatter, verbose, and show-unreleased-apis options
        options.append(ArgumentInfo(name='+formatter',
                                    arg_action='store',
                                    choices=CliOptions.FORMATTERS,
                                    default=CliOptions.FORMATTER_OPTION_DEFAULT_VALUE,
                                    description='Specify the formatter to use to format the command output'))
        options.append(ArgumentInfo(name='+verbose',
                                    arg_action='store_true',
                                    default=CliOptions.VERBOSE_DEFAULT_VALUE,
                                    description='Prints verbose output'))
        options.append(ArgumentInfo(name='+loglevel',
                                    arg_action='store',
                                    default=CliOptions.LOG_LEVEL_DEFAULT_VALUE,
                                    choices=CliOptions.LOGLEVELS,
                                    description="Specify the verbosity for log file. (default: '{}')".format(CliOptions.LOG_LEVEL_DEFAULT_VALUE)))
        # To show commands and namepaces of APIs that are under development
        options.append(ArgumentInfo(name='+show-unreleased-apis',
                                    arg_action='store_true',
                                    default=CliOptions.SHOW_UNRELEASED_APIS_DEFAULT_VALUE,
                                    description=argparse.SUPPRESS))

        # credstore options
        options.append(ArgumentInfo(name='+credstore-file',
                                    arg_action='store',
                                    default=CliOptions.CREDSTORE_FILE_OPTION_DEFAULT_VALUE,
                                    description="Specify the dcli credential store file (default: '{}')".format(CliOptions.CREDSTORE_FILE_OPTION_DEFAULT_VALUE)))
        options.append(ArgumentInfo(name='+credstore-add',
                                    mutex_group='credstore',
                                    arg_action='store_true',
                                    default=CliOptions.CREDSTORE_ADD_DEFAULT_VALUE,
                                    description='Store the login credentials in credential store without prompting'))
        options.append(ArgumentInfo(name='+credstore-list',
                                    mutex_group='credstore',
                                    arg_action='store_true',
                                    default=CliOptions.CREDSTORE_LIST_DEFAULT_VALUE,
                                    description='List the login credentials stored in credential store'))
        options.append(ArgumentInfo(name='+credstore-remove',
                                    mutex_group='credstore',
                                    arg_action='store_true',
                                    default=CliOptions.CREDSTORE_REMOVE_DEFAULT_VALUE,
                                    description='Remove login credentials from credential store'))
        options.append(ArgumentInfo(name='+session-manager',
                                    arg_action='store',
                                    description='Specify the session manager for credential store remove operation'))

        # configuration and more options
        options.append(ArgumentInfo(name='+configuration-file', arg_action='store',
                                    default=CliOptions.CONFIGURATION_FILE_OPTION_DEFAULT_VALUE,
                                    description="Specify the dcli configuration store file (default: '{}')".format(CliOptions.CONFIGURATION_FILE_OPTION_DEFAULT_VALUE)))
        options.append(ArgumentInfo(name='+more',
                                    arg_action='store_true',
                                    default=CliOptions.MORE_OPTION_DEFAULT_VALUE,
                                    description='Flag for page-wise output'))

        return options

    @classmethod
    def get_non_interactive_parser_plus_options(cls):
        """ Initialize dcli interactive options """
        options = []

        options.append(ArgumentInfo(name='+interactive',
                                    arg_action='store_true',
                                    default=CliOptions.INTERACTIVE_DEFAULT_VALUE,
                                    description='Open a CLI shell to invoke commands'))
        options.append(ArgumentInfo(name='+prompt',
                                    arg_action='store',
                                    default=CliOptions.PROMPT_DEFAULT_VALUE,
                                    description='Prompt for cli shell (default: {})'.format(CliOptions.PROMPT_DEFAULT_VALUE)))

        return options
