###############################################################################
# (c) Copyright 2017 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Module that manages the DEV install area on /cvmfs/lhcbdev.cern.ch/lib

@author: Ben Couturier & Stefan-Gabriel CHITIC
'''
from lbinstall.Installer import Installer
import logging


class LbInstallManager:

    def __init__(self, siteroot):
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.DEBUG)
        if siteroot:
            self.installer = Installer(siteroot=siteroot)
            return
        raise Exception("Please specify MYSITEROOT in "
                        "the environment or use the "
                        "--root option")

    def _removeInstalledPackagesFromInstallList(self, rpm_names):
        # Get packages from names
        rpmlist = []
        # Now checking whether they are in the repo...
        self.log.warning("Config file loaded, looking for RPMs")
        for full_name in rpm_names:
            self.log.debug("Looking for %s" % full_name)
            tmp_full_name = full_name.split('-')
            name = tmp_full_name[0]
            version = None
            release = None
            if len(tmp_full_name) > 1:
                version = tmp_full_name[1]
            if len(tmp_full_name) > 2:
                release = tmp_full_name[2]
            package_remote = self.installer.remoteFindPackage(name,
                                                              version,
                                                              release)
            self.log.warning(
                "For %s, %s remotes were found" % (full_name,
                                                   len(package_remote)))
            if len(package_remote) > 0:
                package_remote = package_remote[0]
                is_installed = self.installer._localDB.isPackagesInstalled(
                    package_remote)
                if is_installed:
                    # Package already installed
                    self.log.warning("%s already installed", full_name)
                else:
                    rpmlist.append(package_remote)
        return rpmlist

    def installFiles(self, rpm_names):
        # Remove already installed files:
        self.rpmlist = self._removeInstalledPackagesFromInstallList(rpm_names)
        # Install packages
        if (len(self.rpmlist) > 0):
            self.log.warning("Now installing the packages")
            self.installer._install(self.rpmlist)
            self.log.warning("Installation done")
        else:
            self.log.warning("Nothing to do")

    def checkPackagesInRemoteDatabase(self, prefix):
        return list(self.installer.remoteListPackages(prefix + ".*"))
