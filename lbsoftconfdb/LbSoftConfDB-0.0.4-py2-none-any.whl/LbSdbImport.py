#!/usr/bin/env python
"""
A script to import a project into the Software Configuration DB

"""
import logging
import sys

from LbCommon.Script import Script
from LbSoftConfDB.AppImporter import AppImporter
from LbSoftConfDB.SoftConfDB import SoftConfDB

class LbSdbImportProject(Script):
    """ Main scripts class for looking up dependencies.
    It inherits from """


    def defineOpts(self):
        """ Script specific options """
        parser = self.parser
        parser.add_option("--norelease",
                          dest = "norelease",
                          default = False,
                          action = "store_true",
                          help = "Disable automatic release of projects not yet in DB")
        parser.add_option("--sourceuri",
                          dest = "sourceuri",
                          default = None,
                          action = "store",
                          help = "Specify the location of the project")
        parser.add_option("--buildtool",
                          dest = "buildtool",
                          default = None,
                          action = "store",
                          type = "choice",
                          choices = [ "cmt", "cmake"],
                          help = "Specify the build tool to use")
        parser.add_option("--platforms",
                          dest = "platforms",
                          default = None,
                          action = "store",
                          help = "Specify the platforms to release, as a comma separated list")

    def main(self):
        """ Main method for bootstrap and parsing the options.
        It invokes the appropriate method and  """
        self.log = logging.getLogger()
        opts = self.options
        args = self.args

        if len(args) < 2 :
            self.log.error("Not enough arguments")
            sys.exit(1)
        else :
            project   = args[0].upper()
            version   = args[1]

            # Creating the object to import dependencies
            platform_list = []
            if opts.platforms:
                platform_list = [ p.strip() for p in opts.platforms.split(",")]
            self.mAppImporter = AppImporter(not opts.norelease, platform_list)

            self.log.warning("Checking SoftConfDB for %s %s" % (project, version))
            self.mAppImporter.processProjectVersion(project,
                                                    version,
                                                    sourceuri=opts.sourceuri)

            # Now setting the build tools as requested
            if opts.buildtool != None:
                cdb = SoftConfDB()
                cdb.setBuildTool(project,
                                 version,
                                 opts.buildtool)

def main():
    sUsage = """%prog [-n] project version  """
    s = LbSdbImportProject(usage=sUsage)
    sys.exit(s.run())

if __name__=='__main__':
    main()
