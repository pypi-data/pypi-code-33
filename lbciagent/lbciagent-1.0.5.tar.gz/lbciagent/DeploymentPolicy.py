import lbmessaging
import os
import re
import pkg_resources


priority_platforms = {
    'lhcb-head': 'x86_64-centos7-gcc7-opt',
    'lhcb-sim09': 'x86_64-slc6-gcc49-opt',
    'lhcb-2018-patches': 'x86_64-centos7-gcc7-opt',
    'lhcb-gaudi-head': 'x86_64-centos7-gcc7-opt',
    'lhcb-tdr-test': 'x86_64-centos7-gcc7-opt',
    'lhcb-run2-patches': 'x86_64-centos7-gcc7-opt',
    'lhcb-gauss-dev': 'x86_64-centos7-gcc7-opt',
    'lhcb-sim09-upgrade': 'x86_64-slc6-gcc49-opt',
    'lhcb-2017-patches': 'x86_64-centos7-gcc62-opt',
    'lhcb-2016-patches': 'x86_64-slc6-gcc49-opt',
    'lhcb-lcg-dev3': 'x86_64-centos7-gcc7-opt',
    'lhcb-lcg-dev4': 'x86_64-centos7-gcc7-opt',
    'lhcb-gauss-newgen': 'x86_64-slc6-gcc49-opt',
    'lhcb-clang-test': 'x86_64-centos7-clang50-opt',
    'lhcb-reco14-patches': 'x86_64-slc5-gcc46-opt',
    'lhcb-stripping21-patches': 'x86_64-slc6-gcc48-opt',
    'lhcb-stripping24-patches': 'x86_64-slc6-gcc49-opt'
}


def isPriorityPlatform(slot, platform):
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
