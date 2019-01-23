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
__all__ = ('os_id', 'architecture', 'compiler_id')

import os
import re
import platform
try:
    from subprocess import check_output, STDOUT, CalledProcessError
except ImportError:  # pragma no cover
    # check_output was introduced in Python 2.7
    from subprocess import STDOUT, CalledProcessError

    def check_output(*args, **kwargs):
        '''
        Minimal packport to Python 2.6 of check_output.
        '''
        from subprocess import Popen, PIPE
        kwargs['stdout'] = PIPE
        proc = Popen(*args, **kwargs)
        out_err = proc.communicate()
        if proc.returncode:
            raise CalledProcessError(proc.returncode, args[0])
        return out_err


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
    elif dist_name == '':
        # Fall back on a generic Linux build if distribution detection fails
        dist_name = 'linux'
    return dist_name + dist_version


def _Darwin_os():
    version = platform.mac_ver()[0].split('.')
    return 'macos' + ''.join(version[:2])


def _Windows_os():
    return 'win' + platform.win32_ver()[1].split('.', 1)[0]


def _unknown_os():
    return 'unknown'


os_id = globals().get('_%s_os' % platform.system(), _unknown_os)


def architecture():
    '''
    Return the host CPU architecture, taking into account aliases.
    '''
    from LbPlatformUtils import normal_name, ARCH_ALIASES
    return normal_name(platform.machine() or 'unknown', ARCH_ALIASES)


def model_name():
    '''
    Return CPU model name from /proc/cpuinfo.
    '''
    if os.path.exists('/proc/cpuinfo'):
        cpuinfo = open('/proc/cpuinfo')
        for l in cpuinfo:
            if l.startswith('model name'):
                return l.split(':', 1)[1].strip()
    return 'unknown'


def microarch_flags():
    '''
    Return a set with all microarchitecture flags from /proc/cpuinfo.
    '''
    flags = set()
    if os.path.exists('/proc/cpuinfo'):
        cpuinfo = open('/proc/cpuinfo')
        for l in cpuinfo:
            if l.startswith('flags'):
                flags = set(l.split(':', 1)[1].split())
                break
    return flags


def compiler_id(cmd=os.environ.get('CC', 'cc')):
    '''
    Return id of system compiler.
    '''
    # prevent interference from localization
    env = dict(os.environ)
    env['LC_ALL'] = 'C'
    try:
        m = re.search(r'(gcc|clang|icc|LLVM) version (\d+)\.(\d+)',
                      check_output([cmd, '-v'],
                                   stderr=STDOUT, env=env).decode('utf-8'))
        comp = 'clang' if m.group(1) == 'LLVM' else m.group(1)
        vers = m.group(2)
        if (comp == 'gcc' and int(vers) < 7) or comp == 'clang':
            vers += m.group(3)
        return comp + vers
    except (AttributeError, CalledProcessError, OSError):
        # prevent crashes if the compiler is not supported or not present
        return 'unknown'
