#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'sv99'

import sys
import argparse
from timeit import default_timer as timer
from pathlib import Path

from tralutils import __version__
from tralutils.msn3 import Msn3File
from tralutils.evt import EvtFile
from tralutils.idx import IdxFile


def get_arg_parser():
    p = argparse.ArgumentParser(description='Show single tral videodata file info')
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("-i", "--input", help='videdata file')
    # g.add_argument("-a", "--all", action="store_true", help='All dictionary in current directory')
    # p.add_argument("--header", action="store_true", default=False, help='Print dictionary header and exit')
    # p.add_argument("-o", "--outdir", default="", help="Output directory")
    # p.add_argument("-c", "--codecs", action=CodecsAction)
    p.add_argument("-v", "--verbose", action="store_true", default=False)
    p.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    return p


def display_time(sec):
    result = ""
    hour = sec // 3600
    if hour:
        result += "{} hours".format(hour)
        if hour == 1:
            result = result.rstrip('s')
    sec -= 3600 * hour
    min = sec // 60
    if min:
        if result != "":
            result += " "
        result += "{} min".format(int(min))
    sec -= 60 * min
    if result != "":
        result += " "
    result += "{0:0.2f} sec".format(sec)
    return result


def main():
    args = get_arg_parser().parse_args()
    file_name = args.input
    file_ext = Path(file_name).suffix
    if file_ext == ".msn3":
        f = Msn3File(file_name, args.verbose)
    elif file_ext == ".evt":
        f = EvtFile(file_name, args.verbose)
    else:
        f = IdxFile(file_name, args.verbose)


    # dicts = []
    # if args.all:
    #     # all lsd in directory
    #     print("Decode all lsd in current directory..")
    #     dicts = get_dicts()
    #     print(dicts)
    # else:
    #     dicts.append(args.input)
    #
    # if args.header:
    #     header(dicts)
    # else:
    #     if args.outdir != "":
    #         # check path
    #         if not os.path.exists(args.outdir):
    #             os.mkdir(args.outdir)

    start = timer()
    f.parse()
    end = timer()

    f.dump()
    print("Elapsed: %s" % display_time(end - start))

    return 0


if __name__ == '__main__':
    sys.exit(main())
