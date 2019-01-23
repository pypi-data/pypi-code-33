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
import smtplib

from lbCVMFSchecker.tests.MockLogger import MockLoggingHandler
from lbCVMFSchecker.LbEmailer import Emailer


class TestPluginBase(unittest.TestCase):

    def dummySend(self, *args, **kwargs):
        for arg in args:
            logging.info(arg)

    def setUp(self):
        self.handler = MockLoggingHandler()
        logging.getLogger().addHandler(self.handler)
        smtplib.SMTP.sendmail = self.dummySend

    def tearDown(self):
        pass

    def test_sendmail(self):
        obj = Emailer('toto', 'toto', 'toto', 'toto')
        obj.send()
        res = ['toto', "['toto']",
               'Content-Type: text/plain; charset="us-ascii"'
               '\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n'
               'From: toto\nTo: toto\nSubject: toto\n\ntoto']
        self.assertEqual(self.handler.messages['info'], res)

    def test_send(self):
        Emailer.Send('toto')
        res = ['Content-Type: text/plain; charset="us-ascii"'
               '\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n',
               'Subject: Failure on cvmfs-lhcbdev\n\ntoto']
        for r in res:
            self.assertTrue(r in self.handler.messages['info'][2])

if __name__ == "__main__":
    unittest.main()
