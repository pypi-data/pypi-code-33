#!/usr/bin/env python
"""

Utilities methods to parse CMake files

"""
import os
import re
import sys



def getHeptoolsVersion(toolchainData):
    '''
    Parse the toolchain file to find the HEPTools version
    we depend on.
    '''
    ret = None
    r = re.compile("\s*set\s*\(\s*heptools_version\s+(\w+)\s*\)", re.MULTILINE)
    m = r.search(toolchainData)
    if m != None:
        ret =  m.group(1)
    return ret



def getGaudiUse(cmakeListsData):
    '''
    Parse the CMakeLists.txt to find which projects this project uses
    '''
    # Locate the  gaudi_project macro
    # gaudi_project(LHCb v39r2
    #   USE Gaudi v26r4
    #   DATA Gen/DecFiles
    #        Det/SQLDDDB VERSION v7r*
    #        FieldMap
    #        ParamFiles
    #        PRConfig
    #        RawEventFormat
    #        TCK/HltTCK
    #        TCK/L0TCK VERSION v4r*)

    # Group to one line to avoid dealing with carriage returns, then gets the lists of deps
    # Remove all comments
    # This is NOT ERROR PROOF as it ignores the fact that the # could be within ascript
    # but we need a proepr parser to sort that out.
    databak = cmakeListsData
    alllines = [ l.strip().split("#")[0] for l in cmakeListsData.splitlines() ]
    data = ' '.join(alllines)
    r = re.compile("gaudi_project\s*\(\s*(\w+)\s+(\w+)\s+(?:FORTRAN\s+)?USE\s+(.*?)\s*(?:\sDATA[^)]*)?\)")
    m = r.search(data)
    if m != None:
        # Checking that we have the right section in the CMakeLists
        tproj = m.group(1)
        tver =  m.group(2)
        # Now check the match for the dependencies
        # Splitting the list and grouping into pairs
        tmpdeps =  m.group(3).split()
        deplist = zip(*[tmpdeps[x::2] for x in (0, 1)])
        return deplist
    
    return []

