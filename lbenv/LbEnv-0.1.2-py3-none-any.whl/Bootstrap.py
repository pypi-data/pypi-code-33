#!/usr/bin/env python
###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Code to bootstrap the initial environment.
'''

def collect_roots(root):
    '''
    Return an iterator of siteroot directories required by the requested root
    dir.

    Chaining of root directories is recorded in {root}/etc/chaining_infos.json
    as a list of required roots.
    '''
    from os.path import join, isdir
    from json import load
    from itertools import chain

    # only take into account existing directories
    if isdir(root):
        yield root  # the requested entry is always the first of the list
        try:
            # get the list of dependencies
            deps = load(open(join(root, 'etc', 'chaining_infos.json')))
            # recurse in each of them, in order
            for r in chain.from_iterable(map(collect_roots, deps)):
                yield r
        except IOError:
            pass


def search_path(roots):
    '''
    Generate a list of entries for the search path from a list of siteroot dirs.
    '''
    from os.path import join
    suffixes = ['lhcb',
                join('lcg', 'releases'),
                # backward compatibility
                join('lcg', 'app', 'releases'),
                join('lcg', 'external'),
                # allow siteroot specific modules
                'cmake']

    yield '${LHCBRELEASES}'
    yield '${LCG_RELEASES}'

    # see if we have LbDevTools
    try:
        import LbDevTools
        yield join(LbDevTools.DATA_DIR, 'cmake')
    except ImportError:
        pass

    for root in roots:
        for suff in suffixes:
            yield join(root, suff)


def bin_path(roots, host_os=None, host_flavour=None):
    '''
    Generate the list of directories to be prepended to the PATH variable.
    '''
    from os.path import join

    for root in roots:
        bindir = join(root, 'bin')
        if host_os:
            yield join(bindir, host_os)
        if host_flavour:
            yield join(bindir, host_flavour)
        yield bindir


def main():
    import os
    import sys
    from os.path import join

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-c', '--platform',
                      help='override the default platform detection')
    parser.add_option('-r', '--siteroot',
                      help='path to the installation root')
    parser.add_option("--sh",
                      action="store_const", const="sh", dest="shell",
                      help="print the changes to the environment as shell "
                           "commands for 'sh'-derived shells")
    parser.add_option("--csh",
                      action="store_const", const="csh", dest="shell",
                      help="print the changes to the environment as shell "
                           "commands for 'csh'-derived shells")
    parser.add_option("--py",
                      action="store_const", const="py", dest="shell",
                      help="print the changes to the environment as a Python "
                           "dictionary")

    if (set(['-h', '--help']).intersection(sys.argv) and
            set(['--sh', '--csh', '--py']).intersection(sys.argv)):
        # if we are in shell script mode, and want the help message, it should
        # be printed on stderr
        sys.stdout = sys.stderr

    opts, args = parser.parse_args()

    if os.environ.get('LBENV_SOURCED'):
        # LbEnv already called, do not run again
        return

    import LbEnv
    import LbPlatformUtils
    from xenv.Control import Environment
    control = Environment()
    control.presetFromSystem()
    original_env = dict(os.environ)

    # Make sure this script is sourced exactly once
    control.set('LBENV_SOURCED', '1')

    # make sure we can find data files
    if opts.platform is None:
        opts.platform = LbEnv.defaultPlatform()

    # this is something like "Linux-x86_64"
    host_flavour = '{0}-{4}'.format(*os.uname())
    host_os = LbPlatformUtils.host_os()

    control.set('CMTCONFIG', opts.platform)
    control.set('LCG_hostos', host_os)

    if opts.siteroot:
        mysiteroot = opts.siteroot
    elif 'MYSITEROOT' in os.environ:
        mysiteroot = os.environ['MYSITEROOT']
    elif 'VO_LHCB_SW_DIR' in os.environ:
        mysiteroot = join(os.environ['VO_LHCB_SW_DIR'], 'lib')
    elif 'VIRTUAL_ENV' in os.environ:
        mysiteroot = os.environ['VIRTUAL_ENV']
    else:
        sys.stderr.write('error: not valid siteroot provided\n')
        sys.exit(1)

    control.set('MYSITEROOT', mysiteroot)

    if 'HOME' in os.environ and os.path.exists(join(os.environ['HOME'],
                                                    'cmtuser')):
        control.set('User_release_area', join(os.environ['HOME'], 'cmtuser'))

    control.set('LHCBRELEASES', os.environ.get('LHCB_LOC',
                                               join(mysiteroot, 'lhcb')))
    control.set('LCG_RELEASES',
                os.environ.get('LCG_RELEASES',
                               join(mysiteroot, 'lcg', 'releases')))

    roots = list(collect_roots(mysiteroot))

    control.prepend('CMAKE_PREFIX_PATH', ':'.join(search_path(roots)))

    control.set('LHCBPROJECTPATH', control['CMAKE_PREFIX_PATH'])

    # FIXME do we really have to set CMTPROJECTPATH?
    control.set('CMTPROJECTPATH', control['CMAKE_PREFIX_PATH'])

    # Add to the paths the utilities hosted in the siteroots
    control.prepend('PATH', ':'.join(bin_path(roots,
                                              host_os=host_os,
                                              host_flavour=host_flavour)))

    for root in roots:
        cmtroot = join(root, 'contrib', 'CMT', 'v1r20p20090520')
        if os.path.exists(cmtroot):
            control.set('CMTROOT', cmtroot)
            control.set('CMTBIN', host_flavour)
            control.append('PATH', join('${CMTROOT}', '${CMTBIN}'))

    # FIXME this chunk is copied from xenv.Script (we need refactoring)
    # print only modified variables
    env = control.vars()

    # generate and print the banner _before_ removing unchanged variables
    if sys.stderr.isatty():
        import LbEnv.Banner
        sys.stderr.write(LbEnv.Banner.generate(env=env))
        sys.stderr.write('\n')

    # only set unmodified variables
    env = dict((name, value)
               for name, value in list(env.items())
               if original_env.get(name) != value)

    if opts.shell == 'py':
        from pprint import pprint
        pprint(env)
    else:
        template = {'sh':  "export {0}='{1}'",
                    'csh': "setenv {0} '{1}';"}.get(opts.shell, "{0}={1}")
        print('\n'.join(template.format(name, value)
                        for name, value in sorted(env.items())))


if __name__ == '__main__':  # pragma no cover
    main()
