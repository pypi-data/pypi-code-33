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
@author: Stefan-Gabriel CHITIC
'''
import datetime
import json
import shelve
import time
from lbCVMFSTools.TaskHandlers.NightliesInstallTask.\
    CVMFSDevManualSlots import getSlots as ManualSlots
import os


class SlotsManager():

    def getSlots(self):
        """ Util function to get slots of interest from conf file """
        slots = None
        # TODO from marco
        if slots is None:
            slots = ManualSlots()
        return slots

    def getTodayStr(self, tmp):
        """ Get today's date as a string """
        if tmp is None:
            return datetime.datetime.now().strftime("%Y-%m-%d")
        else:
            return tmp

    def _checksum(self, filename):
        import hashlib
        return hashlib.md5(open(filename, 'rb').read()).hexdigest()


class PathManager():

    def __init__(self, workspace=None, installArea=None):
        if workspace:
            self.workspace = workspace
        else:
            self.workspace = os.environ["HOME"]
        if installArea:
            self.installArea = installArea
        else:
            self.installArea = '/cvmfs/'

    def _getRepoDir(self):
        return self.installArea

    def getVarDir(self):
        return os.path.join(self.workspace, "var")

    def getConfDir(self):
        return os.path.join(self.workspace, "conf")

    def getSlotDir(self, slotname, buildId):
        return os.path.join(self._getRepoDir(), slotname, str(buildId))

    def getSlotDirDayLink(self, slotname, strdate=None):
        dname = datetime.datetime.now().strftime("%a")
        if strdate is not None:
            t = time.strptime(strdate, "%Y-%m-%d")
            dname = time.strftime("%a", t)
        return os.path.join(self._getRepoDir(), slotname, dname)

    def getSlotTodayLink(self, slotname):
        return os.path.join(self._getRepoDir(), slotname, "Today")

    def getSlotInstalledFilename(self, slotname, buildId):
        return os.path.join(self._getRepoDir(), slotname, str(buildId),
                            ".installed")

    def getVarInstalledFilename(self, slotname, buildId):
        return os.path.join(self.getVarDir(),
                            ".".join([slotname, str(buildId), "installed"]))


class LinkManager():

    def __init__(self, pathManager):
        self.pathManager = pathManager

    def checkLinks(self, slotname, buildId, strdate=None):
        """ Check that the links are correct """
        daylinkOk = False
        todaylinkOk = False
        daylink = self.pathManager.getSlotDirDayLink(slotname, strdate)
        todaylink = self.pathManager.getSlotTodayLink(slotname)
        if os.path.exists(daylink):
            if os.readlink(daylink) == str(buildId):
                daylinkOk = True

        if os.path.exists(todaylink):
            if os.readlink(todaylink) == str(buildId):
                todaylinkOk = True
        return daylinkOk and todaylinkOk

    def fixLinks(self, slotname, buildId, strdate=None):
        """ Check that the links are correct """

        daylink = self.pathManager.getSlotDirDayLink(slotname, strdate)
        todaylink = self.pathManager.getSlotTodayLink(slotname)
        if os.path.exists(daylink):
            if os.readlink(daylink) != str(buildId):
                os.remove(daylink)
                os.symlink(str(buildId), daylink)
        else:
            os.symlink(str(buildId), daylink)

        if os.path.exists(todaylink):
            if os.readlink(todaylink) != str(buildId):
                os.remove(todaylink)
                os.symlink(str(buildId), todaylink)
        else:
            os.symlink(str(buildId), todaylink)


class InstalledManager():

    INST_SLOTS = "INSTALLED"

    def __init__(self, pathManager):
        self.pathManager = pathManager
        self.slotsManager = SlotsManager()

    def getFilenameForDate(self, strdate=None):
        strdate = self.slotsManager.getTodayStr(strdate)
        return os.path.join(self.pathManager.getVarDir(),
                            "slots_installed.%s" % strdate)

    def copyInstalledFile(self, slotname, buildId):
        import shutil
        shutil.copyfile(
            self.pathManager.getSlotInstalledFilename(slotname, buildId),
            self.pathManager.getVarInstalledFilename(slotname, buildId))

    def installHasChanged(self, slotname, buildId):
        oldmd5 = ""
        sManager = SlotsManager()
        if os.path.exists(
                self.pathManager.getVarInstalledFilename(slotname, buildId)):
            oldmd5 = sManager._checksum(
                self.pathManager.getVarInstalledFilename(slotname, buildId))

        newmd5 = sManager._checksum(
            self.pathManager.getSlotInstalledFilename(slotname, buildId))
        return oldmd5 != newmd5

    def getInstalled(self, strdate=None):
        """ Returns the list of installed platforms as shelved on the system
        """
        data = set()
        f = shelve.open(self.getFilenameForDate(strdate))
        data = f.get(self.INST_SLOTS, set())
        f.close()
        return data

    def addInstalled(self, installed, strdate=None):
        """ Adds triplets to  the list of installed platforms as shelved on
        the system """
        f = shelve.open(self.getFilenameForDate(strdate))
        try:
            data = f.get(self.INST_SLOTS, set())
            if data is None:
                data = set()
            for tup in installed:
                data.add(tup)
            f[self.INST_SLOTS] = data
        except Exception as e:
            f.close()
            raise(e)

    def setInstalled(self, installed, strdate=None):
        """ Adds triplets to  the list of installed platforms as
        shelved on the system """
        f = shelve.open(self.getFilenameForDate(strdate))
        try:
            data = set()
            for tup in installed:
                data.add(tup)
            f[self.INST_SLOTS] = data
        except Exception as e:
            f.close()
            raise(e)