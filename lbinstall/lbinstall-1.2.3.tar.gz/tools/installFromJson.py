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
from os.path import abspath
import json
from lbinstall.Installer import Installer
import re


def installFromJson(siteroot=None, rpmcache=[], dbonly=True):

    # Preparing the new install area
    if siteroot is None:
        siteroot = tempfile.mkdtemp(prefix="siteroot")
    installer = Installer(siteroot)
    for cachedir in rpmcache:
        installer.addDirToRPMCache(abspath(cachedir))

    with open("packages_to_install.json", "r") as f:
        raw_data = f.read()
        data = json.loads(raw_data)
    files_to_install = set()
    for rpmname in data:
        m = re.match("(.*)-([\d\.]+)-(\d+)$", rpmname)
        if m is not None:
            rpmname = m.group(1)
            version = m.group(2)
            release = m.group(3)
        packagelist = installer.remoteFindPackage(rpmname, version, release)
        files_to_install |= set(packagelist)
    files_to_install = list(files_to_install)
    installer.install(files_to_install,
                      justdb=dbonly
                      )

if __name__ == "__main__":
    rpmcache = []
    if len(sys.argv) < 2:
        exit(0)

    rpmcache = sys.argv[1].split('|')

    logging.basicConfig(level=logging.INFO)
    exit(installFromJson(siteroot=os.environ["MYSITEROOT"], rpmcache=rpmcache))
