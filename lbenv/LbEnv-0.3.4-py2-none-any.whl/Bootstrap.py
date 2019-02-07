#!/usr/bin/env python
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
    from itertools import chain, imap

    # only take into account existing directories
    if isdir(root):
        yield root  # the requested entry is always the first of the list
        try:
            # get the list of dependencies
            deps = load(open(join(root, 'etc', 'chaining_infos.json')))
            # recurse in each of them, in order
            for r in chain.from_iterable(imap(collect_roots, deps)):
                yield r
        except (IOError, ValueError):
            pass


def search_path(roots):
    '''
    Generate a list of entries for the search path from a list of siteroot
    dirs.
    '''
    from os.path import join
    suffixes = [
        'lhcb',
        join('lcg', 'releases'),
        # backward compatibility
        join('lcg', 'app', 'releases'),
        join('lcg', 'external'),
        # hint to look up special projects
        'contrib',
        # allow siteroot specific modules
        'cmake'
    ]

    for root in roots:
        for suff in suffixes:
            yield join(root, suff)

    # see if we have LbDevTools
    try:
        from LbDevTools import DATA_DIR
        yield join(DATA_DIR, 'cmake')
    except ImportError:
        pass


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
    from itertools import chain
    from LbEnv import __version__
    from LbEnv.ProjectEnv.options import checkPlatform

    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {}'.format(__version__))
    parser.add_argument(
        '-c', '--platform', help='override the default platform detection')
    parser.add_argument(
        '-r', '--siteroot', help='path to the installation root')
    parser.add_argument(
        '-u',
        '--userarea',
        help='override default User_release_area value',
    )
    parser.add_argument(
        '-w',
        '--workspace',
        help='optional directory to prefix to the projects search path')
    parser.add_argument(
        "--sh",
        action="store_const",
        const="sh",
        dest="shell",
        help="print the changes to the environment as shell "
        "commands for 'sh'-derived shells")
    parser.add_argument(
        "--csh",
        action="store_const",
        const="csh",
        dest="shell",
        help="print the changes to the environment as shell "
        "commands for 'csh'-derived shells")
    parser.add_argument(
        "--py",
        action="store_const",
        const="py",
        dest="shell",
        help="print the changes to the environment as a Python "
        "dictionary")

    parser.set_defaults(
        userarea=os.environ.get('User_release_area') or (join(
            os.environ['HOME'], 'cmtuser') if 'HOME' in os.environ else None),
        workspace=os.environ.get('LBENV_CURRENT_WORKSPACE'))

    if (set(['-h', '--help']).intersection(sys.argv)
            and set(['--sh', '--csh', '--py']).intersection(sys.argv)):
        # if we are in shell script mode, and want the help message, it should
        # be printed on stderr
        sys.stdout = sys.stderr

    args = parser.parse_args()

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
    control.set('LBENV_SOURCED', __version__)
    control.set(
        'LBENV_ALIASES',
        os.path.join(
            os.path.dirname(__file__), 'data',
            'aliases.' + (args.shell or 'sh')))

    args.platform = checkPlatform(parser, args.platform)

    # this is something like "Linux-x86_64"
    host_flavour = '{0}-{4}'.format(*os.uname())
    host_os = LbPlatformUtils.host_os()

    control.set('BINARY_TAG', args.platform)
    control.set('CMTCONFIG', args.platform)
    control.set('LCG_hostos', host_os)

    if args.siteroot:
        mysiteroot = args.siteroot
    elif 'MYSITEROOT' in os.environ:
        mysiteroot = os.environ['MYSITEROOT']
    elif 'VO_LHCB_SW_DIR' in os.environ:
        mysiteroot = join(os.environ['VO_LHCB_SW_DIR'], 'lib')
    elif 'VIRTUAL_ENV' in os.environ:
        mysiteroot = os.environ['VIRTUAL_ENV']
        # the venv is usually in #MYSITEROOT/var/..., so we try to deduce it
        head, tail = mysiteroot, 'none'
        while tail and tail != 'var':
            head, tail = os.path.split(head)
        if tail:
            # 'var' was found in the path, so the parent directory is the root
            mysiteroot = head
    else:
        sys.stderr.write('error: not valid siteroot provided\n')
        sys.exit(1)

    control.set('MYSITEROOT', mysiteroot)

    if args.userarea and os.path.exists(args.userarea):
        control.set('User_release_area', args.userarea)

    # LHCB_LOC and LCG_RELEASES can be set beforehand to override default
    # entries in the search path
    control.set('LHCBRELEASES',
                os.environ.get('LHCB_LOC', join(mysiteroot, 'lhcb')))
    control.set(
        'LCG_RELEASES',
        os.environ.get('LCG_RELEASES', join(mysiteroot, 'lcg', 'releases')))

    roots = list(collect_roots(mysiteroot))

    control.prepend(
        'CMAKE_PREFIX_PATH', ':'.join(
            chain(['${LHCBRELEASES}', '${LCG_RELEASES}'], search_path(roots))))
    if args.workspace:
        args.workspace = os.path.abspath(args.workspace)
        control.prepend('CMAKE_PREFIX_PATH', args.workspace)
        control.set('LBENV_CURRENT_WORKSPACE', args.workspace)
    elif args.shell == 'csh':
        # this is a special hack needed for the csh version of lb-set-workspace
        control.set('LBENV_CURRENT_WORKSPACE', '')

    # Add to the paths the utilities hosted in the siteroots
    control.prepend(
        'PATH', ':'.join(
            bin_path(roots, host_os=host_os, host_flavour=host_flavour)))

    if 'VIRTUAL_ENV' in os.environ:
        control.default('XDG_DATA_DIRS', '/usr/local/share:/usr/share')
        control.prepend('XDG_DATA_DIRS',
                        join(os.environ['VIRTUAL_ENV'], 'share'))
        control.prepend('XDG_DATA_DIRS', join(mysiteroot, 'share'))

    # FIXME this chunk is copied from xenv.Script (we need refactoring)
    # print only modified variables
    env = control.vars()

    # generate and print the banner _before_ removing unchanged variables
    if sys.stderr.isatty():
        import LbEnv.Banner
        sys.stderr.write(LbEnv.Banner.generate(env=env))
        sys.stderr.write('\n')

    # only set unmodified (non function) variables
    env = dict((name, value) for name, value in env.items()
               if not name.endswith('()') and original_env.get(name) != value)

    if args.shell == 'py':
        from pprint import pprint
        pprint(env)
    else:
        template = {
            'sh': "export {0}='{1}' ;",
            'csh': "setenv {0} '{1}' ;"
        }.get(args.shell, "{0}={1}")
        print '\n'.join(
            template.format(name, value)
            for name, value in sorted(env.items()))
        print 'source "$LBENV_ALIASES"'


if __name__ == '__main__':  # pragma no cover
    main()
