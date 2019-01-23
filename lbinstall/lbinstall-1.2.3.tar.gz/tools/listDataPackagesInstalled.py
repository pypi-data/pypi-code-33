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

from lbinstall.extra.Utils import InstallAreaTool
from lbinstall.Installer import Installer


def listDataPackages(pattern=None, siteroot=None):

    # Preparing the new install area
    if siteroot is None:
        siteroot = tempfile.mkdtemp(prefix="siteroot")
    installer = Installer(siteroot)

    # Looking up the packages to install from the old install area
    oldarea = InstallAreaTool()
    dpkgs = oldarea.getDatapackageList()

    # Now gathering the packages by name
    from collections import defaultdict
    pdict = defaultdict(lambda: [])
    for p in dpkgs:
        l = pdict[p[0]]
        l.append(p)

    # Keeping only the last one!
    from LbUtils import versionSort
    torebuild = []
    for k in pdict.keys():
        ver =  pdict[k]
        sver =  versionSort(ver, reverse=True)
        p = sver[0]
        if p[0].startswith("TOOL"):
            print "Ignoring TOOL:" , p
        else:
            torebuild.append(p)

    # Now formatting the string for the nightlies...
    finalcommand = []
    for p in torebuild:
        ps = p[0].split("_")
        pname = ps[0] + ":" + "/".join(ps[1:])
        finalcommand += [pname, p[1]]

    print " ".join(finalcommand)

if __name__ == "__main__":
    pattern = None
    if len(sys.argv) > 1:
        pattern = (sys.argv[1])
    logging.basicConfig(level=logging.INFO)
    exit(listDataPackages(pattern, siteroot=os.environ["MYSITEROOT"]))
