###############################################################################
# (c) Copyright 2013 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Contains scripts fo push or get artifact with rsync
'''
__author__ = 'Colas Pomies <colas.pomies@cern.ch>'

import os
import logging
from LbNightlyTools.Scripts.Common import PlainScript

from socket import gethostname
from LbNightlyTools.Utils import retry_call as call, ensureDirs

def execute_rsync(src, dest, includes=None, excludes=None, extra_param=None):

    cmd = ['rsync', '--archive', '--whole-file',
           '--partial-dir=.rsync-partial.%s.%d' %
           (gethostname(), os.getpid()),
           '--delay-updates', '--rsh=ssh']

    for param in extra_param or []:
        cmd.append(param)

    for include in includes or []:
            cmd.append('--include=%s' % include)

    for exclude in excludes or []:
        cmd.append('--exclude=%s' % exclude)

    if os.path.isdir(src) or ':' in src:
        src += '/'
        dest += '/'

    cmd.extend([src, dest])

    # create destination directory, if missing
    if ':' in dest:
        host, path = dest.split(':', 1)
        call(['ssh', host, 'mkdir -pv "%s"' % path])
    else:
        ensureDirs([dest])

    logging.debug("Rsync call : %s", cmd)

    return call(cmd, retry=3)

class Script(PlainScript):

    __usage__ = '%prog [options] source destination'
    __version__ = ''

    def defineOpts(self):
        """ User options -- has to be overridden """
        from LbNightlyTools.Scripts.Common import (addBasicOptions,
                                                   addDashboardOptions)
        addBasicOptions(self.parser)
        addDashboardOptions(self.parser)

        self.parser.add_option('--get-config',
                               action='store_true',
                               dest='get_config',
                               help='Synchronize configs files')

        self.parser.add_option('--get-sources',
                               action='store_true',
                               dest='get_sources',
                               help='Synchronize sources files')

        self.parser.add_option('--get-ccache',
                               action='store',
                               metavar='PLATFORM',
                               dest='get_ccache',
                               help='Transfer the ccache data for the given '
                                    'platform')

        self.parser.set_defaults(get_config=False,
                                 get_sources=False,
                                 get_ccache=None,
                                 source=None,
                                 destination=None)

    def main(self):

        if len(self.args) != 2:
            self.parser.error('wrong number of arguments')

        opts = self.options

        source = self.args[0]
        destination =  self.args[1]

        includes_param = ['/packs/', '/rpms/']
        excludes_param = []
        extra_param = []

        if opts.get_config:
            includes_param.append("/slot-config.json")
            includes_param.append("/configs.zip")
            excludes_param = ["*"]
        if opts.get_sources:
            includes_param.append("/packs/*.src.*")
            includes_param.append("/rpms/*")
            includes_param.append("/checkout.zip")
            excludes_param = ["*"]
        if opts.get_ccache:
            includes_param.append("/packs/ccache_dir.*.{0}.tar.bz2"
                                  .format(opts.get_ccache))
            excludes_param = ["*"]

        if self.log.level <= logging.INFO:
            extra_param = ['--progress']

        return execute_rsync(
            source,
            destination,
            includes_param,
            excludes_param,
            extra_param)
