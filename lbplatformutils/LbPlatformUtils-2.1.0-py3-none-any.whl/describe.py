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

BINARY_TAGS_CACHE = ('/cvmfs/lhcb.cern.ch/lib/var/lib/platforms-list.json')
BINARY_TAGS_URL = ('https://lhcb-couchdb.cern.ch/nightlies-release'
                   '/_design/names/_view/platforms?group=true')


def allBinaryTags(path=None):
    '''
    Return the list of known binary tags, either from a cache in /cvmfs or from
    the release builds database.
    '''
    import json

    try:
        if path is not None:
            btags = open(path)
        elif os.path.exists(BINARY_TAGS_CACHE):
            btags = open(BINARY_TAGS_CACHE)
        else:
            import urllib.request, urllib.error, urllib.parse
            btags = urllib.request.urlopen(BINARY_TAGS_URL)
        data = btags.read()
    except (ImportError, urllib.error.URLError, IOError):
        import pkg_resources
        data = pkg_resources.resource_string('LbPlatformUtils',
                                             'platforms-list.json')

    if hasattr(data, 'decode'):
        data = data.decode()
    platforms_data = json.loads(data)
    # the check `if '-' in p['key']` is meant to hide obsolete platform names
    # like slc4_ia32_gcc34
    return [p['key'] for p in platforms_data.get('rows') if '-' in p['key']]


def platform_info(all_binary_tags=None):
    '''
    Return a dictionary with all details about the host platform.
    '''
    import LbPlatformUtils as lpu
    import LbPlatformUtils.inspect as inspect

    info = {}
    if all_binary_tags is None:
        all_binary_tags = allBinaryTags()

    if lpu.__version__:
        info['LbPlatformUtils version'] = lpu.__version__

    dirac_platform = lpu.dirac_platform()

    info['dirac_platform'] = dirac_platform
    info['host_os'] = lpu.host_os()
    info['host_binary_tag'] = lpu.host_binary_tag()
    info['os_id'] = inspect.os_id()
    info['arch'] = inspect.architecture()
    info['model'] = inspect.model_name()
    info['flags'] = sorted(inspect.microarch_flags())

    info['compatible_binary_tags'] = [
        btag for btag in all_binary_tags
        if lpu.can_run(dirac_platform, lpu.requires(btag))
    ]

    info['container_technology'] = {}
    info['container_technology']['singularity'] = dict((path, [
        btag for btag in all_binary_tags
        if lpu.can_run(lpu.dirac_platform(force_os=os_id), lpu.requires(btag))
    ]) for path, os_id in inspect.singularity_os_ids())

    return info


def main(args=None):
    '''
    Simple script to describe the platform.
    '''
    try:  # pragma no cover
        from argparse import ArgumentParser
    except ImportError:  # pragma no cover
        import optparse
        optparse.OptionParser.add_argument = optparse.OptionParser.add_option
        optparse.OptionParser.parse_args_ = optparse.OptionParser.parse_args
        optparse.OptionParser.parse_args = (
            lambda self, *args, **kwargs: self.parse_args_(*args, **kwargs)[0])
        ArgumentParser = optparse.OptionParser

    parser = ArgumentParser()
    parser.add_argument(
        '--platforms-list',
        help='path to a file containing the list of '
        'platforms (see {} for the format)'.format(BINARY_TAGS_URL))
    parser.add_argument(
        '--flags',
        action='store_true',
        help='also print the list of microarchitecture '
        'flags')
    parser.add_argument(
        '--raw',
        action='store_true',
        help='print a raw dictionary instead of a YAML-like format')
    args = parser.parse_args(args)

    info = platform_info(allBinaryTags(args.platforms_list))

    if args.raw:
        if not args.flags:
            del info['flags']
        from pprint import pprint
        pprint(info)
        return

    # To have a stable printout across versions of the script we hardcode
    # the order and items we want to print
    print('LbPlatformUtils version: {0}'.format(
        info['LbPlatformUtils version']))

    print('\n'.join('{0}: {1}'.format(key, info[key]) for key in [
        'dirac_platform',
        'host_os',
        'host_binary_tag',
        'os_id',
        'arch',
        'model',
    ]))

    if args.flags:
        print('flags:', *info['flags'], sep='\n  - ')

    print(
        'compatible_binary_tags:',
        *info['compatible_binary_tags'],
        sep='\n  - ')

    if info['container_technology']['singularity']:
        print('  singularity:')
        for path, btags in list(info['container_technology']['singularity'].items()):
            if btags:
                print('    {0}:'.format(path), *btags, sep='\n      - ')


def host_binary_tag_script(args=None):
    '''
    Simple script to print the host binary tag string.
    '''
    try:  # pragma no cover
        import argparse
        parser = argparse.ArgumentParser(
            description='print default host binary tag string')
        args = parser.parse_args(args)
    except ImportError:  # pragma no cover
        import optparse
        parser = optparse.OptionParser(
            description='print default host binary tag string')
        args = parser.parse_args(args)[0]
    from LbPlatformUtils import host_binary_tag
    print(host_binary_tag())
