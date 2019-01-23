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
from lbCVMFSTools.TaskHandlers.NightliesInstallByProjectTask.Utils \
    import PathManager, LinkManager, InstalledManager
from LbNightlyTools import Dashboard
from lbCVMFSTools import Audit


FREQ = 1


@inject(pathManager=PathManager)
class NightliesInstallByProjectTask(TaskHandlerInterface, object):

    def __init__(self, slot, build, platform, project,
                 installOnCvmfs=True, overrideTodayCheck=False,
                 pathManager=None, *args, **kwargs):
        if kwargs.get('FREQ', None):
            global FREQ
            FREQ = kwargs.get('FREQ')
        super(NightliesInstallByProjectTask, self).__init__(FREQ, *args,
                                                            **kwargs)
        self.slot = slot
        self.build = build
        self.platform = platform
        self.project = project
        self.log_prefix = ''
        if self.dry_run:
            self.log_prefix = 'IN DRY-RUN MODE: '
        self.installOnCvmfs = installOnCvmfs
        logging.getLogger().setLevel(logging.INFO)
        self.overrideTodayCheck = overrideTodayCheck
        if pathManager:
            self.pathManager = pathManager
        else:
            self.pathManager = PathManager()
        self.linkManager = LinkManager(pathManager=self.pathManager)
        self.installManager = InstalledManager(pathManager=self.pathManager)

    def get_list_of_tasks(self):
        alreadyInstalled = self.installManager.getInstalled()
        tuple_slot = (self.slot, self.build, self.platform,  self.project)
        if tuple_slot in alreadyInstalled:
            logging.info("%s%s, %s, %s, %s is already installed for today, "
                         "skipping" % (self.log_prefix, self.slot, self.build,
                                       self.platform, self.project))
            return []
        if not self.overrideTodayCheck and not self._is_slot_for_today():
            logging.info("%s%s, %s, %s, %s is not a slot for today, "
                         "skipping" % (self.log_prefix, self.slot, self.build,
                                       self.platform, self.project))
            return []
        return [tuple_slot]

    def _is_slot_for_today(self):
        dash = Dashboard()
        strdate = self.installManager.getTodayStr(None)
        rows = [(row.doc['slot'], row.doc['build_id']) for row in
                dash.db.view('summaries/byDay', key=strdate, include_docs=True)]
        for slot, build in rows:
            if self.slot == slot and str(self.build) == str(build):
                return True
        return False

    def perform_task(self, task):
        slot = task[0]
        build = task[1]
        platform = task[2]
        project = task[3]
        # BY default we consider all is there
        needPublish = False
        # Now installing and checking the difference
        # making sure we haev the appropriate links for the builds
        try:
            if not self.linkManager.checkLinks(slot, build):
                logging.info("%sNeed to fix the links for %s %s" %
                             (self.log_prefix, slot, build))
                needPublish = True
                if not self.dry_run:
                    self.linkManager.fixLinks(slot, build)
        except Exception as e:
            pass

        # performing the install
        logging.info("%sUpdating %s %s %s %s" % (self.log_prefix,
                                                 slot, build, platform,
                                                 project))
        if self.installOnCvmfs:
            try:
                self.lbnInstall(slot, build, platform, project)
            except:
                # Ignoring problems with the tar files...
                logging.info(
                    "%sInstallation problem. Ignoring to avoid transaction "
                    "rollback" % self.log_prefix)
        else:
            self.lbnInstall(slot, build, platform, project)

        # Comparing the list of tar files
        try:
            if self.installManager.installHasChanged(slot, build):
                logging.info(
                    "%sInstall has changed - copying list of "
                    "installed tars" % self.log_prefix)
                if not self.dry_run:
                    self.installManager.copyInstalledFile(slot, build)
                needPublish = True
        except Exception as e:
            print(e)
            # We just ignore and will not publish
            logging.info(
                "%sError checking whether the install has changed" %
                self.log_prefix)
        # Mark the platform as installed
        if not self.dry_run:
            self.installManager.addInstalled([(slot, build, platform, project)])

        if not needPublish and self.installOnCvmfs:
            logging.info(
                "%sNo new files to install - aborting transaction" %
                self.log_prefix)
            raise UserWarning("No new files, aborting transaction")

    def lbnInstall(self, slotname, buildId, platform, project):
        """ Actually call the lbn install command"""
        targetDir = self.pathManager.getSlotDir(slotname, buildId)
        args = ["lbn-install", "--dest=%s" % targetDir,
                "--platforms=%s" % platform, '--projects=%s' % project,
                slotname, str(buildId)]
        logging.info("%sInvoking: %s" % (self.log_prefix, " ".join(args)))
        if self.dry_run:
            return
        Audit.write(Audit.LBNINSTALL_START)
        rc = subprocess.call(args)
        Audit.write(Audit.LBNINSTALL_END)
        if rc != 0:
            raise RuntimeError("Could not perform lbn-install")

if __name__ == '__main__':
    a = NightliesInstallByProjectTask('lhcb-head', '1696', None, None)
    print a.get_list_of_tasks()
    a = NightliesInstallByProjectTask('lhcb-head', '1697', None, None)
    print a.get_list_of_tasks()
