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
import logging
import optparse
import os
import sys

from lbCVMFSscheduler.lbCVMFSexecutor.LbCVMFSManager import LbCVMFSManager


class LbCVMFSSchedulerOptionParser(optparse.OptionParser):
    """ Custom OptionParser to intercept the errors and rethrow
    them as LbCVMFSSchedulerExceptions """

    def error(self, msg):
        """
        Arguments parsing error message exception handler

        :param msg: the message of the exception
        :return: Raises LbCVMFSSchedulerException with the exception message
        """
        raise Exception("Error parsing arguments: " + str(msg))

    def exit(self, status=0, msg=None):
        """
        Arguments parsing error message exception handler

        :param status: the status of the application
        :param msg: the message of the exception
        :return: Raises LbCVMFSSchedulerException with the exception message
        """
        raise Exception("Error parsing arguments: " + str(msg))


class LbCVMFSSchedulerClient(object):
    """ Main class for the tool """

    MODE_EXECUTE = "execute"
    MODE_INTERACTIVE = "interactive"

    MODES = [MODE_EXECUTE, MODE_INTERACTIVE]

    def __init__(self, arguments=None, prog="LbCVMFSScheduler"):
        """ Common setup for both clients """
        self.log = logging.getLogger(__name__)
        self.arguments = arguments
        self.prog = prog
        self.dryrun = False
        self.queueName = 'commands'
        self.test = False
        parser = LbCVMFSSchedulerOptionParser(usage=usage(self.prog))
        parser.disable_interspersed_args()
        self.parser = parser

        parser.add_option('--dry-run',
                          dest="dryrun",
                          default=False,
                          action="store_true",
                          help="Will not execute the command")
        parser.add_option('--test',
                          dest="test",
                          default=False,
                          action="store_true",
                          help="Will add a random sleep to the command")
        parser.add_option('--queue_name',
                          dest="queue_name",
                          default='commands',
                          action="store",
                          help="Listen of different queue")

    def main(self):
        """ Main method for the ancestor:
        call parse and run in sequence

        :returns: the return code of the call
        """

        rc = 0
        try:
            opts, args = self.parser.parse_args(self.arguments)
            if opts.dryrun:
                self.dryrun = True
            if opts.test:
                self.test = True
            if opts.queue_name:
                self.queueName = opts.queue_name
            self.run(opts, args)
        except Exception as lie:
            print("ERROR: " + str(lie), file=sys.stderr)
            self.parser.print_help()
            rc = 1
        return rc

    def run(self, opts, args):
        """ Main method for the command

        :param opts: The option list
        :param args: The arguments list
        """
        # Parsing first argument to check the mode
        if len(args) > 0:
            cmd = args[0].lower()
            if cmd in LbCVMFSSchedulerClient.MODES:
                mode = cmd
            else:
                raise Exception("Unrecognized command: %s" % args)
        else:
            raise Exception("Argument list too short")
        manager = LbCVMFSManager(self.dryrun, self.test,
                                 queueName=self.queueName)
        # Now executing the command
        if mode == LbCVMFSSchedulerClient.MODE_EXECUTE:
            manager.start()
        elif mode == LbCVMFSSchedulerClient.MODE_INTERACTIVE:
            manager.interactive()
        else:
            self.log.error("Command not recognized: %s" % mode)


# Usage for the script
###############################################################################
def usage(cmd):
    """ Prints out how to use the script...

    :param cmd: the command executed
    """
    cmd = os.path.basename(cmd)
    return """\n%(cmd)s - runs CVMFS manager on Stratum-0""" % {"cmd": cmd}


def LbCVMFSScheduler(prog="LbCVMFSScheduler"):
    """
    Default caller for command line LbCVMFSScheduler client
    :param prog: the name of the executable
    """
    logging.basicConfig(format="%(levelname)-8s: %(message)s")
    logging.getLogger().setLevel(logging.WARNING)
    sys.exit(LbCVMFSSchedulerClient(prog=prog).main())

# Main just chooses the client and starts it
if __name__ == "__main__":
    LbCVMFSScheduler()
