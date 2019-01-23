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
from lbCVMFSchecker.Plugins.NightliesChecker import NightliesChecker
import unittest
from lbCVMFSchecker.tests.MockLogger import MockLoggingHandler
import logging


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


class DummyPoints2():

    def get_points(self):
        return [{
            'slot': 'test1',
            'day': '2017-05-30',
            'time': '2',
            'is_installed': False,
            'installed_time': 'Mon Jun 19 03:13:17 2017',
            'is_alerted': False,
            'back_to_normal': False
        }]


class DummyPoints3():

    def get_points(self):
        return [{
            'slot': 'test1',
            'day': '2017-05-30',
            'time': '2',
            'is_installed': True,
            'installed_time': 'Mon Jun 19 03:13:17 2017',
            'is_alerted': True,
            'back_to_normal': False
        }]


class DummyPoints4():

    def get_points(self):
        return [{
            'slot': 'test2',
            'day': '2017-05-30',
            'time': '2',
            'is_installed': False,
            'installed_time': '',
            'is_alerted': True,
            'back_to_normal': False
        }]


class DummyPoints():

    def get_points(self):
        return [{
            'slot': 'test1',
            'day': '2017-05-30',
            'time': '1',
            'is_installed': True,
            'installed_time': 'Mon Jun 19 03:13:17 2017',
            'is_alerted': True,
            'back_to_normal': True

        }, {
            'slot': 'test1',
            'day': '2017-05-30',
            'time': '2',
            'is_installed': True,
            'installed_time': 'Mon Jun 19 03:13:17 2017',
            'is_alerted': True,
            'back_to_normal': True
        }]


class TestLbLoader(unittest.TestCase):

    def dummySend(self, *args, **kwargs):
        for arg in args:
            logging.info(arg)

    def setUp(self):
        self.handler = MockLoggingHandler()
        logging.getLogger().addHandler(self.handler)
        self.obj = NightliesChecker()
        self.obj.pwd = '/tmp/'
        self.obj.connector = DummyConnector()
        self.obj.SLOTS = ['test1']
        self.obj.SLOTS_MAX_TIME = {'test1': '00:01:00'}
        smtplib.SMTP.sendmail = self.dummySend

    def tearDown(self):
        pass

    def test_shouldAlert(self):
        results = {
            'all': [
                {
                    'is_alerted': False,
                    'installed_time': False,
                }
            ]
        }

        self.assertTrue(self.obj.shouldAlert(results))
        results['all'].append(
            {
                'is_alerted': False,
                'installed_time': True,
            }
        )
        self.assertFalse(self.obj.shouldAlert(results))
        results = {
            'all': [
                {
                    'is_alerted': True,
                    'installed_time': False,
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
        today = datetime.today().strftime('%Y-%m-%d')
        self.assertEqual(self.obj.info_messages[2],
                         'test1                         Yes            '
                         '2017-06-19 03:13:17  %s 00:01:00  ' % today
                         )

    def test_verify_limits2(self):
        self.obj.connector = DummyConnector(f=DummyPoints2)
        self.obj.verify_limits()
        self.assertTrue('Today path was not created for test1' in
                        self.obj.messages[0])

    def test_verify_limits3(self):
        self.obj.connector = DummyConnector(f=DummyPoints3)
        self.obj.verify_limits()
        today = datetime.today().strftime('%Y-%m-%d')
        self.assertEqual(self.obj.info_messages[2],
                         'test1                         Yes            '
                         '2017-06-19 03:13:17  %s 00:01:00  ' % today
                         )

    def test_verify_limits4(self):
        self.obj.SLOTS = ['test2']
        self.obj.connector = DummyConnector(f=DummyPoints4)
        self.obj.verify_limits()
        self.assertEqual(self.obj.info_messages[2].strip(),
                         'test2                         No'
                         )

    def test_execute(self):
        self.obj.execute()
        self.assertTrue("'slot': 'test1'" in self.handler.messages['info'][1])

    def test_getValues(self):
        res = self.obj.getValues()
        self.assertEqual(res, {
            'test1': {
                'last': {
                            'slot': 'test1',
                            'day': '2017-05-30',
                            'time': '2',
                            'is_installed': True,
                            'installed_time': 'Mon Jun 19 03:13:17 2017',
                            'is_alerted': True,
                            'back_to_normal': True
                },
                'all': [{
                            'slot': 'test1',
                            'day': '2017-05-30',
                            'time': '1',
                            'is_installed': True,
                            'installed_time': 'Mon Jun 19 03:13:17 2017',
                            'is_alerted': True,
                            'back_to_normal': True
                }, {
                            'slot': 'test1',
                            'day': '2017-05-30',
                            'time': '2',
                            'is_installed': True,
                            'installed_time': 'Mon Jun 19 03:13:17 2017',
                            'is_alerted': True,
                            'back_to_normal': True
                }]
            }
        })

    def test_updateAlerted(self):
        results = {
            'all': [
                {
                    'slot': 'test1',
                    'day': '2017-05-30',
                    'time': '2017-05-30',
                    'is_installed': True,
                    'installed_time': '2017-05-30',
                }
            ]
        }
        self.obj.updateAlerted(results['all'][0], hasBeenAlerted=True)
        self.assertTrue("'is_alerted': True" in self.handler.messages['info'][1])
        self.assertTrue("'back_to_normal': False" in
                        self.handler.messages['info'][1])

    def test_check_install(self):
        self.obj._check_install()
        self.assertTrue("'installed_time': ''", self.handler.messages['info'])
        self.assertTrue("'slot': 'test1'", self.handler.messages['info'])
        if not os.path.exists('/tmp/test1'):
            os.mkdir('/tmp/test1')
        with open('/tmp/test1/Today', 'w') as f:
            f.write('')
        created_time = os.path.getmtime('/tmp/test1/Today')
        created_time = time.ctime(created_time)
        self.obj._check_install()
        self.assertTrue("'installed_time': '%s'" % created_time,
                        self.handler.messages['info'])
        self.assertTrue("'slot': 'test1'", self.handler.messages['info'])


if __name__ == "__main__":
    unittest.main()
