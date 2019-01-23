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
import time
import subprocess

from lbCVMFSchecker.Plugins.LogChecker import LogChecker
import unittest
from lbCVMFSchecker.tests.MockLogger import MockLoggingHandler
import logging


class mockSuprocess:

    def __init__(self):
        self.stdout = mockProc()

    def wait(self):
        pass

    @staticmethod
    def Popen(self, *args, **kwargs):
        logging.info(args)
        return mockSuprocess()


class mockProc:

    i = 0
    lines = ['Error', 'a\tb\t301\tIdle\n', '']

    def readline(self):
        r = self.lines[self.i]
        self.i += 1
        return r


class TestLogChecker(unittest.TestCase):

    def setUp(self):
        self.handler = MockLoggingHandler()
        logging.getLogger().addHandler(self.handler)
        subprocess.Popen = mockSuprocess.Popen
        self.obj = LogChecker()
        self.obj.PROCESS_MAX_TIMES['toto'] = None

    def tearDown(self):
        pass

    def test_execute(self):
        self.obj.execute()
        self.assertEqual(self.obj.messages,
                         ['Execution time of Idle was 301 (Limit: 300)'])


if __name__ == "__main__":
    unittest.main()
