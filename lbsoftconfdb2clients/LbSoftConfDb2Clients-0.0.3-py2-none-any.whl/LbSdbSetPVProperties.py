#!/usr/bin/env python
"""

Script to set the properties about a project.

"""
import logging
import sys

from LbSoftConfDb2Clients.GenericClient import LbSoftConfDbBaseClient, \
    WRITE_ALLOWED_MODE


class LbSdbSetPVProperties(LbSoftConfDbBaseClient):
    """ Update a property for a project:

    lb-sdb-setpvprops <project name> <version> <prop name> <value>

    To remove a specific property:

    lb-sdb-setpvprops -r <project name>  <version> <prop name>

    To remove all properties:

    lb-sdb-setpvprops -r <project name>  <version>

    """

    def __init__(self, *args, **kwargs):
        LbSoftConfDbBaseClient.__init__(
            self, server_mode=WRITE_ALLOWED_MODE, *args, **kwargs)

    def defineOpts(self):
        """ Script specific options """
        parser = self.parser
        parser.add_option("-r",
                          dest="reset",
                          action="store_true",
                          default=False,
                          help="Reset the properties")

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

        if opts.reset:
            if len(args) < 2 :
                self.log.error("Not enough arguments: "
                               "please specify the project name version")
                sys.exit(1)
            else:
                project = args[0].upper()
                version = args[1]

                if len(args) == 2:
                    self.mConfDB.resetPVProperties(project, version)
                    sys.exit(0)
                else:
                    propname = args[2]
                    self.mConfDB.setPVProperty(project, version, propname, None)
                    sys.exit(0)

        if len(args) < 4 :
            self.log.error("Not enough arguments: please specify "
                           "<project name> <version> <prop name> <prop value>")
            sys.exit(1)
        else:
            project = args[0].upper()
            version = args[1]
            propname = args[2]
            propval = args[3]

        self.mConfDB.setPVProperty(project, version, propname, propval)


def main():
    sUsage = """%prog project version propname propval
    Sets a property on a given project/version
    """
    s = LbSdbSetPVProperties(usage=sUsage)
    sys.exit(s.run())


if __name__ == '__main__':
    main()
