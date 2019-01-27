#!/usr/bin/env python
"""
Module SIGS -- Signal Handler Utilities
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2015 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains utilities for signal handling.
"""

from contextlib import contextmanager
from signal import signal


@contextmanager
def signal_handler(sig, handler):
    oldhandler = signal(sig, handler)
    try:
        yield
    finally:
        signal(sig, oldhandler)
