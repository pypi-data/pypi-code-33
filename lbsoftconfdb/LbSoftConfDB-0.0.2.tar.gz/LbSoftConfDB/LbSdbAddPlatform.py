#!/usr/bin/env python
"""
A script to add a platform to a project/version

"""
import logging
import sys

from LbCommon.Script import Script
from LbSoftConfDB.SoftConfDB import SoftConfDB

class LbSdbAddPlatform(Script):
    """ Script to add platforms to a project in the Software
    Configuration DB. Use:
    LbSdbAddPlatform project version platform
    """

    def defineOpts(self):
        """ Script specific options """
        parser = self.parser
        parser.add_option("-d",
                          dest = "debug",
                          action = "store_true",
                          help = "Display debug output")
        parser.add_option("-r", "--remove",
                          dest = "remove",
                          action = "store_true",
                          default=False,
                          help = "Remove platform instead of adding")
        parser.add_option("--release",
                          dest = "release",
                          action = "store_true",
                          default=False,
                          help = "Change the REQUESTED_PLATFORM instead of the PLATFORM link")

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
        if len(args) < 3 :
            self.log.error("Not enough arguments")
            sys.exit(1)
        else :
            project   = args[0].upper()
            version   = args[1]
            platforms  = args[2:]

            # Connect to the ConfDB to update the platform
            self.mConfDB = SoftConfDB()

            reltype = "PLATFORM"
            if opts.release:
                reltype = "REQUESTED_PLATFORM"

            for platform in platforms:
                if opts.remove:
                    self.mConfDB.delPVPlatform(project, version, platform, reltype)
                else:
                    self.mConfDB.addPVPlatform(project, version, platform, reltype)

if __name__=='__main__':
    sUsage = """%prog project version platform [platform...]  """
    s = LbSdbAddPlatform(usage=sUsage)
    sys.exit(s.run())


