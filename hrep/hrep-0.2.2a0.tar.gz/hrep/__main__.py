#!/usr/bin/env python
from __future__ import print_function
import io
import fnmatch
import os
import re
import sys
import argparse
import binascii
import scandir

BUFSIZE = 4*1024*1024
TAILSIZE = BUFSIZE
HEXDIGITS = "0123456789abcdef"

try:
    range = xrange
except NameError:
    pass

def hex_pattern(expr):
    m = re.match(r"^\s*((?:[0-9a-f?]{2}|\*|\s*)*)\s*$", expr, re.I)
    if m:
        # parse hex pattern
        groups = re.findall(r"([0-9a-f?]{2}|\*)", m.group(1), re.I)
        pat = []
        for b in groups:
            if b == "??":
                pat.append('.')
            elif b == "*":
                pat.append(".*?")
            elif '?' in b:
                pat.append("[%s]" % "".join(br"\x%s" % b.replace('?', i).lower() for i in HEXDIGITS))
            else:
                pat.append(r"\x%s" % b.lower())
        return re.compile(''.join(pat).encode('ascii'), re.S)
    else:
        raise ValueError("Invalid hex pattern: `%s'" % expr)

def fblocks(fobj, start=0, length=None, chunksize=BUFSIZE, tailsize=None):
    if tailsize is None:
        tailsize = chunksize
    assert tailsize <= chunksize

    buf = bytearray(chunksize + tailsize)
    head = memoryview(buf)[tailsize:]
    tail = memoryview(buf)[:tailsize]
    total = 0

    while length is None or total < length:
        if total == 0:
            tailsize = fobj.readinto(tail)
        read = fobj.readinto(head)

        if read < chunksize:
            yield total + start, buf[:tailsize + read]
            break
        else:
            yield total + start, buf

        tail[:] = head[-tailsize:]
        total += read

def multisearch(block, patterns):
    for i, p in enumerate(patterns):
        for m in p.finditer(block):
            yield m

def list_recursively(dirnames):
    for d in dirnames:
        if os.path.isfile(d):
            yield d
        for path, dirs, files in scandir.walk(d):
            for f in files:
                yield os.path.normpath(os.path.join(path, f))

def filename_filter(filenames, include_filters, exclude_filters):
    for fn in filenames:
        if include_filters:
            for pattern in include_filters:
                if fnmatch.fnmatch(fn, pattern):
                    break
            else:
                continue
        for pattern in exclude_filters:
            if fnmatch.fnmatch(fn, pattern):
                break
        else:
            yield fn

def open_files(filenames):
    for fn in filenames:
        try:
            yield io.open(fn, "rb", buffering=0)
        except IOError as e:
            print("Error opening file: `%s`: %s" % (e.filename, e.strerror), file=sys.stderr)

MARK_ON = u'\ufff9'
SEPERATOR = u'\ufffa'
MARK_OFF = u'\ufffb'
UNPRINTABLE = u'\ufffd'
UNPRINTABLE_MARKED = u'\ufffc'

class HexDumper(object):
    line_fmt = (u"{addr_mark}{addr:#10x}{addr_end}" 
                + SEPERATOR + "{start_mark} {dump} {end_mark}"
                + SEPERATOR + "{ss}" + SEPERATOR)

    def __init__(self, width, align, before, after):
        self.width = width
        self.align = align
        self.before = before
        self.after = after
        self.btrans = bytearray(x if 32 <= x < 127 else 0xff for x in range(256))

    def dump(self, data, offset, start, end):
        lines = []
        marking = False
        width = self.width

        # take only relevant data
        dstart = ((start - self.before) // self.align) * self.align
        dend = ((end + self.after + self.align - 1) // self.align) * self.align
        dstart = max(0, dstart)

        for i in range(dstart, dend, width):
            bs = ['{:02x}'.format(x) for x in bytearray(data[i:i + width])]
            ss = (data[i:i+width]).translate(self.btrans).decode('ascii', 'replace')
            # padding
            bs += ['  '] * (width - len(bs))
            ss = ss.ljust(width)

            start_mark = end_mark = addr_mark = ''

            if start - width < i < end:
                # mark appears on this line
                addr_mark, addr_end= MARK_ON, MARK_OFF
                mark_end = end - i
                mark_start = start - i
                ss = (ss[:max(mark_start, 0)] 
                    + MARK_ON
                    + ss[max(mark_start, 0):mark_end].replace(UNPRINTABLE, UNPRINTABLE_MARKED)
                    + MARK_OFF
                    + ss[mark_end:])

                if mark_end <= width:
                    # mark ends after this byte
                    bs[mark_end-1] = bs[mark_end-1] + MARK_OFF
                else:
                    # mark continues to next line
                    end_mark = MARK_OFF

                if mark_start >= 0:
                    # mark starts at this byte
                    bs[mark_start] = MARK_ON + bs[mark_start]
                else:
                    # mark started in previous line
                    start_mark = MARK_ON
                # need to override unprintable character color

            # group by pairs, then groups of 4 pairs
            dump = [''.join(bs[j:j+2]) for j in range(0, len(bs), 2)]
            dump = [' '.join(dump[j:j+4]) for j in range(0, len(dump), 4)]
            dump = '  '.join(dump)

            addr = offset + i
            lines.append(self.line_fmt.format(**locals()))
        return '\n'.join(lines)

def print_match(filename, block, offset, match, decimal):
    match_hex = binascii.hexlify(block[match.start():match.end()]).decode('ascii')
    start = offset + match.start()
    if decimal:
        print("{}:{}:{}".format(filename, start, match_hex))
    else:
        print("{}:0x{:x}:{}".format(filename, start, match_hex))

def colorscheme(mark_on, mark_off, unprintable, unprintable_marked, seperator):
    return {
        ord(MARK_ON): mark_on,
        ord(MARK_OFF): mark_off,
        ord(UNPRINTABLE): unprintable,
        ord(UNPRINTABLE_MARKED): unprintable_marked,
        ord(SEPERATOR): seperator
    }

COLORSCHEME_DEFAULT = colorscheme(
    mark_on = u"\x1b[31;1m",
    mark_off = u"\x1b[0m",
    unprintable = u"\x1b[90m.\x1b[0m",
    unprintable_marked = u".",
    seperator = u'\x1b[34m|\x1b[0m',
)

COLORSCHEME_MONOCHROME = colorscheme(
    mark_on = u"\x1b[4;1m",
    mark_off = u"\x1b[0m",
    unprintable = u"\x1b[90m.\x1b[0m",
    unprintable_marked = u".",
    seperator = u'\x1b[1m|\x1b[0m',
)

COLORSCHEME_NO_COLOR = colorscheme(
    mark_on = u"",
    mark_off = u"",
    unprintable = u".",
    unprintable_marked = u".",
    seperator = u'|',
)


def main():
    ap = argparse.ArgumentParser("hrep", 
        description="Search for binary sequences in files",
        epilog="Each output line corresponds to a match in the format:\n\
        <filename>:<offset>:<match>")
    ap.add_argument("-x", "--hex", dest="hex", action="append", default=[],
        help="Search for a hexadecimal pattern"
             "('?' matches a single nibble, '*' matches any number of bytes)")
    ap.add_argument("-a", "--ascii", dest="ascii", action="append", default=[],
        help="Search for an ASCII string")
    ap.add_argument("-e", "--regex", dest="regex", action="append", default=[],
        help="Search for a regular expression")

    ap.add_argument("-r", "--recursive", action="store_true",
        help="Recursively search in directories")
    ap.add_argument("--chunk-size",  default=BUFSIZE,
        help="Override default buffer size")
    ap.add_argument("-d", "--decimal-offset", action="store_true",
        help="Output decimal file offsets (by default prints hex)")
    ap.add_argument("-X", "--no-hexdump", action="store_true",
        help="Disable hex dump")
    ap.add_argument("-w", "--dump-width", type=int, default=16,
        help="Width of hex dump")
    ap.add_argument("-s", "--summary", action="store_true",
        help="Print summary at the end")
    ap.add_argument("-A", "--after", type=int, default=0,
        help="Number of additional bytes to display after match")
    ap.add_argument("-B", "--before", type=int, default=0,
        help="Number of additional bytes to display before match")
    ap.add_argument("-C", "--context", type=int, default=0,
        help="Number of additional bytes to display before and after match")

    ap.add_argument("-I", "--include", action="append", default=[],
        help="Filename pattern to include")
    ap.add_argument("-E", "--exclude", action="append", default=[],
        help="Filename pattern to exclude")

    ap.add_argument("-L", "--files-without-match", action="store_true",
        help="Only output unmatching filenames")
    ap.add_argument("-l", "--files-with-match", action="store_true",
        help="Only output matching filenames")
    ap.add_argument("-c", "--count", action="store_true",
        help="Only output number of matches for each input file")
    ap.add_argument("-m", "--max-count", metavar='NUM', default=None, type=int,
        help="Stop searching after NUM matches. ")

    ap.add_argument("--no-color", action="store_true",
        help="Disable color output")
    ap.add_argument("--monochrome", action="store_true",
        help="Use monochrome color scheme")

    ap.add_argument("--debug", action="store_true", help=argparse.SUPPRESS)

    ap.add_argument(dest="hex_a", metavar="HEX", 
        nargs="?", help="Hex encoded binary sequence to search for")
    ap.add_argument(dest="filename", nargs="*",
        help="List of files to search in")
    args = ap.parse_args()

    args.before += args.context
    args.after += args.context

    if args.hex or args.ascii or args.regex:
        if args.hex_a is not None:
            args.filename.insert(0, args.hex_a)
    else:
        if args.hex_a is not None:
            args.hex.append(args.hex_a)
        else:
            ap.error("No pattern specified")

    if args.no_color or os.name == 'nt':
        colors = COLORSCHEME_NO_COLOR
    elif args.monochrome:
        colors = COLORSCHEME_MONOCHROME
    else:
        colors = COLORSCHEME_DEFAULT

    try:
        patterns = [hex_pattern(x) for x in args.hex] + \
                   [re.compile(re.escape(x.encode("ascii"))) for x in args.ascii] + \
                   [re.compile(x.encode("ascii")) for x in args.regex]
    except ValueError as e:
        ap.error(str(e))

    if args.debug:
        print('patterns:')
        for p in patterns:
            print(p.pattern)

    if args.recursive:
        if len(args.filename) == 0:
            args.filename = ['.']
        args.filename = list_recursively(args.filename)
    else:
        if len(args.filename) == 0:
            args.filename = [sys.stdin.fileno()]

    files = open_files(filename_filter(args.filename, args.include, args.exclude))
    matches = 0
    matched_files = set()

    dumper = HexDumper(
        width=args.dump_width, 
        align=args.dump_width, 
        before=args.before, 
        after=args.after)

    for f in files:
        fname = f.name
        if fname == 0:
            fname = '<stdin>'
        for offset, block in fblocks(f, chunksize=args.chunk_size, tailsize=args.chunk_size):
            matches = 0

            for m in sorted(multisearch(block, patterns), key=lambda m: m.start()):
                if args.max_count and matches >= args.max_count:
                    break
                if args.files_with_match:
                    print(fname)
                    break
                matches += 1
                if args.files_without_match:
                    break
                if args.count:
                    continue

                if m.start() > args.chunk_size:
                    # Already matched this one (in the tail)
                    continue

                matches += 1
                matched_files.add(f)
                print_match(fname, block, offset, m, args.decimal_offset)

                if not args.no_hexdump:
                    print(dumper.dump(block, offset, m.start(), m.end()).translate(colors), file=sys.stderr)
                    print(file=sys.stderr)

            if args.count:
                print('{}:{}'.format(fname, matches))
            if args.files_without_match and matches == 0:
                print(fname)

    if args.summary:
        print("{} match(es) accross {} file(s)".format(matches, len(matched_files)),
            file=sys.stderr)
    return 0 if matches > 0 else 1




if __name__ == '__main__':
    sys.exit(main())
