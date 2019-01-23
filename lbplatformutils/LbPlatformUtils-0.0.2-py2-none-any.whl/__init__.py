#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Utility functions for platform detection and compatibility mapping.
'''
import platform
import sys
import os

try:
    from pkg_resources import get_distribution, DistributionNotFound
    try:
        __version__ = get_distribution(__name__).version
    except DistributionNotFound:  # pragma: no cover
        # package is not installed
        __version__ = 'unknown'
except ImportError:  # pragma: no cover
    __version__ = None

# map reference OSs to equivalent ones
OS_EQUIVALENCE = {
    'centos7': ['sl7', 'redhat7', 'suse42'],
    'slc6': ['sl6', 'centos6', 'redhat6'],
    'slc5': ['sl5', 'centos5', 'redhat5'],
    'ubuntu1604': [],
    'ubuntu1610': [],
    'ubuntu1704': [],
    'ubuntu1710': [],
}

# define compatibility between reference OSs:
# - the OS in the key can run binaries built for the OSs in the value list
# - compatibility is meant to be transitive (if A can run B, and B can run C,
#   then A can run C) unless the entry in the list starts with '!' (e.g.
#   {'A': ['B', '!C'], 'B': ['C']} means that A cannot run C even if B can)
OS_COMPATIBILITY = {
    'centos7': ['slc6'],
    'slc6': ['slc5'],
    'slc5': ['slc4'],
}

# define compatibility between CPU architectures:
# - the architecture in the key can run binaries built for the architecture in
#   the value list
# - compatibility is meant to be transitive (if A can run B, and B can run C,
#   then A can run C) unless the entry in the list starts with '!' (e.g.
#   {'A': ['B', '!C'], 'B': ['C']} means that A cannot run C even if B can)
ARCH_COMPATIBILITY = {
    'x86_64': ['i686'],
    'aarch64': []
}

# normalization for some architectures that are never used explicitely
ARCH_ALIASES = {
    'i386': 'i686'
}

# known microarchitecture feature in order of inclusion (the 1st is a superset
# of the 2nd, etc.)
MICROARCH_LEVELS = ['avx2+fma', 'avx2', 'avx', 'sse4_2']

# mapping between known binary tags (i.e. CMTCONFIG values) and minimum
# required platform (only special cases, the default is the second component
# of the BINARY_TAG)
BINARY_TAG_REQUIREMENTS = {
    'x86_64-centos7-gcc62': 'x86_64.centos7.sse4_2',
    'x86_64-slc6-gcc62': 'x86_64.slc6.sse4_2',
}


# ==== begin: Code duplicatied from Gaudi
#   https://gitlab.cern.ch/gaudi/Gaudi/blob/v28r2/cmake/get_host_binary_tag.py

def _Linux_os():
    dist = platform.linux_distribution(full_distribution_name=False)
    dist_name = dist[0].lower()
    dist_version = dist[1]
    if dist_name in ('redhat', 'centos'):
        rh_rel = open('/etc/%s-release' % dist_name).read().strip()
        if 'CERN' in rh_rel:
            dist_name = 'slc'
        elif 'Scientific Linux' in rh_rel:
            dist_name = 'sl'
        dist_version = dist_version.split('.', 1)[0]
    elif dist_name == 'suse':
        dist_version = dist_version.split('.', 1)[0]
    elif dist_name == 'debian':
        dist_version = dist_version.split('.', 1)[0]
        # there's a problem with vanilla Python not recognizing Ubuntu
        # see https://sft.its.cern.ch/jira/browse/SPI-961
        try:
            for l in open('/etc/lsb-release'):
                if l.startswith('DISTRIB_ID='):
                    dist_name = l.strip()[11:].lower()
                elif l.startswith('DISTRIB_RELEASE='):
                    dist_version = l.strip()[16:]
        except IOError:
            pass  # lsb-release is missing
    if dist_name == 'ubuntu':
        dist_version = dist_version.replace('.', '')
    return dist_name + dist_version


def _Darwin_os():
    version = platform.mac_ver()[0].split('.')
    return 'macos' + ''.join(version[:2])


def _Windows_os():
    return 'win' + platform.win32_ver()[1].split('.', 1)[0]


def _unknown_os():
    return 'unknown'


os_id = globals().get('_%s_os' % platform.system(), _unknown_os)

# ==== end: Code duplicatied from Gaudi


def architecture():
    '''
    Return the host CPU architecture, taking into account aliases.
    '''
    arch = platform.machine() or 'unknown'
    return ARCH_ALIASES.get(arch, arch)


def dirac_platform():
    '''
    Inspect the system to return an identifier summarizing system capabilities.
    '''
    system = platform.system()

    arch = architecture()

    short_id = os_id()

    # map the short name and version to a supported platform id
    if short_id not in OS_EQUIVALENCE:
        # not a reference platform
        for k, v in OS_EQUIVALENCE.items():
            if short_id in v:
                short_id = k
                break
        else:
            # not supported nor equivalent
            return arch + '.unknown'

    microarch = ''
    if system == 'Linux':
        cpuinfo = open('/proc/cpuinfo')
        flags = set()
        for l in cpuinfo:
            if l.startswith('flags'):
                flags = set(l.split(':', 1)[1].split())
                break
        for f in MICROARCH_LEVELS:
            if flags.issuperset(f.split('+')):
                microarch = f
                break

    return '.'.join(bit for bit in [arch, short_id, microarch] if bit)


def requires(binary_tag):
    '''
    Return the minimum required platform for a binary_tag.
    '''
    binary_tag = binary_tag.split('-')
    if '+' in binary_tag[0]:
        # explicit microarch
        arch, microarch = binary_tag[0].split('+', 1)
        return '.'.join([arch, binary_tag[1], microarch])
    # we try to match the prefix of the binary_tag
    for sub in ['-'.join(binary_tag[:n])
                for n in range(len(binary_tag), 0, -1)]:
        if sub in BINARY_TAG_REQUIREMENTS:
            return BINARY_TAG_REQUIREMENTS[sub]
    return '.'.join(binary_tag[0:2])  # require plain arch.OS


def _split_platform(platf):
    '''
    Split a dirac platform in a tuple (os, microarch), where microarch is None
    if not specified.

    >>> _split_platform('i686.slc5')
    ('i686', 'slc5', None)
    >>> _split_platform('x86_64.centos7.avx2')
    ('x86_64', 'centos7', 'avx2')
    '''
    platf = platf.split('.', 2)
    if len(platf) == 2:  # no microarch
        platf.append(None)
    return tuple(platf)


def check_compatibility(a, b, compatibility_map):
    '''
    Check if 'a' is compatible with 'b' according to the compatibility map.

    The compatibility_map must be a mapping from string to list of supported
    or unsupported (when prefixed with '!') strings.
    Compatibilty is transitive.

    As a special case, something is always compatible with itself even if not
    explicitly declared in the map.

    >>> compatibility_map = {'new': ['old', '!too_old'],
    ...                      'old': ['older', 'too_old']}
    >>> check_compatibility('new', 'old', compatibility_map)
    True
    >>> check_compatibility('new', 'older', compatibility_map)
    True
    >>> check_compatibility('new', 'too_old', compatibility_map)
    False
    '''
    if a != b:
        allowed = compatibility_map.get(a, [])
        if '!' + b in allowed:  # explicitely disallowed
            return False
        if b not in allowed:  # not explicitely allower, recurse
            fallback = [alt for alt in allowed if not alt.startswith('!')]
            if not any(check_compatibility(f, b, compatibility_map)
                       for f in fallback):
                return False
    return True


def can_run(current, required):
    '''
    Tell if the current platform meets the constraints of the required one.
    '''
    current_arch, current_os, current_microarch = _split_platform(current)
    required_arch, required_os, required_microarch = _split_platform(required)
    if 'unknown' in (current_os, required_os, current_arch, required_arch):
        return False  # we do not have enough information
    # check arch and os
    if not (check_compatibility(current_arch, required_arch,
                                ARCH_COMPATIBILITY) and
            check_compatibility(current_os, required_os,
                                OS_COMPATIBILITY)):
        return False
    # check microarch
    # (note: if nothing is required, anything fits)
    if required_microarch is None or required_microarch == current_microarch:
        return True
    if required_microarch not in MICROARCH_LEVELS:
        return False  # we do not know anything about the required microarch
    if current_microarch not in MICROARCH_LEVELS:
        # at this point, required is something we know (and not None), so,
        # if current is not known or None, it's not compatible
        return False
    # what remains to check is if current includes required, according to the
    # order in MICROARCH_LEVELS
    return (MICROARCH_LEVELS.index(current_microarch) <=
            MICROARCH_LEVELS.index(required_microarch))
