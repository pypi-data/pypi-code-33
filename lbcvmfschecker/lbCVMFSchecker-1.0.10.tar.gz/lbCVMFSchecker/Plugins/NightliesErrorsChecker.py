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


:author: Stefan-Gabriel CHITIC
'''

from lbCVMFSchecker.LbCVMFSCheckerPluginBase import PluginBase
from datetime import datetime
from datetime import timedelta
import os
import time
from lbCVMFSchecker.LbDBConnector import getConnector
from lbCVMFSchecker.LbEmailer import Emailer
from pyrabbit2.api import Client


class NightliesErrorsChecker(PluginBase):

    def __init__(self):
        super(NightliesErrorsChecker, self).__init__()
        self.connector = getConnector()
        user, pwd = self._get_pwd_from_sys()
        self.cl = Client('lbmessagingbroker.cern.ch:15672',
                         user, pwd)

    def _get_pwd_from_sys(self):
        """
        Get the RabbitMQ password from the environment of from a file on disk
        """
        # First checking the environment
        res = os.environ.get("RMQPWD", None)

        # Checking for the password in $HOME/private/rabbitmq.txt
        if res is None:
            fname = os.path.join(os.environ["HOME"], "private", "rabbitmq.txt")
            if os.path.exists(fname):
                with open(fname, "r") as f:
                    data = f.readlines()
                    if len(data) > 0:
                        res = data[0].strip()

        # Separate the username/password
        (username, password) = res.split("/")
        return username, password

    def execute(self):
        self._check_install()
        self.verify_limits()

    def verify_limits(self):
        now = datetime.now()
        results = self.getValues()
        data = results['last']
        should_alert = self.shouldAlert(results)
        if data['installed_time'] > 10:
            msg = 'Warning! More than 10 ' \
                  'messages in the error queue: %s' % data['installed_time']
            self.messages.append(msg)
            if should_alert:
                Emailer.Send(msg)
                self.updateAlerted(data)
                return
        elif self.isAlerted(results):
            msg = "Everything is back to normal! " \
                  "There are less than 10 messages in the error queue"
            Emailer.Send(msg, backToNrormal=True)
            self.updateAlerted(data, hasBeenAlerted=False)

    def isAlerted(self, results):
        alerted = False
        backToNormal = False
        for result in results['all']:
            if result['is_alerted']:
                alerted = True
            if result['back_to_normal']:
                backToNormal = True
        return (alerted and not backToNormal)

    def updateAlerted(self, results, hasBeenAlerted=True):
        db_entry = {
            'measurement': "nightliesErrors",
            'tags': {
                'day': results['day']
            },
            "time": results['time'],
            'fields': {
                'is_alerted': hasBeenAlerted,
                'installed_time': results['installed_time'],
                'back_to_normal': not(hasBeenAlerted)
            }
        }
        self.connector.write_points([db_entry])

    def shouldAlert(self, results):
        for result in results['all']:
            if result['is_alerted'] is True:
                return False
        return True

    def getValues(self):
        now = datetime.now()
        query = 'select * from nightliesErrors WHERE day=\'%s\';'
        query = query % (now.strftime('%Y-%m-%d'))
        result = self.connector.query(query)
        all_results = list(result.get_points())
        last_result = all_results[0]
        for res in all_results[1:]:
            if res['time'] > last_result['time']:
                last_result = res
        to_return = {
            'last': last_result,
            'all': all_results
        }
        return to_return

    def _check_install(self):
        q = self.cl.get_queue('/lhcb', 'CVMFSDevActionsErrors')
        nb_errors = q['messages']
        now = datetime.now()
        current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        db_entries = []
        db_entry = {
            'measurement': "nightliesErrors",
            'tags': {
                'day': now.strftime('%Y-%m-%d')
            },
            "time": current_time,
            'fields': {
                'is_alerted': False,
                'installed_time': nb_errors,
                'back_to_normal': False,
            }
        }
        db_entries.append(db_entry)
        self.connector.write_points(db_entries)

