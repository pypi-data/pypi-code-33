#!/usr/bin/env python
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

Tools that scans an install area for installed LHCb projects and creates
a lbinstall local DB with the equivallent RPMs installed.

This is a tool written for the purpose of migrating existing install areas.

'''
import os
import sys
import tempfile
import logging

from lbinstall.extra.Utils import InstallAreaTool, lookupRPMsForProject
from lbinstall.Installer import Installer


def importInstallAreaPackages(pattern=None, siteroot=None):

    # Preparing the new install area
    if siteroot is None:
        siteroot = tempfile.mkdtemp(prefix="siteroot")
    installer = Installer(siteroot)

    # Looking up the packages to install from the old install area
    oldarea = InstallAreaTool()
    oldprojs = oldarea.getProjectList()
    # oldprojs = list(oldprojs)[:10] # for quicker test

    toinstall = set()
    for (name, version, platforms) in oldprojs:
        logging.debug("Processing %s %s %s" % (name, version, str(platforms)))
        packages = lookupRPMsForProject(installer, name, version, platforms)
        toinstall |= packages

    pname = [p.rpmName() for p in toinstall]
    with open("packages_to_install.json", "w") as f:
        import json
        json.dump(pname, f)

if __name__ == "__main__":
    pattern = None
    if len(sys.argv) > 1:
        pattern = (sys.argv[1])
    logging.basicConfig(level=logging.INFO)
    # name, version, platforms = ('GAUDI', 'v24r2', ['x86_64-slc5-gcc46-dbg',
    # 'x86_64-slc5-gcc46-opt', 'x86_64-slc6-gcc46-dbg', 'x86_64-slc6-gcc46-opt'
    # , 'x86_64-slc6-gcc48-dbg', 'x86_64-slc6-gcc48-opt'])
    exit(importInstallAreaPackages(pattern, siteroot=os.environ["MYSITEROOT"]))
