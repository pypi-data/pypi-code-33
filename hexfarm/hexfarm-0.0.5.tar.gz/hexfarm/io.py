# -*- coding: utf-8 -*- #
#
# hexfarm/io.py
#
#
# MIT License
#
# Copyright (c) 2018-2019 Brandon Gomes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

"""
Utilities for IO.

"""

# -------------- Standard Library -------------- #

import os

# -------------- External Library -------------- #

from path import Path

# -------------- Hexfarm  Library -------------- #

from .util import identity


def has_extension(ext, path):
    """Check if Path Has Given Extension."""
    return Path(path).ext == ext


def walk_paths(
    directory,
    dir_predicate=identity,
    file_predicate=identity,
    *,
    topdown=True,
    onerror=None,
    followlinks=False,
    **kwargs
    ):
    """Walk Paths Filtering Directories and Files."""
    for root, dirs, files in os.walk(directory,
                                     topdown=topdown,
                                     onerror=onerror,
                                     followlinks=followlinks):
        yield root, filter(dir_predicate, dirs), filter(file_predicate, files)


def fwalk_paths(
    directory,
    dir_predicate=identity,
    file_predicate=identity,
    *,
    topdown=True,
    onerror=None,
    follow_symlinks=False,
    dir_fd=None,
    **kwargs
    ):
    """Walk Paths Filtering Directories and Files."""
    for root, dirs, files, rootfd in os.fwalk(directory,
                                              topdown=topdown,
                                              onerror=onerror,
                                              followlinks=followlinks,
                                              dir_fd=dir_fd):
        yield root, filter(dir_predicate, dirs), filter(file_predicate, files), rootfd
