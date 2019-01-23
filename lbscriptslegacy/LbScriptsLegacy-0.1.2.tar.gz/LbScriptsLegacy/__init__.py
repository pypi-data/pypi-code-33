###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""

Compatibility layer for the old LbScripts commands
@author Ben Couturier <ben.couturier@cern.ch>

"""
from __future__ import print_function

import os
import sys

command_mappings = {'getNightlyRefs': 'lbn-get-new-refs',
                    'Lbglimpse': 'lb-glimpse'}


def sanitizename(n):
    """ Make sure we don't end up with an invalid method name 

    >>> sanitizename("toto-titi")
    'toto_titi'
    """
    return n.replace('-', '_')


def gen_wrapper(old_method, new_method):
    def wrapper():
        print("WARNING: %s is deprecated, please use %s instead" %
              (old_method, new_method), file=sys.stderr)
        return os.execvp(new_method, [new_method] + sys.argv[1:])
    return wrapper


for old_method, new_method in command_mappings.items():
    globals()[sanitizename(old_method)] = gen_wrapper(old_method, new_method)
del old_method, new_method


def get_entry_points(mappings=None):
    """ returns the list of entry points provided by this module,
    as specified in the map: command_mapping """
    mappings = command_mappings if mappings is None else mappings
    return ["{0}=LbScriptsLegacy:{1}".format(m, sanitizename(m)) for m in command_mappings]
