# -*- coding: utf-8 -*-
"""
Created on Sun Dec 30 08:12:55 2018

@author: yoelr
"""

def dim(string):
    """Return string with gray ansicolor coding."""
    return '\x1b[37m\x1b[22m' + string + '\x1b[0m'
