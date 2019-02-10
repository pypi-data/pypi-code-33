# -*- coding: utf-8 -*- #
#
# hexfarm/cli.py
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
Utilities for CLI Programs.

"""

# -------------- Standard Library -------------- #

import sys
from functools import wraps

# -------------- Hexfarm  Library -------------- #


__all__ = (
    'run_main'
)


def run_main(
    argv=sys.argv,
    exit=sys.exit,
    *,
    auto_run=True,
    ignore_arg_zero=False,
    check_name_is_main=False
):
    """Run Main Function with Given Arguments and Exit Process."""
    def internal(main):
        @wraps(main)
        def wrapper():
            return exit(main(argv[1:] if ignore_arg_zero else argv))
        if auto_run:
            if check_name_is_main and __name__ == '__main__':
                wrapper()
            else:
                wrapper()
        return wrapper
    return internal
