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


class NightliesRemoval(PluginBase):

    def __init__(self):
        super(NightliesRemoval, self).__init__()
        self.connector = getConnector()
        self.pwd = '/cvmfs/lhcbdev.cern.ch/nightlies'
        self.maxnbperslot = 9

    def execute(self):
        self._check_install()
        self.verify_limits()

    def verify_limits(self):
        now = datetime.now()
        results = self.getValues()
        self.info_messages.append('Displaying all slots checks at %s' % now)
        header = "%-30s%-15s%-22s" % ('Slot', 'Number of links',
                                      'Total number of builds')
        self.info_messages.append(header)
        self.error_messages = []
        should_alert = False
        for slot in results.keys():
            data = results[slot]['last']
            local_should_alert = self.shouldAlert(results[slot])
            msg = "%-30s%-15s%-22s" % (
                slot, data['current_links'], data['total_slots'])
            self.info_messages.append(msg)
            todays_builds = self.getTodaysBuilds(os.path.join(self.pwd, slot))
            if int(data['total_slots']) > (self.maxnbperslot + todays_builds):
                msg = 'For slot %s we have %s builds out ' \
                      'of which %s are symlinks' % (slot,
                                                    data['total_slots'],
                                                    data['current_links'])
                self.messages.append(msg)
                if local_should_alert:
                    self.error_messages.append(msg)
                    self.updateAlerted(data)
            elif self.isAlerted(results[slot]):
                msg = "Back to normal for %s" % slot
                Emailer.Send(msg, backToNrormal=True)
                self.updateAlerted(data, hasBeenAlerted=False)
                local_should_alert = False
            else:
                local_should_alert = False
            should_alert = should_alert or local_should_alert
        if should_alert:
            Emailer.Send('\n'.join(self.error_messages))

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
            'measurement': "nightlies_removeal",
            'tags': {
                'slot': results['slot'],
                'day': results['day']
            },
            "time": results['time'],

            'fields': {
                'current_links': results['current_links'],
                'is_alerted': hasBeenAlerted,
                'total_slots': results['total_slots'],
                'back_to_normal': not(hasBeenAlerted),
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
        for slot in os.listdir(self.pwd):
            query = 'select * from nightlies_removeal ' \
                    'WHERE day=\'%s\' and slot=\'%s\';'
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

    def getTodaysBuilds(self, slotdir):
        counter = 0
        for f in os.listdir(slotdir):
            created_time = os.path.getmtime(os.path.join(slotdir, f))
            created_time = time.ctime(created_time)
            d = datetime.strptime(
                created_time, "%a %b %d %H:%M:%S %Y")
            if d.date() == datetime.now().date():
                counter += 1
        return counter

    def listBuildsInDir(self, slotdir):
        """ List all the builds installed in a given dir
            and returns a triplet(buildId, date, isLinked) """
        buildIds = [f for f in os.listdir(slotdir)
                    if not os.path.islink(os.path.join(slotdir, f))]
        # List builds which are target of a loink therefore cannot be removed
        linkTargets = set()
        for f in os.listdir(slotdir):
            fp = os.path.join(slotdir, f)
            if os.path.islink(fp):
                linkTargets.add(os.readlink(fp))
        retinfo = [(f, os.path.join(slotdir, f),
                    os.path.getctime(os.path.join(slotdir, f)),
                    f in linkTargets)
                   for f in buildIds]

        # Returns a list of tuples containing:
        # (buildId, full path, creation time, is target of a link)
        def cast(tup):
            retval = 0
            try:
                retval = int(tup[0])
            except ValueError:
                pass
            return retval
        return sorted(retinfo, key=cast, reverse=True)

    def _check_install(self):
        now = datetime.now()
        current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        db_entries = []
        allSlots = os.listdir(self.pwd)
        for slot in allSlots:
            apath = os.path.join(self.pwd, slot)
            allbuilds = self.listBuildsInDir(apath)
            nbTotal = len(allbuilds)
            nbForceKept = len([t for t in allbuilds if t[3]])
            db_entry = {
                'measurement': "nightlies_removeal",
                'tags': {
                    'slot': slot,
                    'day': now.strftime('%Y-%m-%d')
                },
                "time": current_time,
                'fields': {
                    'current_links': '%s' % nbForceKept,
                    'is_alerted': False,
                    'total_slots': '%s' % nbTotal,
                    'back_to_normal': False,
                }
            }
            db_entries.append(db_entry)
        self.connector.write_points(db_entries)
