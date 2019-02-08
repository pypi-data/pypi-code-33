#!/usr/bin/env python

"""Get Python configuration variables.

Usage: python getconfig.py VARIABLE

Used to extract variables from Python's Makefile, intended to be
called from Asap's Makefile.
"""
from __future__ import print_function

import sys
import distutils.sysconfig

if len(sys.argv) != 2:
    print("\nERROR: Got %s arguments, expected 1.\n\n" % (len(sys.argv)-1,), file=sys.stderr)
    print(__doc__, file=sys.stderr)
    sys.exit(-1)

key = sys.argv[1]
if key == "SITEPACKAGES":
    print(distutils.sysconfig.get_python_lib(plat_specific=True))
else:
    cfgDict = distutils.sysconfig.get_config_vars()
    if key == 'BLDLIBRARY':
        val = cfgDict.get(key, None)
        if not val:
            val = '-lpython{0}'.format(cfgDict['VERSION'])
        print(val)
    else:
        print(cfgDict[key])
        
