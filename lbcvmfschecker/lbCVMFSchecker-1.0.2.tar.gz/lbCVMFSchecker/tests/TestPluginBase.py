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
import logging
import shutil
import subprocess
import unittest

import os

from lbCVMFSchecker.tests.MockLogger import MockLoggingHandler
from lbCVMFSchecker.LbCVMFSCheckerPluginBase import PluginBase


class DummyImpls(PluginBase):
    raise_error = False

    def execute(self):
        if self.raise_error:
            self.messages.append("test error")


class TestPluginBase(unittest.TestCase):

    def setUp(self):
        self.handler = MockLoggingHandler()
        logging.getLogger().addHandler(self.handler)

    def tearDown(self):
        pass

    def test_constructor(self):
        PluginBase()
        self.assertEqual(self.handler.messages['info'], ["Loaded PluginBase "
                                                         "plugin"])

    def test_exec(self):
        obj = PluginBase()
        self.assertRaises(NotImplementedError, obj.execute)

    def test_Check(self):
        obj = PluginBase()
        self.assertRaises(NotImplementedError, obj.check)
        self.assertEqual(self.handler.messages['info'], ["Loaded PluginBase "
                                                         "plugin",
                                                         "Performing checks "
                                                         "for PluginBase "
                                                         "plugin"])

    def test_With_Dummy(self):
        obj = DummyImpls()
        obj.check()
        self.assertEqual(self.handler.messages['info'], ["Loaded DummyImpls "
                                                         "plugin",
                                                         "Performing checks "
                                                         "for DummyImpls "
                                                         "plugin",
                                                         "No errors in "
                                                         "DummyImpls"])
        obj.raise_error = True
        self.handler.reset()
        obj.check()
        self.assertEqual(self.handler.messages['info'], [
                                                         "Performing checks "
                                                         "for DummyImpls "
                                                         "plugin"
                                                         ])
        self.assertEqual(self.handler.messages['error'], ["test error"])


if __name__ == "__main__":
    unittest.main()
