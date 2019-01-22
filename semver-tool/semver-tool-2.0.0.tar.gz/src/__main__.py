#!/usr/bin/python2
"""Print SemVer version for a git project. Git tags must match `v?M.N.P` pattern.
Full format string is MNPRBD, where
 M - major
 N - minor
 P - patch
 R - prerelease
 B - build
 D - dirty
"""

############################################################
# {{{ configure logging
import logging
import sys
import json

try:
    import customlogging
except:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

log = logging.getLogger("gwsa")
if "--debug" in sys.argv:
    log.setLevel(logging.DEBUG)


def prettify(obj):
    class AllEncoder(json.JSONEncoder):
        def default(self, obj):
            try:
                return json.JSONEncoder.default(self, obj)
            except Exception as e:
                return str(obj)

    return json.dumps(obj, indent=4, sort_keys=True, cls=AllEncoder)

# }}}

############################################################
# {{{ main: argparse and dispatch

import argparse
import os
import semver_tool


def AppArgParser():
    p = argparse.ArgumentParser(
        prog=__package__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__, )
    p.add_argument("--debug", help="debug mode", action="store_true")
    p.add_argument(
        "--version",
        action="version",
        version=semver_tool.__version__)
    p.add_argument(
        "--rc",
        help='release candidate prefix; default "%(default)s"',
        metavar='str',
        default='rc')
    p.add_argument(
        "-f",
        "--format",
        help='version format; default %(default)s',
        default='MNPRBD',
        metavar='str')
    p.add_argument(
        "dir",
        help='git repo dir; default "%(default)s"',
        default='.',
        nargs='?')
    return p


def main():
    p = AppArgParser()

    Args, UnknownArgs = p.parse_known_args()
    log.debug("Args: %s", prettify(vars(Args)))
    log.debug("UnknownArgs: %s", UnknownArgs)

    sm = semver_tool.GitSemVer(root=Args.dir, rc_prefix=Args.rc)
    print sm.format(Args.format)

# }}}

if __name__ == "__main__":
    main()
