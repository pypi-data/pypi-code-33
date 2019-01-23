#!/usr/bin/env python
"""

Script to set the release request flag on a project/version

"""
import logging
import json
import sys
from LbSoftConfDb2Clients.GenericClient import LbSoftConfDbBaseClient, \
    WRITE_ALLOWED_MODE


class LbSdbDumpProjects(LbSoftConfDbBaseClient):
    """ Dump the information known about projects """

    def __init__(self, *args, **kwargs):
        LbSoftConfDbBaseClient.__init__(
            self, server_mode=WRITE_ALLOWED_MODE, *args, **kwargs)

    def defineOpts(self):
        """ Script specific options """
        parser = self.parser
        parser.add_option("-o",
                          dest="fileoutput",
                          action="store",
                          default=None,
                          help="Store result in file")

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

        props = self.mConfDB.dumpAllProjectProperties()
        fp = sys.stdout
        if opts.fileoutput is not None:
            fp = open(opts.fileoutput, "w")
        json.dump(props, fp)
        if opts.fileoutput is not None:
            fp.close()


def main():
    sUsage = """%prog [-r] project
    Sets the project as an Application """
    s = LbSdbDumpProjects(usage=sUsage)
    sys.exit(s.run())


if __name__ == '__main__':
    main()
