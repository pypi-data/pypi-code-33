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

Part of the code was imported from Gaudi and inspired by
* https://github.com/HEP-SF/documents/tree/master/HSF-TN/draft-2015-NAM
* https://github.com/HEP-SF/tools
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
OS_ALIASES = {
    'centos7': ['sl7', 'redhat7', 'suse42', 'suse15'],
    'slc6': ['sl6', 'centos6', 'redhat6'],
    'slc5': ['sl5', 'centos5', 'redhat5'],
    'ubuntu1604': [],
    'ubuntu1610': [],
    'ubuntu1704': [],
    'ubuntu1710': [],
    'ubuntu1804': [],
}

# map reference architectures to equivalent ones
ARCH_ALIASES = {
    'i686': ['i386'],
    'x86_64': ['AMD64'],  # Windows architecture name
}

# define compatibility between reference OSs:
# - the OS in the key can run binaries built for the OSs in the value list
# - compatibility is meant to be transitive (if A can run B, and B can run C,
#   then A can run C) unless the entry in the list starts with '!' (e.g.
#   {'A': ['B', '!C'], 'B': ['C']} means that A cannot run C even if B can)
OS_COMPATIBILITY = {
    'centos7': ['slc6', '!slc5'],
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

# known microarchitecture feature in order of inclusion (the 1st is a superset
# of the 2nd, etc.)
MICROARCH_LEVELS = ['avx2+fma', 'avx2', 'avx', 'sse4_2']

# mapping between known binary tags (i.e. CMTCONFIG values) and minimum
# required platform (only special cases, the default is the second component
# of the BINARY_TAG)
BINARY_TAG_REQUIREMENTS = {
    'x86_64-centos7-gcc62': 'x86_64-centos7.sse4_2',
    'x86_64-slc6-gcc62': 'x86_64-slc6.sse4_2',
}


def normal_name(name, aliases, default=None):
    '''
    Return the _normalized_ name corresponding to the requested one, based on
    the aliases list.  If not found return the original name, or, if specified,
    'default'.

    >>> aliases = {'a': ['1', '2', '3'],
    ...            'b': []}
    >>> normal_name('2', aliases)
    'a'
    >>> normal_name('b', aliases)
    'b'
    >>> normal_name('c', aliases)
    'c'
    >>> normal_name('c', aliases, 'unknown')
    'unknown'
    '''
    if name in aliases:
        return name
    else:
        # not a reference platform
        for k, v in list(aliases.items()):
            if name in v:
                return k
        # not supported nor equivalent
        return default or name


def host_os():
    '''
    Return a string identifying host architecture and os, as '<arch>-<os_id>'.
    '''
    from LbPlatformUtils.inspect import architecture, os_id
    return '-'.join([architecture(), normal_name(os_id(), OS_ALIASES)])


def host_binary_tag():
    '''
    Return host binary tag string.

    See https://github.com/HEP-SF/documents/tree/master/HSF-TN/draft-2015-NAM
    '''
    from LbPlatformUtils.inspect import compiler_id
    return '-'.join([host_os(), compiler_id(), 'opt'])


def dirac_platform():
    '''
    Inspect the system to return an identifier summarizing system capabilities.
    '''
    from LbPlatformUtils.inspect import architecture, os_id, microarch_flags
    arch = architecture()
    short_id = normal_name(os_id(), OS_ALIASES, 'unknown')

    microarch = ''
    flags = microarch_flags()
    for f in MICROARCH_LEVELS:
        if flags.issuperset(f.split('+')):
            microarch = f
            break

    return arch + '-' + '.'.join(bit for bit in [short_id, microarch] if bit)


def requires(binary_tag):
    '''
    Return the minimum required platform for a binary_tag.
    '''
    binary_tag = binary_tag.split('-')
    if '+' in binary_tag[0]:
        # explicit microarch
        arch, microarch = binary_tag[0].split('+', 1)
        return '%s-%s.%s' % (arch, binary_tag[1], microarch)
    # we try to match the prefix of the binary_tag
    for sub in ['-'.join(binary_tag[:n])
                for n in range(len(binary_tag), 0, -1)]:
        if sub in BINARY_TAG_REQUIREMENTS:
            return BINARY_TAG_REQUIREMENTS[sub]
    return '-'.join(binary_tag[0:2])  # require plain arch.OS


def _split_platform(platf):
    '''
    Split a dirac platform in a tuple (os, microarch), where microarch is None
    if not specified.

    >>> _split_platform('i686-slc5')
    ('i686', 'slc5', None)
    >>> _split_platform('x86_64-centos7.avx2')
    ('x86_64', 'centos7', 'avx2')
    '''
    arch, rest = platf.split('-', 1)
    if '.' in rest:
        os, micro = rest.split('.', 1)
    else:
        os, micro = rest, None
    return (arch, os, micro)


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
