#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'sv99'

import fnmatch
import os
import sys
import argparse
from pprint import pprint
from timeit import default_timer as timer

from tralutils import __version__
from tralutils.msn3 import Msn3File
from tralutils.evt import EvtFile
from tralutils.idx import IdxFile
from tralutils.tools import sizeof_fmt


def get_arg_parser():
    p = argparse.ArgumentParser(description='Show tral archive videodir information')
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("-i", "--input", help='videodata dir')
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
    path = args.input
    print("Videdir path: %s" % path)

    files = os.listdir(path)
    print("Files: %i" % len(files))
    msn3_files = sorted(fnmatch.filter(files, "*.msn3"))
    print("Msn3 files: %i" % len(msn3_files))
    id3_files = sorted(fnmatch.filter(files, "*.id3"))
    print("Id3 files: %i" % len(id3_files))

    start = timer()
    # paser first msn3 - get tral name
    msn3 = Msn3File(os.path.join(path, msn3_files[0]), args.verbose)
    msn3.parse_first_hdr()
    print("Tral name: %s" % msn3.device_name)
    for file in id3_files:
        id3 = IdxFile(os.path.join(path, file), args.verbose)
        id3.parse()
        id3.dump()
        msn3_path = os.path.join(path, os.path.splitext(file)[0] + ".msn3")
        if os.path.exists(msn3_path):
            print("%s Size: %s" % (os.path.basename(msn3_path), sizeof_fmt(os.path.getsize(msn3_path))))

    end = timer()
    print("Elapsed: %s" % display_time(end - start))

    return 0


if __name__ == '__main__':
    sys.exit(main())
