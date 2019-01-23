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

from lbCVMFSTools.Injector import inject
from lbCVMFSTools.TaskHandlerInterface import TaskHandlerInterface
from lbCVMFSTools.TaskHandlers.NightliesInstallTask.Utils \
    import SlotsManager, PathManager, LinkManager, InstalledManager


@inject(pathManager=PathManager)
class NightliesInstallTask(TaskHandlerInterface, object):

    def __init__(self, installOnCvmfs=True, slotsPrefix='cvmfs',
                 pathManager=None, *args, **kwargs):
        super(NightliesInstallTask, self).__init__(*args, **kwargs)
        self.log_prefix = ''
        if self.dry_run:
            self.log_prefix = 'IN DRY-RUN MODE: '
        self.installOnCvmfs = installOnCvmfs
        self.slotsPrefix = slotsPrefix
        logging.getLogger().setLevel(logging.INFO)

        if pathManager:
            self.pathManager = pathManager
        else:
            self.pathManager = PathManager()
        self.slotManager = SlotsManager()
        self.linkManager = LinkManager(pathManager=self.pathManager)
        self.installManager = InstalledManager(pathManager=self.pathManager)

    def get_list_of_tasks(self):
        slots_platforms_all = self.slotManager.getSlots()
        slots_platforms = slots_platforms_all.get(self.slotsPrefix, [])
        todo = []
        alreadyInstalled = self.installManager.getInstalled()
        for slot_platform in slots_platforms:
            slot = slot_platform.get('slot', None)
            build_id = slot_platform.get('build_id', None)
            platform = slot_platform.get('platform', None)
            completed = slot_platform.get('completed', False)
            if not slot or not build_id or not platform:
                continue
            if completed:
                if (slot, build_id, platform) in alreadyInstalled:
                    logging.info(
                        "%s%s, %s, %s is already installed for today, "
                        "skipping" % (self.log_prefix, slot, build_id,
                                      platform))
                    continue
            todo.append((slot, build_id, platform, completed))

        if len(todo) == 0:
            logging.info("%sAll slots installed, nothing to do" %
                         self.log_prefix)
        return todo

    def perform_task(self, tasks):
        if not isinstance(tasks, list):
            tasks = [tasks]
        # BY default we consider all is there
        needPublish = False
        # Now installing and checking the difference
        for (sname, bid, platform, completed) in tasks:
            # making sure we haev the appropriate links for the builds
            try:
                if not self.linkManager.checkLinks(sname, bid):
                    logging.info(
                        "%sNeed to fix the links for %s %s" % (self.log_prefix,
                                                               sname,
                                                               bid))
                    needPublish = True
                    if not self.dry_run:
                        self.linkManager.fixLinks(sname, bid)
            except Exception as e:
                pass

            # performing the install
            logging.info("%sUpdating %s %s %s" % (self.log_prefix,
                                                  sname, bid, platform))
            if self.installOnCvmfs:
                try:
                    self.lbnInstall(sname, bid, platform)
                except:
                    # Ignoring problems with the tar files...
                    logging.info(
                        "%sInstallation problem. Ignoring to avoid transaction "
                        "rollback" % self.log_prefix)
            else:
                self.lbnInstall(sname, bid, platform)

            # Comparing the list of tar files
            try:
                if self.installManager.installHasChanged(sname, bid):
                    logging.info(
                        "%sInstall has changed - copying list of "
                        "installed tars" % self.log_prefix)
                    if not self.dry_run:
                        self.installManager.copyInstalledFile(sname, bid)
                    needPublish = True
            except Exception as e:
                print(e)
                # We just ignore and will not publish
                logging.info(
                    "%sError checking whether the install has changed" %
                    self.log_prefix)
            # Mark the platform as installed
            if not self.dry_run:
                if completed:
                    self.installManager.addInstalled([(sname, bid, platform)])

        if not needPublish and self.installOnCvmfs:
            logging.info(
                "%sNo new files to install - aborting transaction" %
                self.log_prefix)
            raise Exception("No new files, aborting transaction")

    def lbnInstall(self, slotname, buildId, platform):
        """ Actually call the lbn install command"""
        targetDir = self.pathManager.getSlotDir(slotname, buildId)
        args = ["lbn-install", "--dest=%s" % targetDir,
                "--platforms=%s" % platform,
                slotname, str(buildId)]
        logging.info("%sInvoking: %s" % (self.log_prefix, " ".join(args)))
        if self.dry_run:
            return
        rc = subprocess.call(args)
        if rc != 0:
            raise RuntimeError("Could not perform lbn-install")
