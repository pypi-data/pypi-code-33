import os
import re
import datetime
from LbNightlyTools import Dashboard


def _getConfDir():
    return os.path.join(os.environ["HOME"],  "conf")


def getSlots(slotfile=None):
    """ Util function to get slots of interest from conf file """
    if slotfile is None:
        slotfile = os.path.join(_getConfDir(), "slots_on_cvmfs.txt")

    slots = []
    with open(slotfile) as f:
        for l in f.readlines():
            if re.match("^\s*#", l):
                continue
            else:
                slots.append(l.rstrip())
    return slots


def getSlotsDict():
    dash = Dashboard()
    strdate = datetime.datetime.now().strftime("%Y-%m-%d")
    slots_to_install = getSlots()
    allSlotsInfo = [
        (row.key, row.doc['slot'], row.doc['build_id'],
         row.doc['config'].get('platforms', [])) for row in dash.db.view(
            'summaries/byDay', key=strdate, include_docs=True)]
    toReturn = {
        'afs': [],
        'cvmfs': []
    }
    for slot in allSlotsInfo:
        if slot[1] in slots_to_install:
            slot_name = slot[1]
            slot_build = slot[2]
            platforms = slot[3]
            for platform in platforms:
                isCompleted = False
                info = dash.db['{0}.{1}'.format(slot_name, slot_build)]
                projects = set(p['name'] for p in info['config']['projects']
                               if p['name'] != 'info')
                for tplatform, builds in info.get('builds', {}).items():
                    if tplatform == platform:
                        completed = set(
                                project for project in builds
                                if 'completed' in builds[project] and
                                project != 'info')
                        isCompleted = True
                        for p in projects:
                            if p not in completed:
                                isCompleted = False
                d = {
                    'slot': slot_name,
                    'build_id': slot_build,
                    'platform': platform,
                    'completed': isCompleted
                }
                toReturn['cvmfs'].append(d)
    return toReturn

