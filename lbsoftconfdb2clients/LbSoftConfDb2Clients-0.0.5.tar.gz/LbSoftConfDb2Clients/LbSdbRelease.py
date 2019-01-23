#!/usr/bin/env python
"""

Script to set the release request flag on a project/version

"""
import logging
import sys

from LbSoftConfDb2Clients.GenericClient import LbSoftConfDbBaseClient, \
    WRITE_ALLOWED_MODE


class LbSdbRelease(LbSoftConfDbBaseClient):
    """ Update information about a project / version """

    def __init__(self, *args, **kwargs):
        LbSoftConfDbBaseClient.__init__(
            self, server_mode=WRITE_ALLOWED_MODE, *args, **kwargs)

    def defineOpts(self):
        """ Script specific options """
        parser = self.parser
        parser.add_option("-r",
                          dest="remove",
                          action="store_true",
                          default=False,
                          help="Remove the link to the release node")

    def main(self):
        """ Main method for bootstrap and parsing the options.
        It invokes the appropriate method and  """
        self.log = logging.getLogger()

        opts = self.options
        args = self.args
        if opts.debug:
            self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.WARNING)
        if len(args) < 2:
            self.log.error("Not enough arguments")
            sys.exit(1)
        else:
            project = args[0].upper()
            version = args[1]

        # Connect to the ConfDB to update the platform
        if self.options.remove:
            self.mConfDB.unsetReleaseFlag(project, version)
        else:
            self.mConfDB.setReleaseFlag(project, version)


def main():
    sUsage = """%prog [-r] project
    Sets the project as an Application """
    s = LbSdbRelease(usage=sUsage)
    sys.exit(s.run())

if __name__ == '__main__':
    main()
