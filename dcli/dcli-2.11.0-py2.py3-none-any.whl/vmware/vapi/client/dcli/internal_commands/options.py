"""
This module handles dcli default options logic
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright (c) 2017-2018 VMware, Inc.  All rights reserved. '
__license__ = 'SPDX-License-Identifier: MIT'
__docformat__ = 'epytext en'

import json
import logging
import os
import stat
import six
from vmware.vapi.client.dcli.exceptions import handle_error
from vmware.vapi.client.dcli.credstore import AutoFileLock
from vmware.vapi.client.dcli.internal_commands.configuration_utils import \
    (load_root, check_configuration_section, load_profile, get_server_entry,
     get_module_entry, get_io_error_msg)
from vmware.vapi.client.dcli.util import CliHelper
OPTIONS_CONFIG_SECTION = 'default_options'

# todo: user logger more extensively
logger = logging.getLogger(__name__)


class Options(object):
    """
    Provides commands for handling default options in dcli
    """
    def __init__(self, dcli_context):
        self.dcli_context = dcli_context
        self.configuration_path = dcli_context.configuration_path
        self.server = dcli_context.server
        self.server_type = dcli_context.server_type
        self.root = {}

        self.load_configuration_file()

    def load_configuration_file(self):
        """
        Reads configuration file and saves content in json object
        """
        self.root = load_root(self.configuration_path)

    def write_configuration_file(self):
        """
        Writes json object in memory to the file system
        """
        try:
            umask_original = os.umask(0)
            # Only owner should have read-write permissions
            mode = stat.S_IRUSR | stat.S_IWUSR  # This is 0o600 in octal

            # Open and share lock configuration file
            with os.fdopen(os.open(self.configuration_path, os.O_RDWR | os.O_CREAT, mode), 'r+') as fd:
                with AutoFileLock(fd, AutoFileLock.SHARED) as locked_fd:
                    locked_fd.seek(0)
                    locked_fd.truncate()
                    locked_fd.write(json.dumps(self.root, indent=4) + '\n')
        except IOError as e:
            msg = get_io_error_msg(e, self.configuration_path)
            handle_error(msg, exception=e)
        finally:
            os.umask(umask_original)

    def list(self, all_profiles=False):
        """
        Gives overview of all default options in current profiles or across
        all of them

        :type all_profiles: :class:`bool`
        :param all_profiles: determines whether to list all profiles default
        options or default one only
        :rtype: :class:`dict`
        :return: returns dict of default options for default profiles or
        all profiles if specified through :param: all_profiles
        """
        if not self.root:
            return self.root
        result = {}

        check_configuration_section(self.root, self.configuration_path)
        configuration = self.root['configuration']

        if not configuration.get('default_profile'):
            error_msg = 'Default profile missing or ' \
                        'empty in configuration file ' \
                        '%s' % self.configuration_path
            handle_error(error_msg)
            raise Exception(error_msg)

        default_profile = configuration['default_profile']

        if 'profiles' not in configuration:
            logger.warning('No profiles in configuration file')
            return None

        for profile in six.iterkeys(configuration['profiles']):
            if not all_profiles and profile != default_profile:
                continue

            profile_entry = configuration['profiles'][profile]
            result[profile] = load_profile(profile_entry)

        return result

    def set(self, option, value, module=None, server=None,
            profile=None):
        """
        Sets a default option

        :type module: :class:`str`
        :param module: module name
        :type option: :class:`str`
        :param option: option name
        :type value: :class:`object`
        :param value: value
        :type server: :class:`str`
        :param server: optional server URL. If not specified uses server URL
        given in __init__
        :type profile: :class:`str`
        :param profile: optional profiles name. If not specified uses default
        one
        """

        if 'configuration' not in self.root:
            self.root['configuration'] = {
                'default_profile': 'default',
                'profiles': {
                    'default': {}
                },
                'version': '1.0'
            }
        configuration = self.root['configuration']

        try:
            profiles = configuration['profiles']

            if profile:
                profiles.setdefault(profile, {})
            profile_entry = \
                profiles[configuration['default_profile']] \
                if profile is None else profiles[profile]

            if module is None:
                module = CliHelper.get_module_name(self.server_type)
            profile_entry.setdefault(module, {})
            module_entry = profile_entry[module]

            if module != 'dcli':
                server = server if server is not None else self.server
                if server is None:
                    error_msg = "Server section for the '%s' option is "\
                                "set to '%s'" % (option, None)
                    raise Exception(error_msg)

                module_entry.setdefault(server, {})
                server_entry = module_entry[server]
            else:
                server_entry = module_entry

            server_entry.setdefault(OPTIONS_CONFIG_SECTION, {})
            server_entry[OPTIONS_CONFIG_SECTION][option] = value
            self.write_configuration_file()
        except KeyError:
            raise Exception('Invalid configuration section in '
                            'configuration file.')

    def get(self, option, module=None, server=None, profile=None):
        """
        Gets value for specified option name. Throws error if one does not
        exist

        :type module: :class:`str`
        :param module: module name
        :type option: :class:`str`
        :param option: option name
        :type server: :class:`str`
        :param server: optional server URL. If not specified uses server URL
        given in __init__
        :type profile: :class:`str`
        :param profile: optional profiles name. If not specified uses default
        one
        :rtype: :class:`str`
        :return: value for specified default option
        """
        check_configuration_section(self.root, self.configuration_path)

        try:
            profile = profile if profile else \
                self.root['configuration']['default_profile']
            profiles = self.root['configuration']['profiles']
            if module is None:
                module = CliHelper.get_module_name(self.server_type)
            module_entry = get_module_entry(profiles, profile, module)
            server_entry = get_server_entry(server, self.server, module_entry, module)
            section_entry = server_entry[OPTIONS_CONFIG_SECTION]
            section_entry = server_entry[OPTIONS_CONFIG_SECTION]
            if option not in section_entry:
                error_msg = \
                    "No saved option '%s' found in module '%s'" % \
                    (option, module)
                raise Exception(error_msg)

            return section_entry[option]

        except KeyError:
            raise Exception('Invalid configuration section in '
                            'configuration file.')

    def try_get(self, option, module=None, server=None, profile=None):
        """
        Gets value for specified default option name. Returns None if one not
        found.

        :type module: :class:`str`
        :param module: module name
        :type option: :class:`str`
        :param option: option name
        :type server: :class:`str`
        :param server: optional server URL. If not specified uses server URL
        given in __init__
        :type profile: :class:`str`
        :param profile: optional profiles name. If not specified uses default
        one
        :rtype: :class:`str`
        :return: value for specified default option
        """
        try:
            return self.get(option, module=module, server=server, profile=profile)
        except Exception:
            if module != 'dcli':
                return self.try_get(option, module='dcli', server=server, profile=profile)
            return None

    def delete(self, option, module=None, server=None, profile=None):
        """
        Deletes default option

        :type module: :class:`str`
        :param module: module name
        :type option: :class:`str`
        :param option: option name
        :type server: :class:`str`
        :param server: optional server URL. If not specified uses server URL
        given in __init__
        :type profile: :class:`str`
        :param profile: optional profiles name. If not specified uses default
        one
        """
        check_configuration_section(self.root, self.configuration_path)

        try:
            profile = profile if profile else \
                self.root['configuration']['default_profile']
            profiles = self.root['configuration']['profiles']
            if module is None:
                module = CliHelper.get_module_name(self.server_type)
            module_entry = get_module_entry(profiles, profile, module)
            server_entry = get_server_entry(server, self.server, module_entry, module)

            if option in server_entry[OPTIONS_CONFIG_SECTION]:
                del server_entry[OPTIONS_CONFIG_SECTION][option]
            else:
                error_msg = \
                    "Missing option '%s' in module '%s' can not be deleted" % \
                    (option, module)
                handle_error(error_msg)
                raise Exception(error_msg)

            self.write_configuration_file()
        except KeyError:
            raise Exception('Invalid configuration section in '
                            'configuration file.')
