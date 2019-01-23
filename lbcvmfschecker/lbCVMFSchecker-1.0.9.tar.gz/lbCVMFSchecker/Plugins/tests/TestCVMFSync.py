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
import smtplib
from datetime import datetime
from lbCVMFSchecker.Plugins.CVMFSync import CVMFSync
import unittest
from lbCVMFSchecker.tests.MockLogger import MockLoggingHandler
import logging
import subprocess

output = '''
[{"raw_revision":"40630"},{"raw_revision":"40215","status":"synchz"}]
'''


class DummyConnector():

    def __init__(self, *args, **kwargs):
        if kwargs.get('f', None):
            self.f = kwargs['f']
        else:
            self.f = None

    def write_points(self, *args, **kwargs):
        for arg in args:
            logging.info(arg)

    def query(self, *args, **kwargs):
        for arg in args:
            logging.info(arg)
        if self.f:
            return self.f()
        return DummyPoints()


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
    lines = ['--> test1',
             output,
             '']

    def readline(self):
        r = self.lines[self.i]
        self.i += 1
        return r


class DummyPoints():

    def get_points(self):
        return [{
            'day': '2017-05-30',
            'time': '1',
            'stratum0_rev': 40630,
            'stratum1_rev': 40215,
            'status': 'synchz',
            'is_alerted': True,
            'back_to_normal': True

        }, {
            'day': '2017-05-30',
            'time': '2',
            'stratum0_rev': 40630,
            'stratum1_rev': 40215,
            'status': 'synchz',
            'is_alerted': True,
            'back_to_normal': True
        }]


class DummyPoints2():

    def get_points(self):
        return [{
            'day': '2017-05-30',
            'time': '1',
            'stratum0_rev': 40630,
            'stratum1_rev': 40215,
            'status': 'unknonw',
            'is_alerted': False,
            'back_to_normal': False

        }]


class DummyPoints3():

    def get_points(self):
        return [{
            'day': '2017-05-30',
            'time': '1',
            'stratum0_rev': 40630,
            'stratum1_rev': 40630,
            'status': 'unknonw',
            'is_alerted': True,
            'back_to_normal': False

        }]


class TestLbLoader(unittest.TestCase):

    def dummySend(self, *args, **kwargs):
        for arg in args:
            logging.info(arg)

    def setUp(self):
        self.handler = MockLoggingHandler()
        logging.getLogger().addHandler(self.handler)
        subprocess.Popen = mockSuprocess.Popen
        self.obj = CVMFSync()
        self.obj.pwd = '/tmp/'
        self.obj.connector = DummyConnector()
        smtplib.SMTP.sendmail = self.dummySend

    def tearDown(self):
        pass

    def test_getValues(self):
        res = self.obj.getValues()
        from pprint import pprint
        pprint(res)
        self.assertEqual(
            res,
            {'all': [{'back_to_normal': True,
                      'day': '2017-05-30',
                      'is_alerted': True,
                      'status': 'synchz',
                      'stratum0_rev': 40630,
                      'stratum1_rev': 40215,
                      'time': '1'},
                     {'back_to_normal': True,
                      'day': '2017-05-30',
                      'is_alerted': True,
                      'status': 'synchz',
                      'stratum0_rev': 40630,
                      'stratum1_rev': 40215,
                      'time': '2'}],
             'last': {'back_to_normal': True,
                      'day': '2017-05-30',
                      'is_alerted': True,
                      'status': 'synchz',
                      'stratum0_rev': 40630,
                      'stratum1_rev': 40215,
                      'time': '2'}}
        )

    def test_shouldAlert(self):
        results = {
            'all': [
                {
                    'is_alerted': False,
                }
            ]
        }

        self.assertTrue(self.obj.shouldAlert(results))
        results = {
            'all': [
                {
                    'is_alerted': True,
                }
            ]
        }
        self.assertFalse(self.obj.shouldAlert(results))

    def test_isAlerted(self):
        results = {
            'all': [
                {
                    'is_alerted': False,
                    'back_to_normal': False,
                }
            ]
        }
        self.assertFalse(self.obj.isAlerted(results))
        results = {
            'all': [
                {
                    'is_alerted': True,
                    'back_to_normal': False,
                }
            ]
        }
        self.assertTrue(self.obj.isAlerted(results))
        results = {
            'all': [
                {
                    'is_alerted': True,
                    'back_to_normal': True,
                }
            ]
        }
        self.assertFalse(self.obj.isAlerted(results))

    def test_verify_limits(self):
        self.obj.verify_limits()
        a = '40630                         40215          ' \
            'synchz                '
        self.assertEqual(self.obj.info_messages[2],
                         a
                         )

    def test_verify_limits2(self):
        self.obj.connector = DummyConnector(f=DummyPoints2)
        self.obj.verify_limits()
        a = '40630                         40215          ' \
            'unknonw               '
        self.assertEqual(self.obj.info_messages[2],
                         a
                         )

    def test_verify_limits3(self):
        self.obj.connector = DummyConnector(f=DummyPoints3)
        self.obj.verify_limits()
        a = '40630                         40630          ' \
            'unknonw               '
        self.assertEqual(self.obj.info_messages[2],
                         a
                         )

    def test_execute(self):
        self.obj.execute()
        self.assertTrue("40630" in str(self.handler.messages['info'][2]))

    def test_check_install(self):
        self.obj._check_install()
        self.assertTrue("'stratum0_rev': 40630", self.handler.messages['info'])
        self.assertTrue("'stratum1_rev': 40215", self.handler.messages['info'])
        self.assertTrue("'stats': 'synchz", self.handler.messages['info'])


if __name__ == "__main__":
    unittest.main()
