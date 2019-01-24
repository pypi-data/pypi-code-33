

































#-*- coding: ISO-8859-15 -*-
#-------------------------------------------------------------------------------
# Metaphor-test
#
# $Id: $ 
#
# Copyright 2018 Jean-Luc PLOIX
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#-------------------------------------------------------------------------------
'''
Created on 6 nov. 2018

@author: jeanluc
'''
#include_start
VERSION_MAJOR = 19
VERSION_MINOR = 1
VERSION_MAINTENANCE = 0
VERSION_BUILD = 2
TAG = "a"

# history # 

# 19.1.0a2  en cours uploader
# 19.1.0a1  creation of meta^hor_nntoolbox project
# 18.11.23a2 fix cython file erasing after install
# 18.11.22a12 fix ccrypt.py after erasing common folder in install
# 18.11.22a11 OK for erasing common folder in install
# 18.11.22a3 OK install
# 18.11.6a10 remove tests with *.so
# 18.11.6a9 modif testfiles extension from TXT to txt
# 18.11.6a2 map setup 
# 18.11.6a1 create metaphor project 
#include_end

VERSION3 = "%d.%d.%d" % (VERSION_MAJOR, VERSION_MINOR, VERSION_MAINTENANCE)
VERSION2 = "%d.%d" % (VERSION_MAJOR, VERSION_MINOR)
if not VERSION_BUILD:
    candidate__version__ = VERSION3
elif TAG:
    candidate__version__ = "{0}{1}{2}".format(VERSION3, TAG, VERSION_BUILD)
else:
    candidate__version__ = "%d.%d.%d.%d" % (VERSION_MAJOR, VERSION_MINOR, VERSION_MAINTENANCE, VERSION_BUILD)  
__version__ = candidate__version__

version = lambda: __version__

def distname(dname="", path="", ext=".tar.gz"):   
    import os
    if not dname:
        dname = 'metaphor'
    st = "%s-%s%s"% (dname, __version__, ext)
    if len(path):
        st = os.path.join(path, st)
    return st

if __name__ == "__main__":
    print("metaphor-nn version :", __version__)