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


class NightliesChecker(PluginBase):

    SLOTS_MAX_TIME = {
        'lhcb-future': "11:30:00",
        'lhcb-2017-patches': "11:30:00",
        'lhcb-gaudi-head': "10:30:00",
        'lhcb-head': "10:30:00",
    }

    SLOTS = [
        'lhcb-2016-patches',
        'lhcb-clang-test',
        'lhcb-compatibility',
        'lhcb-dirac',
        'lhcb-future',
        'lhcb-gaudi-head-noavx',
        'lhcb-gauss-cmake',
        'lhcb-gitconddb',
        'lhcb-lcg-dev3',
        'lhcb-master',
        'lhcb-old-stripping-tests',
        'lhcb-patches3',
        'lhcb-reco14-patches',
        'lhcb-sim09-upgrade',
        'lhcb-turbosp',
        'lhcb-2017-patches',
        'lhcb-compatibility-2',
        'lhcb-decfilestests',
        'lhcb-future-clang',
        'lhcb-g4r102',
        'lhcb-gaudi-head',
        'lhcb-gauss-dev',
        'lhcb-head',
        'lhcb-lcg-dev4',
        'lhcb-nightly-builds-test',
        'lhcb-patches2',
        'lhcb-prerelease',
        'lhcb-sim08',
        'lhcb-sim09']

    def __init__(self):
        super(NightliesChecker, self).__init__()
        self.connector = getConnector()
        self.pwd = '/cvmfs/lhcbdev.cern.ch/nightlies'

    def execute(self):
        self._check_install()
        self.verify_limits()

    def verify_limits(self):
        now = datetime.now()
        results = self.getValues()
        self.info_messages.append('Displaying all slots checks at %s' % now)
        header = "%-30s%-15s%-22s%-22s" % ('Slot', 'Is Created?',
                                           'Creation Time', 'Limit')
        self.info_messages.append(header)
        for slot in results.keys():
            data = results[slot]['last']
            requested_time = self.SLOTS_MAX_TIME.get(slot, None)
            if requested_time:
                should_alert = self.shouldAlert(results[slot])
                parsed_time = "%s-%s-%s %s" % (now.year, now.month, now.day,
                                               requested_time)
                parsed_time = datetime.strptime(parsed_time.strip(),
                                                '%Y-%m-%d %H:%M:%S')
                if now > parsed_time:
                    if not data['is_installed']:
                        msg = 'Today path was not created for %s ' \
                              '(time limit: %s) at %s' % (slot,
                                                          requested_time,
                                                          now)
                        self.messages.append(msg)
                        if should_alert:
                            Emailer.Send(msg)
                            self.updateAlerted(data)
                        continue
                    elif self.isAlerted(results[slot]):
                        msg = "%s (Time limit %s) is now installed " \
                              "at %s." % (slot, requested_time, now)
                        Emailer.Send(msg, backToNrormal=True)
                        self.updateAlerted(data, hasBeenAlerted=False)
                parsed_time = parsed_time.strftime('%Y-%m-%d %H:%M:%S  ')
            else:
                parsed_time = '%-22s' % ''
            if data['installed_time']:
                parsed_installed_time = datetime.strptime(
                    data['installed_time'], '%a %b %d %H:%M:%S %Y')

                tmp_parsed_installed_time = parsed_installed_time.strftime(
                    '%Y-%m-%d %H:%M:%S  ')
                msg = "%-30s%-15s%-22s%-22s" % (
                    slot, 'Yes', tmp_parsed_installed_time, parsed_time)
                self.info_messages.append(msg)
            else:
                msg = "%-30s%-15s%-22s%-22s" % (slot, 'No', '', parsed_time)
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
            'measurement': "nightlies",
            'tags': {
                'slot': results['slot'],
                'day': results['day']
            },
            "time": results['time'],
            'fields': {
                'is_installed': results['is_installed'],
                'is_alerted': hasBeenAlerted,
                'installed_time': results['installed_time'],
                'back_to_normal': not(hasBeenAlerted)
            }
        }

        self.connector.write_points([db_entry])

    def shouldAlert(self, results):
        for result in results['all']:
            if (result['is_alerted'] or result['installed_time']) is True:
                return False
        return True

    def getValues(self):
        now = datetime.now()
        to_return = {}
        for slot in self.SLOTS:
            query = 'select * from nightlies WHERE day=\'%s\' and slot=\'%s\';'
            query = query % (now.strftime('%Y-%m-%d'), slot)
            result = self.connector.query(query)
            all_results = list(result.get_points())
            last_result = all_results[0]
            for res in all_results[1:]:
                if res['time'] > last_result['time']:
                    last_result = res
            to_return[slot] = {
                'last': last_result,
                'all': all_results
            }
        return to_return

    def _check_install(self):
        now = datetime.now()
        current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        db_entries = []
        for slot in self.SLOTS:
            today_path = "%s/%s/Today" % (self.pwd, slot)
            db_entry = {
                'measurement': "nightlies",
                'tags': {
                    'slot': slot,
                    'day': now.strftime('%Y-%m-%d')
                },
                "time": current_time,
                'fields': {
                    'is_installed': False,
                    'is_alerted': False,
                    'installed_time': '',
                    'back_to_normal': False,
                }
            }

            if os.path.exists(today_path):
                created_time = os.path.getmtime(today_path)
                created_time = time.ctime(created_time)
                db_entry['fields']['is_installed'] = True
                db_entry['fields']['installed_time'] = created_time
            db_entries.append(db_entry)
        self.connector.write_points(db_entries)

