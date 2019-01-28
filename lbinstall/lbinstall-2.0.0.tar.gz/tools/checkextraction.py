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
Tool to validate the extraction of RPM files with the rpmfile package
and the PackageManager module.

'''

import os
import sys
import tempfile

from lbinstall.extra.ExtractionChecker import checkExtraction
from lbinstall.Installer import Installer


def getLHCbPackage(installer):
    ''' List packages from LHCb and implicitly needed ones '''
    allpackages = set()
    for p in installer.remoteListPackages():
        if p.repository.name != "lcg":
            allpackages.add(p)
    return allpackages


def checkFilesFromRepo(pattern=None, siteroot=None):

    if siteroot is None:
        siteroot = tempfile.mkdtemp(prefix="siteroot")
    installer = Installer(siteroot)
    allpackages = getLHCbPackage(installer)

    print("=====> %s packages in LHCb repos" % len(allpackages))

    superset = set()
    for p in list(allpackages):
        print(p.name)
        superset |= set(installer.listDependencies(p))

    toprocess = list(superset)
    try:
        import numpy as np
        toprocess = np.ramdom.permutation(superset)
    except:
        pass

    localfiles = installer._downloadfiles(toprocess)
    print(localfiles)
    patternstr = pattern
    if patternstr is None:
        patternstr = "ALL"
    with open("test_result_%s.txt" % pattern, "w") as f:
        for p in localfiles:
            (d1, d2) = checkExtraction(p)
            f.write("\n========= %s\n" % os.path.basename(p))
            if len(d1) != 0 or len(d2) != 0:
                for d in d1:
                    f.write("%s\n" % str(d))
                f.write("\n--------\n")
                for d in d2:
                    f.write("%s\n" % str(d))
            f.flush()

if __name__ == "__main__":
    pattern = None
    if len(sys.argv) > 1:
        pattern = (sys.argv[1])
    import logging
    logging.basicConfig(level=logging.INFO)
    exit(checkFilesFromRepo(pattern, siteroot=os.environ["MYSITEROOT"]))
