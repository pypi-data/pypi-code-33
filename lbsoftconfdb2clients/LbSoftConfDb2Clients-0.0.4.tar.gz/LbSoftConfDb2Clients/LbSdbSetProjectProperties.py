#!/usr/bin/env python
"""

Script to set the properties about a project.

"""
import logging
import sys

from LbSoftConfDb2Clients.GenericClient import LbSoftConfDbBaseClient, \
    WRITE_ALLOWED_MODE


class LbSdbSetProjectProperties(LbSoftConfDbBaseClient):
    """ Update a property for a project:

    lb-sdb-setprojectprops <project name> <prop name> <value>

    To remove a specific property:

    lb-sdb-setprojectprops -r <project name> <prop name>

    To remove all properties:

    lb-sdb-setprojectprops -r <project name>

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

        service = None
        group = None
        name = None

        if opts.reset:
            if len(args) < 1:
                self.log.error(
                    "Not enough arguments: please specify the project name")
                sys.exit(1)
            else:
                project = args[0].upper()
                if len(args) == 1:
                    self.mConfDB.resetProjectProperties(project)
                    sys.exit(0)
                else:
                    propname = args[1]
                    self.mConfDB.setProjectProperty(project, propname, name)
                    sys.exit(0)

        if len(args) < 3:
            self.log.error(
                "Not enough arguments: please specify "
                "<project name> <prop name> <prop value>")
            sys.exit(1)
        else:
            project = args[0].upper()
            propname = args[1]
            propval = args[2]

        # Connect to the ConfDB to update the platform
        self.mConfDB.setProjectProperty(project, propname, propval)


def main():
    sUsage = """%prog project gitlabGroup gitlabName
    Sets a property on a given project
    """
    s = LbSdbSetProjectProperties(usage=sUsage)
    sys.exit(s.run())


if __name__ == '__main__':
    main()
