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
import os
import six
from vmware.vapi.client.dcli.exceptions import extract_error_msg
from vmware.vapi.client.dcli.credstore import AutoFileLock

OPTIONS_CONFIG_SECTION = 'default_options'
CONFIG_SECTION = 'configuration'


def load_root(configuration_path):
    """
    Loads the json content of a configuration file

    :type configuration_path: :class:`str`
    :param configuration_path: path to the configuration file
    :return: json str containing the content of the
    provided configuration file
    :raises ValueError: raises value error if configuration
    file is invalid
    """
    root = {}
    try:
        with open(configuration_path, 'r+') as fd:
            with AutoFileLock(fd, AutoFileLock.SHARED) as locked_fd:
                if os.path.getsize(configuration_path) > 0:
                    root = json.load(locked_fd)
    except IOError:
        # likely non-existing file
        # leave root empty ready to be fille or
        # return empty list for list operation
        pass
    except ValueError as e:
        erro_msg = 'Invalid configuration file %s' % \
            configuration_path
        new_error = ValueError(erro_msg)
        new_error.inner_exception = e
        raise new_error

    return root


def check_configuration_section(root, configuration_path):
    """
    Validates configuration section

    :type configuration_path: :class:`str`
    :param configuration_path: path to the configuration file
    :type root: :class:`str`
    :param root: the content of the current configuration file
    :raises Exception: raises exception if configuration json has
    no configuration section
    """
    if CONFIG_SECTION not in root:
        error_msg = "No '%s' section found in " \
                    'configuration file %s' % \
                    (CONFIG_SECTION, configuration_path)
        raise Exception(error_msg)


def get_server_entry(server, default_server, module_entry, module):
    """
    Gets the server entry from a given module entry. Gets server from
    __init__ if no server value was provided.

    :type server: :class:`str`
    :param server: the server
    :type module_entry: :class:`str`
    :param module_entry: configuration of the module
    :type module: :class:`str`
    :param module: module name
    :return: the server entry
    :raises Exception: raises exception if server is missing
    """
    if module == 'dcli':
        return module_entry

    server = server if server is not None else default_server
    if server not in module_entry:
        error_msg = \
            "Missing server '%s' in module '%s'" % \
            (server, module)
        raise Exception(error_msg)

    if OPTIONS_CONFIG_SECTION not in module_entry[server]:
        error_msg = \
            "Missing section '%s' for server '%s'" % \
            (OPTIONS_CONFIG_SECTION, server)
        raise Exception(error_msg)
    return module_entry[server]


def get_module_entry(profiles, profile, module):
    """
    Gets the module entry from a given profile

    :type profiles: :class:`str`
    :param profiles: all retrieved profiles
    :type profile: :class:`str`
    :param profile: the current profile
    :type module: :class:`str`
    :param module: the current module
    :return: the module entry from the profile
    :raises Exception: raises exception if profile or module is missing
    """
    if profile not in profiles:
        error_msg = "Missing profile '%s'" % profile
        raise Exception(error_msg)
    profile_section = profiles[profile]

    if module not in profile_section:
        error_msg = \
            "Missing module '%s' in profile '%s'" % \
            (module, profile)
        raise Exception(error_msg)
    return profile_section[module]


def load_profile(profile_entry):
    """
    Loads the result profile from a given profile entry

    :type profile_entry: :class:`str`
    :param profile_entry: the entry for the current profile
    :return: json str containing the profile
    """
    result = {}
    for module in six.iterkeys(profile_entry):
        result[module] = {}
        module_entry = profile_entry[module]
        for server in six.iterkeys(module_entry):
            if module == 'dcli':
                result[module][OPTIONS_CONFIG_SECTION] = \
                    module_entry[OPTIONS_CONFIG_SECTION]
            else:
                result[module][server] = {}
                server_entry = module_entry[server]
                server_entry.setdefault(OPTIONS_CONFIG_SECTION, {})
                result[module][server][OPTIONS_CONFIG_SECTION] = \
                    server_entry[OPTIONS_CONFIG_SECTION]
    return result


def get_io_error_msg(e, configuration_path):
    """
    Builds the error message for a common IOError,
    which occurs when configuration file can not be opened

    :type e: :class:`IOError`
    :param e: the IOError which occured
    :return: error_msg string
    """
    msg = extract_error_msg(e)
    error_msg = 'Unable to open configuration file %s. ' \
                % configuration_path
    if msg:
        error_msg = '%s Message: %s' % (error_msg, msg)
    return error_msg
