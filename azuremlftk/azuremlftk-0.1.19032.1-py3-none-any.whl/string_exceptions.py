"""
A module that contains utility functions for strings.
"""

#------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation.  All rights reserved.
# 
#------------------------------------------------------------------------

import uuid

def unique_string():
    return str(uuid.uuid1())

def bytecount_to_string(bytecount):
    kbytes = bytecount / 1024
    if kbytes < 1:
        return "{0} bytes".format(bytecount)            
    mbytes = kbytes / 1024
    if mbytes < 1:
        return "{0} KB".format(round(kbytes, 1))
            
    gbytes = mbytes / 1024
    if gbytes < 1:
        return "{0} MB".format(round(mbytes, 1))
            
    return "{0} GB".format(round(gbytes, 1))

def equals_caseinsensitive(str1, str2):
    return str1.casefold() == str2.casefold()

def find_caseinsensitive(source, substr, start=None, end=None):
    """
        Case insensivity search
    """
    return source.find(substr.casefold(), start, end)

def contains(source, substr, caseinsensitive=False):
    if caseinsensitive:
        return find_caseinsensitive(source, substr) >= 0
    return source.find(substr) >= 0
