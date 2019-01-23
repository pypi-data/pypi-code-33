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

from lbCVMFSscheduler.lbscheduler.LbSchedulerExecuter import RPCSchedulerExecutor


class LbSchedulerClientOptionParser(optparse.OptionParser):
    """ Custom OptionParser to intercept the errors and rethrow
    them as LbSchedulerClientExceptions """

    def error(self, msg):
        """
        Arguments parsing error message exception handler

        :param msg: the message of the exception
        :return: Raises LbSchedulerClientException with the exception message
        """
        raise Exception("Error parsing arguments: " + str(msg))

    def exit(self, status=0, msg=None):
        """
        Arguments parsing error message exception handler

        :param status: the status of the application
        :param msg: the message of the exception
        :return: Raises LbSchedulerClientException with the exception message
        """
        raise Exception("Error parsing arguments: " + str(msg))


class LbSchedulerClientClient(object):
    """ Main class for the tool """

    def __init__(self, arguments=None, prog="LbSchedulerClient"):
        """ Common setup for both clients """
        self.log = logging.getLogger(__name__)
        self.arguments = arguments
        self.prog = prog
        self.queue = None
        self.vhost = None
        self.exchange = None
        parser = LbSchedulerClientOptionParser(usage=usage(self.prog))
        parser.disable_interspersed_args()
        self.parser = parser

        parser.add_option('--queue',
                          dest="queue",
                          default='CronJobs',
                          action="store",
                          help="Publish on different queue")
        parser.add_option('--vhost',
                          dest="vhost",
                          default='/lhcb',
                          action="store",
                          help="Publish using a different vhost")
        parser.add_option('--exchange',
                          dest="exchange",
                          default='topic.cvmfs',
                          action="store",
                          help="Publish using a different exchange")

    def main(self):
        """ Main method for the ancestor:
        call parse and run in sequence

        :returns: the return code of the call
        """
        rc = 0
        try:
            opts, args = self.parser.parse_args(self.arguments)
            rc = self.run(opts, args)
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
        if len(args) > 1:
            delay = args[0]
            cmd = args[1]
            arguments = [x for x in args[2:]]
            self.queue = opts.queue
            self.vhost = opts.vhost
            self.exchange = opts.exchange
            # Initializing the installer
            executor = RPCSchedulerExecutor(self.queue, self.vhost,
                                            self.exchange, delay,
                                            cmd, args=arguments)
            return executor.returnCode
        else:
            raise Exception("Argument list too short")


# Usage for the script
###############################################################################
def usage(cmd):
    """ Prints out how to use the script...

    :param cmd: the command executed
    """
    cmd = os.path.basename(cmd)
    return """\n%(cmd)s <delay> <command> [<arguments>] - runs CVMFS client for
               Stratum-0""" % {"cmd": cmd}


def LbSchedulerClient(prog="LbSchedulerClient"):
    """
    Default caller for command line LbSchedulerClient client
    :param prog: the name of the executable
    """
    logging.basicConfig(format="%(levelname)-8s: %(message)s")
    logging.getLogger().setLevel(logging.WARNING)
    sys.exit(LbSchedulerClientClient(prog=prog).main())

# Main just chooses the client and starts it
if __name__ == "__main__":
    LbSchedulerClient()
