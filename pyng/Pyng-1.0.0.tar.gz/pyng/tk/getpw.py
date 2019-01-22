#!/usr/bin/python
"""\
@file   getpw.py
@author Nat Goodspeed
@date   2015-12-11
@brief  getpw() function for console-based Python scripts to prompt user for
        password

        This is for console-based Python scripts because it expects there's no
        existing Tk root window.

        If you need to prompt for more than one password, consider using
        form.display_form() instead of successive calls to this function.

$LicenseInfo:firstyear=2015&license=internal$
Copyright (c) 2015, Linden Research, Inc.
$/LicenseInfo$
"""
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
import tkinter, tkinter.simpledialog
import os
import __main__                         # for filename of main script
from .__init__ import WINDOW_TITLE, BULLET, get_root

def getpw(title="password:"):
    get_root()
    return tkinter.simpledialog.askstring(WINDOW_TITLE, title, show=BULLET)
