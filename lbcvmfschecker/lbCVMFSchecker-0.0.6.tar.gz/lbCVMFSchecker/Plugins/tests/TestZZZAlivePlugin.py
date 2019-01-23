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
import urllib2

from lbCVMFSchecker.Plugins.ZZZAlivePlugin import ZZZAlivePlugin
import unittest
from lbCVMFSchecker.tests.MockLogger import MockLoggingHandler
import logging


class mockReader:

    def __init__(self, throwError):
        self.throwError = throwError

    def read(self):
        if self.throwError:
            raise urllib2.HTTPError(None, 404, None, None, None)


class TestLogChecker(unittest.TestCase):

    def dummyUrlopen(self, *args, **kwargs):
        logging.info(args)
        return mockReader(self.throwError)

    def setUp(self):
        self.handler = MockLoggingHandler()
        self.throwError = False
        logging.getLogger().addHandler(self.handler)
        urllib2.urlopen = self.dummyUrlopen
        self.obj = ZZZAlivePlugin()

    def tearDown(self):
        pass

    def test_execute(self):
        self.obj.execute()
        self.assertEqual(self.handler.messages['info'][1],
                         "('https://lhcb-nightlies.cern.ch/updateCVMFSmonitor/"
                         "',)")

        self.throwError = True

        self.obj.execute()
        self.assertEqual(self.obj.messages[0], 404)



if __name__ == "__main__":
    unittest.main()
