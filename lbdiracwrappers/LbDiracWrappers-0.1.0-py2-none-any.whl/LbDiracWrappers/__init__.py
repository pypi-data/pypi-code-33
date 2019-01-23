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

Wrappers for some DIRAC commands

@author Joel Closier <joel.closier@cern.ch>
@author Ben Couturier <ben.couturier@cern.ch>

"""

import os
import sys


def call_dirac(command):
    """ Invoke the command in the LHCbDirac environment """
    prefix = ["lb-run", "-c", "best", "LHCbDirac/prod"]
    full_command = prefix + command
    # using execvp here as we can get rid of the current process and replace it by the lb-run image.
    # execvp uses the path to locate lb-run (as opposed to execv which requires an absolute path)
    return os.execvp(full_command[0], full_command)


def lhcb_proxy_init():
    """ Invoke lhcb-proxy-init in the correct environment """
    # We just ignore the first argument...
    return call_dirac(["lhcb-proxy-init"] + sys.argv[1:])


def lhcb_proxy_info():
    """ Invoke lhcb-proxy-init in the correct environment """
    # We just ignore the first argument...
    return call_dirac(["dirac-proxy-info"] + sys.argv[1:])
