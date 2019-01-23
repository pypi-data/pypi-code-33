import os
import re
import urllib2
import json


class Utils:

    @staticmethod
    def cmpList(x):
        if x[4] == '':
            return '9999-99-99 99:99:99'
        return x[4]

    @staticmethod
    def getSlots():
        """ Util function to get slots of interest from conf file """
        slotfile = os.path.join(os.environ.get("HOME"), "conf",
                                "slots_on_cvmfs.txt")

        slots = []
        with open(slotfile) as f:
            for l in f.readlines():
                if re.match("^\s*#", l):
                    continue
                else:
                    slots.append(l.rstrip())
        return slots

    @staticmethod
    def getSlotsProjects(date):
        shouldInstall = {}
        url = "https://lhcb-couchdb.cern.ch/nightlies-nightly/_design/" \
              "deployment/_view/ready?key=[\"%s\",\"cvmfs\"]" \
              "&include_docs=true" % date
        response = urllib2.urlopen(url)
        slots = json.loads(response.read())
        for slot in slots['rows']:
            shouldInstall[slot['doc']['slot']] = {'projects': [],
                                                  'platforms': []}
            for platform_row in slot['value']:
                shouldInstall[slot['doc']['slot']]['platforms'].append(
                    platform_row['platform'])
            counter = 0
            while True:
                if counter == len(
                        shouldInstall[slot['doc']['slot']]['platforms']):
                    break
                platform_0 = shouldInstall[slot['doc']['slot']]['platforms'][
                    counter]
                try:
                    for project in slot['doc']['builds'][platform_0].keys():
                        if project != 'info':
                            shouldInstall[slot['doc']['slot']][
                                'projects'].append(project)
                    break
                except:
                    counter += 1
        return shouldInstall


