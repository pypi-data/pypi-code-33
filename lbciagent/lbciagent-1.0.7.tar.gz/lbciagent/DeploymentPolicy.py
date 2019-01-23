import lbmessaging
import os
import re
import pkg_resources
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen
from datetime import datetime
import json


priority_platforms = None


def _sortPlatformsForToday():
    url = "https://lhcb-couchdb.cern.ch/nightlies-nightly/_design/summaries/" \
          "_view/byDay?key=\"%s\"" % datetime.now().strftime("%Y-%m-%d")
    response = urlopen(url)
    raw_data = json.loads(response.read().decode('utf-8'))
    today_slot_platforms = {}
    for row in raw_data['rows']:
        slot_name = row['value']['slot']
        platforms = row['value']['platforms']
        platforms.sort(key=_platform_sort_key, reverse=True)
        today_slot_platforms[slot_name] = platforms[0]
    return today_slot_platforms


def _platform_sort_key(platform):
    '''
    Key function to sort platforms.
    The preferred platform has highest score.
    '''
    if '-' not in platform:
        os_id, arch, comp = platform.split('_')
        arch = {'ia32': 'i686', 'amd64': 'x86_64'}.get(arch, arch)
        opt = 'opt'
    else:
        arch, os_id, comp, opt = platform.split('-')
    # We need to force SLC6 as primary os_id since lxplus is based on SLC6
    if os_id == 'slc6':
        os_id = tuple([999, ])
    else:
        os_id = tuple(int(i) for i in os_id if i.isdigit())
    comp = tuple(int(i) for i in comp if i.isdigit())
    return ('0' if opt == 'do0' or arch != 'x86_64'
            else opt, arch, os_id, comp)


def isPriorityPlatform(slot, platform):
    global priority_platforms
    if priority_platforms is None:
        priority_platforms = _sortPlatformsForToday()
    return priority_platforms.get(slot, 'None') == platform


def computePriority(slot, platform):
    """
    Computes the priority of a slot / platform
    :return: the lbmessaging normalized priority
    """
    slots_to_install = _getSlots()

    # Compute slot priority
    try:
        slot_position = slots_to_install.index(slot)
    except:
        slot_position = len(slots_to_install)
    len_positions = len(slots_to_install)

    # Normalized priority of the whole slot, taking into account its
    # position in the list
    slot_priority = (len_positions - slot_position) * 1.0 / len_positions

    # If the platform has high priority, to ensure that it gets i
    # nstalled straight away,
    # we force the prio to be in [0.5, 1]
    # Otherwise the priority is half teh slot_priority (therefore in [0, 0.5]
    priority = slot_priority / 2.0
    if isPriorityPlatform(slot, platform):
        priority += 0.5
    return lbmessaging.priority(lbmessaging.LOW, priority)


def _getSlots():
    """ Util function to get slots of interest from conf file """
    slotfile = pkg_resources.resource_filename(__name__, "slotsOnCVMFS")

    slots = []
    with open(slotfile) as f:
        for l in f.readlines():
            if re.match("^\s*#", l):
                continue
            else:
                slots.append(l.rstrip())
    return slots
