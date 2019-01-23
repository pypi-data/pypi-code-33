#!/usr/bin/env python

###############################################################################
# (c) Copyright 2016 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Command line client that interfaces to the Installer class

:author: Stefan-Gabriel CHITIC
'''
from __future__ import print_function
import sys

from lbCVMFSTools.TaskHandlers.SampleTask.SampleTask \
    import SampleTask
from lbCVMFSTools.TransactionHandlers.DefaultTransactionHandler. \
    DefaultTransactionHandler import DefaultTransactionHandler
from lbCVMFSTools.GenericClient import GenericClient


class SampleClient(GenericClient, object):
    """ Main class for the tool """

    def __init__(self, prog, help):
        """ Common setup for both clients """
        super(SampleClient, self).__init__(
            prog=prog, help=help)

    def defineTaskHandler(self, args, opts):
        return SampleTask(dry_run=opts.dry_run)

    def defineTransitionHandler(self, args, opts):
        return DefaultTransactionHandler(dry_run=opts.dry_run)

    def configureClient(self, args, opts):
        pass


def Sample(prog="Sample", help="Sample"):
    """
    Default caller for command line CVMFSDevChecker client
    :param configType: the configuration used
    :param prog: the name of the executable
    """
    sys.exit(SampleClient(prog=prog, help=help).main())

# Main just chooses the client and starts it
if __name__ == "__main__":
    Sample()
