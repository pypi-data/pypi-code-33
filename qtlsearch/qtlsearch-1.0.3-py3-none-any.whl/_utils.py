#!/usr/bin/env python
'''
    QTLSearch — to search for candidate causal genes in QTL studies
     by combining Gene Ontology annotations across many species, leveraging
    hierarchical orthologous groups.

    (C) 2015-2018 Alex Warwick Vesztrocy <alex@warwickvesztrocy.co.uk>

    This file is part of QTLSearch. It contains the necessary utility functions.

    QTLSearch is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    QTLSearch is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with QTLSearch.  If not, see <http://www.gnu.org/licenses/>.
'''
import bz2
import gzip
import os
import sys


# File opening. This is based on the example on SO here:
# http://stackoverflow.com/a/26986344
fmagic = {b'\x1f\x8b\x08': gzip.open,
          b'\x42\x5a\x68': bz2.BZ2File}


def auto_open(fn, *args):
    '''
        Opens files based on their "magic bytes". Supports bz2 and gzip. If it
        finds neither of these, presumption is it is a standard, uncompressed
        file.
    '''
    if os.path.isfile(fn) and os.stat(fn).st_size > 0:
        with open(fn, 'rb') as fp:
            fs = fp.read(max([len(x) for x in fmagic]))
        for (magic, _open) in fmagic.items():
            if fs.startswith(magic):
                return _open(fn, *args)
    else:
        if fn.endswith('gz'):
            return gzip.open(fn, *args)
        elif fn.endswith('bz2'):
            return bz2.BZ2File(fn, *args)

    return open(fn, *args)


def exe_name():
    '''
        Return the executable's basename, for inclusion in the help (with the
        help of argparse).
    '''
    return os.path.basename(sys.argv[0])
