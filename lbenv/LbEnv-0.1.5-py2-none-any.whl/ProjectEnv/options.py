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
Common functions to add common options to a OptionParser instance.
'''
__author__ = 'Marco Clemencic <marco.clemencic@cern.ch>'

import os
import re

from LbEnv.ProjectEnv import SearchPathEntry, EnvSearchPathEntry, SearchPath


class LHCbDevPathEntry(EnvSearchPathEntry):
    def __init__(self):
        EnvSearchPathEntry.__init__(self, 'LHCBDEV')

    def __repr__(self):
        return '{0}()'.format(self.__class__.__name__)


class NightlyPathEntry(SearchPathEntry):
    def __init__(self, base, slot, day):
        self.base, self.slot, self.day = base, slot, day

    @property
    def path(self):
        return os.path.join(self.base, self.slot, self.day)

    def __str__(self):
        search_path = map(str, [self.path] + self.getNightlyExtraPath())
        return os.pathsep.join(search_path)

    def getNightlyExtraPath(self):
        extra_path = []
        path = self.path
        confSumm_file = os.path.join(path, 'confSummary.py')
        config_file = os.path.join(path, 'configuration.xml')
        if os.path.exists(
                confSumm_file):  # Try with the python digested version
            data = {'__file__': confSumm_file}
            exec open(confSumm_file).read() in data  # IGNORE:W0122
            # Get the list and convert it to strings
            extra_path = data.get('cmtProjectPathList', [])
        elif os.path.exists(config_file):  # Try with the XML configuration
            from LbEnv.ProjectEnv.compatibility import getNightlyCMTPROJECTPATH
            extra_path = getNightlyCMTPROJECTPATH(config_file, self.slot,
                                                  self.day)
        return map(SearchPathEntry, extra_path)

    def toCMake(self):
        return (
            '# Use the nightly builds search path if needed.\n'
            'if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/build.conf)\n'
            '  file(STRINGS ${CMAKE_CURRENT_SOURCE_DIR}/build.conf build_conf)\n'
            '  foreach(l ${build_conf})\n'
            '    if(l MATCHES "^ *([a-zA-Z_][a-zA-Z0-9_]*)=([^ ]*) *$$")\n'
            '      set(${CMAKE_MATCH_1} "${CMAKE_MATCH_2}")\n'
            '    endif()\n'
            '  endforeach()\n'
            'endif()\n'
            'if(NOT nightly_base)\n'
            '  set(nightly_base "$ENV{LHCBNIGHTLIES}")\n'
            'endif()\n'
            '\n'
            'if(nightly_slot)\n'
            '  if(EXISTS ${nightly_base}/${nightly_slot}/${nightly_day}/searchPath.cmake)\n'
            '    include(${nightly_base}/${nightly_slot}/${nightly_day}/searchPath.cmake)\n'
            '  endif()\n'
            '  list(INSERT CMAKE_PREFIX_PATH 0 "${nightly_base}/${nightly_slot}/${nightly_day}")\n'
            'endif()\n')

    def toCMT(self, shell='sh'):
        if shell == 'csh':
            return '''# Use the nightly builds search path if needed.
if ( -e build.conf ) then
    eval `sed -n '/^[^#]/{{s/^/set /;s/$/ ;/p}}' build.conf`
endif
if ( ! $?nightly_base ) then
    if ( $?LHCBNIGHTLIES ) then
        set nightly_base = "$LHCBNIGHTLIES"
    else
        set nightly_base = ""
    endif
endif

if ( $?nightly_slot && $?nightly_day ) then
    if ( $?CMTPROJECTPATH ) then
        set SAVED_CMTPROJECTPATH = ":$CMTPROJECTPATH"
    else
        set SAVED_CMTPROJECTPATH = ""
    endif
    if ( -e ${nightly_base}/${nightly_slot}/${nightly_day}/setupSearchPath.csh ) then
        source ${nightly_base}/${nightly_slot}/${nightly_day}/setupSearchPath.csh
    else
        setenv CMTPROJECTPATH "${nightly_base}/${nightly_slot}/${nightly_day}"
    endif
    # This a temporary work around because setupSearchPath.csh overrides CMTPROJECTPATH
    # instead of extending it.
    setenv CMTPROJECTPATH "${CMTPROJECTPATH}${SAVED_CMTPROJECTPATH}"
endif
'''
        return '''# Use the nightly builds search path if needed.
if [ -e ./build.conf ] ; then
    . ./build.conf
fi
if [ -z "$nightly_base" ] ; then
    nightly_base="$LHCBNIGHTLIES"
fi

if [ -e ${nightly_base}/${nightly_slot}/${nightly_day} ] ; then
    if [ -e ${nightly_base}/${nightly_slot}/${nightly_day}/setupSearchPath.sh ] ; then
        SAVED_CMTPROJECTPATH="${CMTPROJECTPATH:+:$CMTPROJECTPATH}"
        . ${nightly_base}/${nightly_slot}/${nightly_day}/setupSearchPath.sh
        # This a temporary work around because setupSearchPath.sh overrides CMTPROJECTPATH
        # instead of extending it.
        export CMTPROJECTPATH="${CMTPROJECTPATH}${SAVED_CMTPROJECTPATH}"
    else
        export CMTPROJECTPATH="${nightly_base}/${nightly_slot}/${nightly_day}${CMTPROJECTPATH:+:$CMTPROJECTPATH}"
    fi
fi
'''

    def __repr__(self):
        return '{0}({1!r}, {2!r}, {3!r})'.format(
            self.__class__.__name__, self.base, self.slot, self.day)


def addSearchPath(parser):
    '''
    Common options used to extend the search path.
    '''
    from optparse import OptionValueError

    def dev_dir_cb(option, opt_str, value, parser):
        if value is None:
            try:
                value = LHCbDevPathEntry()
            except ValueError:
                raise OptionValueError(
                    '--dev used, but LHCBDEV is not defined')
        else:
            value = SearchPathEntry(value)
        parser.values.dev_dirs.append(value)

    parser.add_option(
        '--dev',
        action='callback',
        callback=dev_dir_cb,
        help='prepend $LHCBDEV to the search path. '
        'Note: the directories are searched in the '
        'order specified on the command line.')
    parser.add_option(
        '--dev-dir',
        action='callback',
        metavar='DEVDIR',
        type='string',
        callback=dev_dir_cb,
        help='prepend DEVDIR to the search path. '
        'Note: the directories are searched in the '
        'order specified on the command line.')

    def nightly_base(option, opt_str, value, parser):
        '''
        Callback for the --nightly-base and --nightly-cvmfs options.
        '''
        if parser.values.nightly:
            raise OptionValueError('%s specified after --nightly' % option)

        if not os.path.isdir(value):
            raise OptionValueError('"%s" is not a directory' % value)

        parser.values.nightly_bases.append(value)

    parser.add_option(
        '--nightly-base',
        action='callback',
        type='string',
        callback=nightly_base,
        help='add the specified directory to the nightly builds '
        'search path (must be specified before --nightly)')

    def nightly_option(_option, opt_str, _value, _parser):
        valid_value = re.compile(
            r'^(mon|tue|wed|thu|fri|sat|sun|today|\d{4}-\d\d-\d\d|\d+)$',
            re.IGNORECASE)
        day = 'Today'

        parser.values.dev = True
        rargs = parser.rargs

        try:
            slot = rargs.pop(0)
        except IndexError:
            raise OptionValueError(
                '%s must be followed by the slot of the '
                'nightlies and optionally by the build id' % opt_str)

        if '/' in slot:
            slot, day = slot.split('/', 1)
        elif rargs:
            match = valid_value.match(rargs[0])
            if match:
                day = rargs.pop(0).capitalize()

        # Locate the requested slot in the know nightlies directories
        from os import environ
        nightly_bases = parser.values.nightly_bases
        nightly_bases += [
            environ.get('LHCBNIGHTLIES', '/cvmfs/lhcbdev.cern.ch/nightlies'),
            environ.get('LCG_nightlies_area',
                        '/cvmfs/sft-nightlies.cern.ch/lcg/nightlies')
        ]

        from LbEnv.ProjectEnv.lookup import (findNightlyDir,
                                             InvalidNightlySlotError)
        try:
            slot_dir = findNightlyDir(slot, day, nightly_bases)

            nightly_base, slot, day = slot_dir.rsplit(os.sep, 2)
            parser.values.dev_dirs.append(
                NightlyPathEntry(nightly_base, slot, day))
            parser.values.nightly = (slot, day, nightly_base)
        except InvalidNightlySlotError as err:
            # to be able to print a friendly message about local installation
            # of a nightly slot, we cannot exit while parsing the arguments
            parser.values.nightly = err

    parser.add_option(
        '--nightly',
        action='callback',
        metavar='SLOT [DAY]',
        type='string',
        callback=nightly_option,
        nargs=0,
        help='Add the required slot of the LHCb nightly builds to the list of '
        'DEV dirs. DAY must be a 3 digit abbreviation of the weekday "Today", '
        'an ISO formatted date or an integer, the default is Today. Special '
        'settings of the CMTPROJECTPATH needed for the nightly build slot are '
        'taken into account.')

    parser.add_option(
        '--help-nightly-local',
        action='store_true',
        help='Print instructions on how to install locally and use a nightly '
        'slot bulid'
    )

    parser.add_option(
        '--user-area',
        action='store',
        help='Use the specified path as User_release_area instead of '
        'the value of the environment variable.')

    parser.add_option(
        '--no-user-area',
        action='store_true',
        help='Ignore the user release area when looking for projects.')

    parser.set_defaults(
        dev_dirs=SearchPath([]),
        user_area=os.environ.get('User_release_area'),
        no_user_area=False,
        nightly=None,
        nightly_bases=[])

    return parser


def addOutputLevel(parser):
    '''
    Add options to get more or less messages.
    '''
    import logging
    parser.add_option(
        '--verbose',
        action='store_const',
        const=logging.INFO,
        dest='log_level',
        help='print more information')
    parser.add_option(
        '--debug',
        action='store_const',
        const=logging.DEBUG,
        dest='log_level',
        help='print debug messages')
    parser.add_option(
        '--quiet',
        action='store_const',
        const=logging.WARNING,
        dest='log_level',
        help='print only warning messages (default)')

    parser.set_defaults(log_level=logging.WARNING)

    return parser


def addPlatform(parser):
    '''
    Add option to specify a platform.
    '''

    parser.add_option(
        '-c', '--platform', help='runtime platform [default: %default]')
    parser.add_option(
        '--force-platform',
        action='store_true',
        help='ignore platform compatibility check')

    parser.set_defaults(platform=None, force_platform=False)

    return parser


def checkPlatform(parser, platform):
    '''
    Validate platform obtained from the parser to get the right value according
    to options, environment or system.
    '''
    try:
        from LbEnv import defaultPlatform
        return (platform or os.environ.get('BINARY_TAG')
                or os.environ.get('CMTCONFIG') or defaultPlatform())
    except RuntimeError:
        parser.error('unknown system, set the environment or use --platform')


def addListing(parser):
    '''
    Add option to request the list of versions.
    '''

    parser.add_option(
        '-l',
        '--list',
        action='store_true',
        help='list the available versions of the requested '
        'project and exit')
    parser.add_option(
        '-L',
        '--list-platforms',
        action='store_true',
        help='list the available platforms for the requested '
        'project/version and exit')

    parser.set_defaults(list=False, list_platforms=False)

    return parser
