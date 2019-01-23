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
Simple script to describe the platform.
'''


import os
import sys


BINARY_TAGS_CACHE = ('/cvmfs/lhcb.cern.ch/lib/var/cache/LbPlatformUtils/'
                     'all_platforms.json')
BINARY_TAGS_URL = ('https://lhcb-couchdb.cern.ch/nightlies-release'
                   '/_design/names/_view/platforms?group=true')


def allBinaryTags(path=None):
    '''
    Return the list of known binary tags, either from a cache in /cvmfs or from
    the release builds database.
    '''
    import json

    if path is not None:
        btags = open(path)
    elif os.path.exists(BINARY_TAGS_CACHE):
        btags = open(BINARY_TAGS_CACHE)
    else:
        import urllib.request, urllib.error, urllib.parse
        btags = urllib.request.urlopen(BINARY_TAGS_URL)

    data = btags.read()
    if hasattr(data, 'decode'):
        data = data.decode()
    platforms_data = json.loads(data)
    # the check `if '-' in p['key']` is meant to hide obsolete platform names
    # like slc4_ia32_gcc34
    return [p['key'] for p in platforms_data.get('rows') if '-' in p['key']]


def main(args=None):
    '''
    Simple script to describe the platform.
    '''
    try:  # pragma no cover
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--platforms-list',
                            help='path to a file containing the list of '
                            'plaltforms (see {} for the format)'.format(
                                BINARY_TAGS_URL
                            ))
        args = parser.parse_args(args)
    except ImportError:  # pragma no cover
        import optparse
        parser = optparse.OptionParser()
        parser.add_option('--platforms-list',
                          help='path to a file containing the list of '
                          'plaltforms (see {0} for the format)'.format(
                              BINARY_TAGS_URL
                          ))
        args = parser.parse_args(args)[0]

    import LbPlatformUtils as lpu

    if lpu.__version__:
        print('LbPlatformUtils version: {0}'.format(lpu.__version__))

    dirac_platform = lpu.dirac_platform()

    print('dirac_platform: {0}'.format(dirac_platform))

    print('arch: {0}'.format(lpu.architecture()))
    print('os_id: {0}'.format(lpu.os_id()))

    lines = ['compatible_binary_tags:']
    lines.extend(btag for btag in allBinaryTags(args.platforms_list)
                 if lpu.can_run(dirac_platform, lpu.requires(btag)))
    print('\n  - '.join(lines))
