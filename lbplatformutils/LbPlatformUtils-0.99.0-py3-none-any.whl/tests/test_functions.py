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


def test_requires():
    from LbPlatformUtils import requires

    assert requires('i686-slc5-gcc43-opt') == 'i686.slc5'
    assert requires('x86_64-slc6-gcc49-opt') == 'x86_64.slc6'
    assert requires('x86_64-slc6-gcc62-opt') == 'x86_64.slc6.sse4_2'
    assert requires('x86_64+avx2+fma-centos7-gcc7-opt') == \
        'x86_64.centos7.avx2+fma'


def test_can_run():
    from LbPlatformUtils import can_run, OS_COMPATIBILITY

    assert can_run('x86_64.centos7', 'x86_64.centos7')
    assert can_run('x86_64.centos7', 'x86_64.slc6')
    assert can_run('x86_64.centos7', 'x86_64.slc5')

    assert can_run('x86_64.slc5', 'i686.slc5')

    assert can_run('x86_64.centos7.avx2+fma', 'x86_64.slc6.sse4_2')
    assert can_run('x86_64.centos7.avx2+fma', 'x86_64.slc6.avx2')

    assert can_run('x86_64.ubuntu1604.avx2+fma', 'x86_64.ubuntu1604')

    assert can_run('anything.anything', 'anything.anything')

    assert not can_run('anything.unknown', 'anything.anything')
    assert not can_run('unknonw.anything', 'anything.anything')

    assert not can_run('x86_64.slc5', 'x86_64.slc6')
    assert not can_run('x86_64.centos7.avx', 'x86_64.centos7.avx999')
    assert not can_run('x86_64.centos7', 'x86_64.centos7.avx2')

    OS_COMPATIBILITY['centos8'] = ['centos7', '!slc5']
    assert can_run('x86_64.centos8', 'x86_64.centos7')
    assert not can_run('x86_64.centos8', 'x86_64.slc5')


def test_compatibility():
    from LbPlatformUtils import check_compatibility

    compatibility_map = {'new': ['old', '!too_old'],
                         'old': ['older', 'too_old']}

    assert check_compatibility('stuff', 'stuff', compatibility_map)
    assert not check_compatibility('stuff', 'other_stuff', compatibility_map)
    assert check_compatibility('new', 'old', compatibility_map)
    assert check_compatibility('new', 'older', compatibility_map)
    assert not check_compatibility('new', 'too_old', compatibility_map)
