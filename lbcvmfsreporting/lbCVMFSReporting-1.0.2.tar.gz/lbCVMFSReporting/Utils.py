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
            shouldInstall[slot['doc']['slot']] = {
                'platforms': [str(p['platform']) for p in slot['value']],
                'projects': [str(p['name'])
                             for p in slot['doc']['config']['projects']
                             if not p['disabled']],
                'completed': [{'project': str(p['name']),
                               'is_build': p.get('completed', None) is not None}
                              for p in slot['doc']['config']['projects']
                              if not p['disabled']]
            }
        return shouldInstall


