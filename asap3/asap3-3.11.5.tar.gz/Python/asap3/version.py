"""The ASAP version number is specified in this file.

This file sets the __version__ variable to ASAP's version number.
The variable is imported by the main Asap module.  Furthermore, this module
prints the version number when executed, this is used by the makefile.
"""
from __future__ import print_function


__version__ = "3.11.5"


if __name__ == '__main__':
    print(__version__)
    
