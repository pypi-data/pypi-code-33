from __future__ import print_function
import logging
import optparse
import os
import sys
import traceback
from lbdevmanager.CIManager import CIManager

# Class for known install exceptions
###############################################################################


class LbDevManagerException(Exception):
    """ Custom exception for lb-devmanager """

    def __init__(self, msg):
        """ Constructor for the exception """
        # super(LbInstallException, self).__init__(msg)
        Exception.__init__(self, msg)


# Classes and method for command line parsing
###############################################################################


class LbDevManagerOptionParser(optparse.OptionParser):
    """ Custom OptionParser to intercept the errors and rethrow
    them as LbDevManagerException """

    def error(self, msg):
        raise LbDevManagerException("Error parsing arguments: " + str(msg))

    def exit(self, status=0, msg=None):
        raise LbDevManagerException("Error parsing arguments: " + str(msg))


class LbDevManagerClient(object):
    """ Main class for the tool """

    MODE_VALIDATE = "validate"
    MODE_LIST = "generate-list"

    MODES = [MODE_VALIDATE, MODE_LIST]

    def __init__(self, arguments=None, prog="LbDevManager"):
        """ Common setup for both clients """
        self.log = logging.getLogger(__name__)
        self.prog = prog
        self.arguments = arguments

        self.debug = False
        self.root = None
        self.token = None
        self.repo = None
        self.tag = None
        self.branch = None
        parser = LbDevManagerOptionParser(usage=usage(self.prog))
        parser.disable_interspersed_args()
        parser.add_option('-d', '--debug',
                          dest="debug",
                          default=False,
                          action="store_true",
                          help="Show debug information")
        parser.add_option('--root',
                          dest="siteroot",
                          default=None,
                          action="store",
                          help="Specify MYSITEROOT on the command line")
        parser.add_option('-p', '--gitlab_token',
                          dest="gitlab_token",
                          default=None,
                          action="store",
                          help="Gitlab token")
        parser.add_option('--vhost',
                          dest="vhost",
                          default='/lhcb',
                          action="store",
                          help="RabbitMQ vhost")
        parser.add_option('-u', '--gitlab_user',
                          dest="gitlab_user",
                          default=None,
                          action="store",
                          help="Gitlab user")
        parser.add_option('-g', '--gitlab_repo',
                          dest="gitlab_repo",
                          default='/lhcb-core/cvmfsdev-sw.git',
                          action="store",
                          help="Gitlab repo")
        parser.add_option('-b', '--gitlab_branch',
                          dest="gitlab_branch",
                          default='install_files',
                          action="store",
                          help="Gitlab branch")
        self.parser = parser

    def main(self):
        """ Main method for the ancestor:
        call parse and run in sequence """
        rc = 0
        try:
            opts, args = self.parser.parse_args(self.arguments)
            # Checking the siteroot and URL
            # to choose the siteroot
            if opts.siteroot is not None:
                self.siteroot = opts.siteroot
                os.environ['MYSITEROOT'] = opts.siteroot
            else:
                self.siteroot = os.environ.get('MYSITEROOT', None)

            if opts.debug:
                logging.basicConfig(format="%(levelname)-8s: "
                                    "%(funcName)-25s - %(message)s")
                logging.getLogger().setLevel(logging.DEBUG)
            self.token = opts.gitlab_token
            self.repo = opts.gitlab_repo
            self.username = opts.gitlab_user
            self.branch = opts.gitlab_branch
            self.vhost = opts.vhost
            # Checking if we should do a dry-run
            rc = self.run(opts, args)
        except LbDevManagerException as lie:
            print("ERROR: " + str(lie), file=sys.stderr)
            self.parser.print_help()
            rc = 1
        except:
            print("Exception in lb-devmanager:", file=sys.stderr)
            print('-'*60, file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            print('-'*60, file=sys.stderr)
            rc = 1
        return rc

    def run(self, opts, args):
        """ Main method for the command """

        # Parsing first argument to check the mode
        if len(args) > 0:
            cmd = args[0].lower()
            if cmd in LbDevManagerClient.MODES:
                mode = cmd
            else:
                raise LbDevManagerException("Unrecognized command: %s" % args)
        else:
            raise LbDevManagerException("Argument list too short")

        # Now executing the command
        if mode == LbDevManagerClient.MODE_VALIDATE:
            u = CIManager(conffile=args[1])
            if u.validateYAML():
                return 0
            return 1
        elif mode == LbDevManagerClient.MODE_LIST:

            if self.token is None:
                raise LbDevManagerException("Please specify Gitlab token -  "
                                            "use the --gitlab_token option")
            if self.username is None:
                raise LbDevManagerException("Please specify Gitlab user "
                                            "- use the --gitlab_user option")
            if self.siteroot is None:
                raise LbDevManagerException("Please specify MYSITEROOT in "
                                            "the environment or use the "
                                            "--root option")
            if len(args) > 1:
                conffile = args[1]
            else:
                conffile = None

            u = CIManager(siteroot=self.siteroot,
                          conffile=conffile,
                          repo=self.repo,
                          token=self.token,
                          branch=self.branch,
                          username=self.username,
                          vhost=self.vhost)
            missing_results = u.check()
            if len(missing_results):
                error_msg = '\n'.join(missing_results)
                raise Exception("There are missing packages:\n"
                                "%s" % error_msg)
            return 0
        else:
            self.log.error("Command not recognized: %s" % mode)


# Usage for the script
###############################################################################
def usage(cmd):
    """ Prints out how to use the script... """
    cmd = os.path.basename(cmd)
    return """\n%(cmd)s -  installes the software from yaml description in MYSITEROOT directory'

The environment variable MYSITEROOT MUST be set for this script to work.

It can be used in the following ways:

%(cmd)s validate <config file>
Validates the yaml config file against the used schema

%(cmd)s [-o outputfilename] generate-list <config file>
Generates the list of file to install

%(cmd)s --root=<root directory for the installation area> install
Install the lastes packages added to the git.

""" % {"cmd": cmd}


def LbDevManager(prog="lbdevcheck"):
    logging.basicConfig(format="%(levelname)-8s: %(message)s")
    logging.getLogger().setLevel(logging.ERROR)
    sys.exit(LbDevManagerClient(prog=prog).main())

# Main just chooses the client and starts it
if __name__ == "__main__":
    LbDevManager()