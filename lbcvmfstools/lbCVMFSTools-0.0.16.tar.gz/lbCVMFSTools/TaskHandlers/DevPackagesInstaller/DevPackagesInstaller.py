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
CVMFS nightlies installer
@author: Stefan-Gabriel CHITIC, Ben Couturier
'''
import logging
import subprocess
import os
from lbCVMFSTools.Injector import inject
from lbCVMFSTools.TaskHandlerInterface import TaskHandlerInterface
from lbdevmanager.GitManager import GitManager
from lbdevmanager.LbInstallManager import LbInstallManager

FREQ = 10 * 60

class DevPackagesInstaller(TaskHandlerInterface, object):

    def __init__(self, installOnCvmfs=True, *args, **kwargs):
        if kwargs.get('FREQ', None):
            global FREQ
            FREQ = kwargs.get('FREQ')
        super(DevPackagesInstaller, self).__init__(FREQ, *args, **kwargs)
        self.log_prefix = ''
        if self.dry_run:
            self.log_prefix = 'IN DRY-RUN MODE: '
        self.installOnCvmfs = installOnCvmfs
        self.siteroot = "/cvmfs/lhcbdev.cern.ch/lib"
        self.repo = os.path.expandvars("${HOME}/conf/cvmfsdev-sw")
        logging.getLogger().setLevel(logging.INFO)
        self.gitManager = GitManager(repo_path=self.repo)

    def get_list_of_tasks(self):
        filesToInstall = self.gitManager.GetFilesDiffToInstall()
        if len(filesToInstall) == 0:
            self.gitManager.UpdateTags()
            return []
        return [filesToInstall]

    def perform_task(self, task):
        installer = LbInstallManager(siteroot=self.siteroot)
        installer.installFiles(task)
        