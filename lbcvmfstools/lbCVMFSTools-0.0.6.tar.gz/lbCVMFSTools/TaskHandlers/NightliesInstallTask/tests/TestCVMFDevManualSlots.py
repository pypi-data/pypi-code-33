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
Test of the version path manager functionality in the model classes.

@author: Stefan-Gabriel CHITIC
'''
import json
import logging
import shutil
import subprocess
import unittest

import os

import lbCVMFSTools.TaskHandlers.NightliesInstallTask.CVMFSDevManualSlots as s


class MockRaw():
    def __init__(self, key):
        self.key = key
        self.doc = {
            'build_id': '1234',
            'config': {'platforms': ['p1', 'p2']}
        }


class MockDashboard():

    def __init__(self):
        self.db.view = self.mockView
        return self

    def mockView(self, *args, **kwargs):
        print(args)
        print(kwargs)
        return [MockRaw('slot1'), MockRaw('slot2')]


class TestManager(unittest.TestCase):

    def setUp(self):
        with open("/tmp/slots_conf.txt", 'w') as f:
            f.write("slot1\nslot2\n#slot3\n")

    def tearDown(self):
        pass

    def mocked_call(self, *a, **kw):
        self.args = a
        self.kwargs = kw
        return self.mocked_return_code

    def test_getConfDir(self):
        a = s._getConfDir()
        self.assertEqual(a, "%s/conf" % os.environ["HOME"])

    def test_getSlots(self):
        a = s.getSlots('/tmp/slots_conf.txt')
        self.assertEqual(a, ['slot1', 'slot2'])

    #def test_getSlotsDict(self):
        #slots = s.getSlotsDict()
        #self.assertEqual(slots, ['slot1', 'slot2'])


if __name__ == "__main__":
    unittest.main()
