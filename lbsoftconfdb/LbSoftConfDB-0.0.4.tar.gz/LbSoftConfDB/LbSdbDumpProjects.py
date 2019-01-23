#!/usr/bin/env python
"""

Script to set the release request flag on a project/version

"""
import logging
import sys

from LbCommon.Script import Script
from LbSoftConfDB.SoftConfDB import SoftConfDB


class LbSdbDumpProjects(Script):
    """ Dump the information known about projects """

    def defineOpts(self):
        """ Script specific options """
        parser = self.parser
        parser.add_option("-d",
                          dest = "debug",
                          action = "store_true",
                          help = "Display debug output")
        parser.add_option("-o",
                          dest = "fileoutput",
                          action = "store",
                          default = None,
                          help = "Store result in file")

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

        # Connect to the ConfDB to update the platform
        self.mConfDB = SoftConfDB()

        props = self.mConfDB.dumpAllProjectProperties()
        import json, sys
        fp = sys.stdout
        if opts.fileoutput != None:
            fp = open(opts.fileoutput, "w")
        json.dump(props, fp)
        if opts.fileoutput != None:
            fp.close()


def main():
    sUsage = """%prog [-r] project
    Sets the project as an Application """
    s = LbSdbDumpProjects(usage=sUsage)
    sys.exit(s.run())


if __name__=='__main__':
    main()
