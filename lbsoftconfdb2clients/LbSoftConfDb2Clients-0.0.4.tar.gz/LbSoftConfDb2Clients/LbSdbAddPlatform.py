#!/usr/bin/env python
"""
A script to add a platform to a project/version

"""
import sys

from LbSoftConfDb2Clients.GenericClient import LbSoftConfDbBaseClient, \
    WRITE_ALLOWED_MODE


class LbSdbAddPlatform(LbSoftConfDbBaseClient):
    """ Script to add platforms to a project in the Software
    Configuration DB. Use:
    LbSdbAddPlatform project version platform
    """

    def __init__(self, *args, **kwargs):
        LbSoftConfDbBaseClient.__init__(
            self, server_mode=WRITE_ALLOWED_MODE, *args, **kwargs)

    def defineOpts(self):
        """ Script specific options """
        parser = self.parser

        parser.add_option("-r", "--remove",
                          dest="remove",
                          action="store_true",
                          default=False,
                          help="Remove platform instead of adding")
        parser.add_option("--release",
                          dest="release",
                          action="store_true",
                          default=False,
                          help="Change the REQUESTED_PLATFORM instead of "
                               "the PLATFORM link")

    def main(self):
        """ Main method for bootstrap and parsing the options.
        It invokes the appropriate method and  """
        opts = self.options
        args = self.args

        if len(args) < 3:
            self.log.error("Not enough arguments")
            sys.exit(1)
        else:
            project = args[0].upper()
            version = args[1]
            platforms = args[2:]

            reltype = "PLATFORM"
            if opts.release:
                reltype = "REQUESTED_PLATFORM"

            for platform in platforms:
                if opts.remove:
                    self.mConfDB.delPVPlatform(project, version, platform,
                                               reltype)
                else:
                    self.mConfDB.addPVPlatform(project, version, platform,
                                               reltype)


def main():
    sUsage = """%prog project version platform [platform...]  """
    s = LbSdbAddPlatform(usage=sUsage)
    sys.exit(s.run())

if __name__ == '__main__':
    main()
