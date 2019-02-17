# -*- coding: utf-8 -*-
"""
Created on Sun Feb 17 11:14:35 2019

@author: hxvin
"""

import time
import sys
for x in range(10000):
    print( "HAPPY >> %s <<\r" % str(x))
    sys.stdout.flush()