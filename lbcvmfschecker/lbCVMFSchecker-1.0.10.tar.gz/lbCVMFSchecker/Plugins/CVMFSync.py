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
import subprocess
import os
import time
import json
from lbCVMFSchecker.LbDBConnector import getConnector
from lbCVMFSchecker.LbEmailer import Emailer


class CVMFSync(PluginBase):

    def __init__(self):
        super(CVMFSync, self).__init__()
        self.connector = getConnector()
        self.pwd = '/cvmfs/lhcbdev.cern.ch/nightlies'
        if os.environ.get('CVMFS_REPO_NAME', None):
            self.pwd = '/cvmfs/%s/nightlies' % os.environ['CVMFS_REPO_NAME']

    def execute(self):
        self._check_install()
        self.verify_limits()

    def verify_limits(self):
        now = datetime.now()
        results = self.getValues()
        self.info_messages.append('Displaying Sync status for '
                                  'Stratum0 - Stratum 1 @ %s' % now)
        header = "%-30s%-15s%-22s" % ('Statum0-rev', 'Statum1-rev',
                                      'Statum1-status')
        self.info_messages.append(header)
        data = results['last']
        should_alert = self.shouldAlert(results)
        if (int(data['stratum0_rev']) - 4 > int(data['stratum1_rev'])):
            if data['status'] != "synchz" or  data['status'] != "No Stratum1":
                msg = 'Stratum 0 - Stratum 1 is out of sync @ %s' % now
                if should_alert:
                    Emailer.Send(msg)
                    self.updateAlerted(data)
        elif self.isAlerted(results):
            msg = "Stratum 0 - Stratum 1 is in sync now @ %s " % now
            Emailer.Send(msg, backToNrormal=True)
            self.updateAlerted(data, hasBeenAlerted=False)
        msg = "%-30s%-15s%-22s" % (data['stratum0_rev'], data['stratum1_rev'],
                                   data['status'])
        self.info_messages.append(msg)

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
            'measurement': "stratum0_1_sync",
            'tags': {
                'day': results['day']
            },
            "time": results['time'],
            'fields': {
                'stratum0_rev': results['stratum0_rev'],
                'stratum1_rev': results['stratum1_rev'],
                'status': results['status'],
                'is_alerted': hasBeenAlerted,
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
        to_return = {}
        query = 'select * from stratum0_1_sync WHERE day=\'%s\';'
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
        now = datetime.now()
        current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        repo = 'lhcbdev.cern.ch'
        if os.environ.get('CVMFS_REPO_NAME', None):
            repo = os.environ['CVMFS_REPO_NAME']
        command = ["./bin/cvmfs_info", "-j", repo]
        output = ""
        try:
            proc = subprocess.Popen(command, shell=False, bufsize=1,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            first_pass = True
            while (True):
                line = proc.stdout.readline()
                try:
                    line = line.decode()
                except:
                    line = str(line)
                if line == "":
                    break
                if line.startswith('-->'):
                    first_pass = False
                    continue
                if not first_pass:
                    output += line
        except Exception as e:
            self.messages.append("Failed to check logs: %s" % e)
        try:
            output = json.loads(output)
            rev_stratum0 = int(output[0]['raw_revision'])
            if len(output) > 1:
                rev_stratum1 = int(output[1]['raw_revision'])
                status_stratum1 = output[1]['status']
            else:
                rev_stratum1 = 0
                status_stratum1 = 'No Stratum1'

            db_entries = []
            db_entry = {
                'measurement': "stratum0_1_sync",
                'tags': {
                    'day': now.strftime('%Y-%m-%d')
                },
                "time": current_time,
                'fields': {
                    'stratum0_rev': rev_stratum0,
                    'stratum1_rev': rev_stratum1,
                    'status': status_stratum1,
                    'is_alerted': False,
                    'back_to_normal': False,
                }
            }
            db_entries.append(db_entry)
            self.connector.write_points(db_entries)
        except Exception as e:
            self.messages.append("Failed to check logs: %s" % e)
