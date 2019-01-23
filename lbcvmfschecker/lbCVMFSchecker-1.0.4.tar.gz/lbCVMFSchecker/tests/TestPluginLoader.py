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
from lbCVMFSchecker.LbCVMFSCheckerPluginBase import PluginBase

from lbCVMFSchecker.PluginLoader import LbLoader


class TestLbLoader(unittest.TestCase):

    def setUp(self):
        self.currentPath = os.path.abspath(__file__)
        self.obj = LbLoader(base='lbCVMFSchecker.tests.Plugins')

    def tearDown(self):
        pass

    def test_getPluginNames(self):
        self.assertEqual(self.obj.getPluginNames(), ['MockPlugin'])

    def test_getPlugins(self):
        res = self.obj._getPlugins()
        self.assertEqual(res, ['MockPlugin'])

    def test_convertToModuleName(self):
        self.assertEqual(self.obj._convertToModuleName('toto.py'), 'toto')

    def test_getSubclass(self):
        from lbCVMFSchecker.tests.Plugins import MockPlugin
        res = self.obj._getSubclass(MockPlugin, PluginBase)
        self.assertEqual(res, MockPlugin.MockPlugin)
        s = Exception
        res = self.obj._getSubclass(s, PluginBase)
        self.assertEqual(res, None)

    def test_getModule(self):
        from lbCVMFSchecker.tests.Plugins.MockPlugin import MockPlugin
        self.assertRaises(ImportError, self.obj.getModule, 'toto')
        self.assertEqual(self.obj.getModule('MockPlugin').__class__, MockPlugin)

    def test_getModules(self):
        from lbCVMFSchecker.tests.Plugins.MockPlugin import MockPlugin
        self.assertEqual([f for f in self.obj.getModules()],
                         ['MockPlugin'])

if __name__ == "__main__":
    unittest.main()
