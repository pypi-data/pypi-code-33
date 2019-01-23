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
Slot manager for CVMFS Tools
@author: Stefan-Gabriel CHITIC
'''
import datetime
import json
import shutil
import unittest

import os

from lbCVMFSTools.TaskHandlers.NightliesInstallTask.Utils import \
    SlotsManager


class TestSlotsManager(unittest.TestCase):
    def setUp(self):
        if os.path.exists("/tmp/toto"):
            shutil.rmtree("/tmp/toto")
        if os.path.exists("/tmp/foo"):
            shutil.rmtree("/tmp/foo/")
        os.mkdir("/tmp/toto/")
        os.mkdir("/tmp/toto/cvmfstest.cern.ch/")
        os.mkdir("/tmp/toto/cvmfstest.cern.ch/nightlies")
        os.mkdir("/tmp/toto/cvmfstest.cern.ch/nightlies/slot1")
        os.mkdir("/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/1234")
        os.mkdir("/tmp/foo/")
        os.mkdir("/tmp/foo/conf/")
        os.mkdir("/tmp/foo/var/")
        with open("/tmp/foo/conf/slots_on_cvmfs.txt", 'w') as f:
            f.write("slot_test1\n")
            f.write("slot_test2\n")
            f.write("#slot_test3\n")

        self.sManager = SlotsManager()

    def tearDown(self):
        if os.path.exists("/tmp/toto"):
            shutil.rmtree("/tmp/toto")
        if os.path.exists("/tmp/foo"):
            shutil.rmtree("/tmp/foo/")

    def test_getTodayStr(self):
        n = datetime.datetime.now()
        self.assertEqual(self.sManager.getTodayStr("2017-05-31"),
                         "2017-05-31")
        self.assertEqual(self.sManager.getTodayStr(None),
                         n.strftime('%Y-%m-%d'))
        self.sManager = SlotsManager()
        self.assertEqual(self.sManager.getTodayStr(None),
                         n.strftime('%Y-%m-%d'))

    def test_checksum(self):
        self.assertEqual(
            self.sManager._checksum('/tmp/foo/conf/slots_on_cvmfs.txt'),
            'ffa032eb24c2adccf42673e6ab6fc252')

if __name__ == "__main__":

    unittest.main()
