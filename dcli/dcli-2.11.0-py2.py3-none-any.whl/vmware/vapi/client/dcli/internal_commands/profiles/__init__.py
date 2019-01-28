"""
This module handles dcli profiles logic
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
from vmware.vapi.client.dcli.exceptions import handle_error
from vmware.vapi.client.dcli.credstore import AutoFileLock
from vmware.vapi.client.dcli.internal_commands.configuration_utils import \
    (load_root, check_configuration_section, get_io_error_msg)

CONFIG_SECTION = 'configuration'
#todo: user logger more extensively
logger = logging.getLogger(__name__)


class Profiles(object):
    """
    Provides commands for handling dcli profiles
    """
    def __init__(self, context):
        self.configuration_path = context.configuration_path

    def list(self):
        """
        Gives a list of all profiles in the configuration file

        :return: list of profiles
        :rtype: :class:`list` of :class:`str`
        """
        try:
            root = load_root(self.configuration_path)
            check_configuration_section(root, self.configuration_path)

            if 'profiles' not in root[CONFIG_SECTION]:
                raise Exception('Missing profiles section in '
                                'configuration file.')

            return list(root[CONFIG_SECTION]['profiles'].keys())

        except IOError as e:
            error_msg = get_io_error_msg(e, self.configuration_path)
            handle_error(error_msg, exception=e)
            raise Exception(error_msg)
        except ValueError:
            error_msg = 'Invalid configuration file %s' % \
                self.configuration_path
            raise Exception(error_msg)

    def add(self, name, origin_profile=None):
        """
        Adds new profiles to the configuration file

        :type name: :class:`str`
        :param name: name of the profiles
        :type origin_profile: :class:`str`
        :param origin_profile: optional name of a profiles to copy key-value pairs
        from
        """
        execute_profile_command(self.configuration_path, name, _add, origin_profile)

    def delete(self, profile):
        """
        Deletes specified profiles section from configuration file

        :type profile: :class:`str`
        :param profile: profiles name to delete
        """
        execute_profile_command(self.configuration_path, profile, _delete)

    def get(self, profile):
        """
        Show the profiles

        :rtype: :class:`str`
        :return: default profiles name
        """
        try:
            root = load_root(self.configuration_path)
            check_configuration_section(root, self.configuration_path)
            profiles = root[CONFIG_SECTION]['profiles']

            if profile not in profiles:
                error_msg = "Missing profiles '%s'" % profile
                raise Exception(error_msg)
            return profiles[profile]

        except IOError as e:
            error_msg = get_io_error_msg(e, self.configuration_path)
            handle_error(error_msg, exception=e)
            raise Exception(error_msg)
        except ValueError:
            error_msg = 'Invalid configuration file %s' % \
                self.configuration_path
            raise Exception(error_msg)


def _add(configuration_path, root, name):
    """
    Adds new profiles to the configuration file
    """
    check_configuration_section(root, configuration_path)
    root[CONFIG_SECTION].setdefault('profiles', {})
    root[CONFIG_SECTION]['profiles'][name] = {}


def _delete(configuration_path, root, name):
    """
    Deletes specified profiles section from configuration file
    """
    check_configuration_section(root, configuration_path)
    if 'profiles' not in root[CONFIG_SECTION]:
        return

    if name in root[CONFIG_SECTION]['profiles']:
        del root[CONFIG_SECTION]['profiles'][name]
    else:
        raise Exception("No profiles '%s' found." % name)


def _copy_from_profile(root, name, origin_profile):
    """
    Copies content of an origin profiles to a source profiles
    """
    if origin_profile not in root[CONFIG_SECTION]['profiles']:
        raise Exception("No '%s' profiles found" % origin_profile)

    root[CONFIG_SECTION]['profiles'][name] = \
        root[CONFIG_SECTION]['profiles'][origin_profile]


def execute_profile_command(configuration_path, name, action, origin_profile=None):
    """
    Executes a passed function, decorating it with common profiles-handling
    logic
    """
    try:
        umask_original = os.umask(0)
        # Only owner should have read-write permissions
        mode = stat.S_IRUSR | stat.S_IWUSR  # This is 0o600 in octal

        # Open and share lock configuration file
        with os.fdopen(os.open(configuration_path, os.O_RDWR | os.O_CREAT, mode), 'r+') as fd:
            with AutoFileLock(fd, AutoFileLock.SHARED) as locked_fd:
                try:
                    root = json.load(locked_fd)
                except ValueError as e:
                    error_msg = 'Invalid configuration file %s' % \
                                configuration_path
                    handle_error(error_msg, exception=e)
                    raise Exception(error_msg)

                action(configuration_path, root, name)
                if origin_profile is not None:
                    _copy_from_profile(root, name, origin_profile)

                locked_fd.seek(0)
                locked_fd.truncate()
                locked_fd.write(json.dumps(root, indent=4) + '\n')
    except IOError as e:
        msg = get_io_error_msg(e, configuration_path)
        handle_error(msg, exception=e)
        raise Exception(msg)
    finally:
        os.umask(umask_original)
