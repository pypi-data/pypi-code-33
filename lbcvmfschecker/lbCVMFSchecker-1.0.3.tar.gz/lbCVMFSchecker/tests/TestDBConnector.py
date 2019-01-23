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
from lbCVMFSchecker.LbDBConnector import InFluxDbConnector, getConnector

from lbCVMFSchecker.tests.MockLogger import MockLoggingHandler
from influxdb import InfluxDBClient


class DummyConnector():

    def __init__(self, *args, **kwargs):
        pass

    def create_database(self, *args, **kwargs):
        pass


class TestPluginBase(unittest.TestCase):

    def my_init(self, *args, **kwargs):
        return DummyConnector(*args, **kwargs)

    def setUp(self):
        self.handler = MockLoggingHandler()
        logging.getLogger().addHandler(self.handler)
        InfluxDBClient.__new__ = self.my_init
        self.obj = InFluxDbConnector()

    def tearDown(self):
        pass

    def test_get(self):
        self.assertEqual(self.obj.getConnector().__class__, DummyConnector)

    def test_getInstance(self):
        con1 = getConnector()
        con2 = getConnector()
        self.assertEqual(con1, con2)

if __name__ == "__main__":
    unittest.main()
