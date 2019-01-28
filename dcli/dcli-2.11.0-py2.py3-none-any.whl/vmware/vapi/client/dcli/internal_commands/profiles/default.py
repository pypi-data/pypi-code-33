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

import logging
from vmware.vapi.client.dcli.exceptions import handle_error
from vmware.vapi.client.dcli.internal_commands.configuration_utils import \
    (load_root, check_configuration_section, get_io_error_msg)
from vmware.vapi.client.dcli.internal_commands.profiles import \
    execute_profile_command

# todo: user logger more extensively
logger = logging.getLogger(__name__)


class Default(object):
    """
    Provides commands for handling dcli default profiles
    """
    def __init__(self, context):
        self.configuration_path = context.configuration_path

    def set(self, profile):
        """
        Change default profiles to specified one

        :type profile: :class:`str`
        :param profile: profiles name to change default one to
        """
        execute_profile_command(self.configuration_path, profile, _set_default)

    def get(self):
        """
        Show which is default profiles

        :rtype: :class:`str`
        :return: default profiles name
        """
        try:
            root = load_root(self.configuration_path)
            check_configuration_section(root, self.configuration_path)

            if 'default_profile' not in root['configuration']:
                raise Exception('default_profile section not found in '
                                'configuration file.')

            return root['configuration']['default_profile']

        except IOError as e:
            error_msg = get_io_error_msg(e, self.configuration_path)
            handle_error(error_msg, exception=e)
            raise Exception(error_msg)


def _set_default(configuration_path, root, name):
    """
    Change default profiles to specified one
    """
    check_configuration_section(root, configuration_path)

    if 'profiles' not in root['configuration']:
        raise Exception('Invalid configuration section in '
                        'configuration file.')

    if name not in root['configuration']['profiles']:
        raise Exception(
            "Profile '%s' not found in "
            "configuration file." % name)

    root['configuration']['default_profile'] = name
