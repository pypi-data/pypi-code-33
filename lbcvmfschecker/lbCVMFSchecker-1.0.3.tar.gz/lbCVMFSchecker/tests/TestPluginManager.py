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
import os
import unittest
import logging
from lbCVMFSchecker.tests.MockLogger import MockLoggingHandler
from lbCVMFSchecker.tests.Plugins import MockPlugin

from lbCVMFSchecker.PluginManager import LbPluginManager


class TestLbLoader(unittest.TestCase):

    def setUp(self):
        self.currentPath = os.path.abspath(__file__)
        self.obj = LbPluginManager(base='lbCVMFSchecker.tests.Plugins')
        self.handler = MockLoggingHandler()
        logging.getLogger().addHandler(self.handler)

    def tearDown(self):
        pass

    def test_reload(self):
        self.obj.loader.plugins = []
        self.obj.reload()
        self.assertEqual(len(self.obj.loader.plugins), 1)
        self.obj.reload()
        self.assertEqual(len(self.obj.loader.plugins), 1)

    def test_exec(self):
        self.obj.execute('MockPlugin')
        self.assertEqual(self.handler.messages['info'],
                         ["Performing checks for MockPlugin plugin",
                          "I'm executed",
                          "No errors in MockPlugin"])
    def test_execall(self):
        self.obj.executeAll()
        self.assertEqual(self.handler.messages['info'],
                         ["Performing checks for MockPlugin plugin",
                          "I'm executed",
                          "No errors in MockPlugin"])

if __name__ == "__main__":
    unittest.main()
