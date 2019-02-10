#-*- coding: ISO-8859-15 -*-

# $Id: test_API.py 4131 2016-05-03 11:33:06Z jeanluc $
#
# Copyright 2016 Jean-Luc PLOIX
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

'''
Created on 22 avr. 2016

Test of Graphmachine API

@author: jeanluc
'''
import os, sys
import chem_gm
#import graphmachine as gm
GMpath = chem_gm.gmpath
#gm.__path__[0]
os.chdir(GMpath)
if not GMpath in sys.path:
    sys.path.append(os.path.join(GMpath, 'main'))
from gm_api import GM_API as gmapi

debug = 1
debugAnalyse = 0
debugprogress = 1
debugModel = 1
skipCreateModel = 1

demodebug = 0
if debug:
    if debugAnalyse:
        demodebug = demodebug | gmapi.DEMO_DEBUG_ANALYSIS
    if debugprogress:
        demodebug = demodebug | gmapi.DEMO_DEBUG_PROGRESS
    if debugModel:
        demodebug = demodebug | gmapi.DEMO_DEBUG_MODEL
    if skipCreateModel:
        demodebug = demodebug | gmapi.DEMO_SKIP_MODEL_CREATION

#===============================================================================
if __name__ == '__main__':
    
    #GMpath = gm.__path__[0]
    #os.chdir(GMpath)
    #import sys
    
    if not GMpath in sys.path:
        sys.path.append(GMpath)
    
    filename = "Base321E_chem.xlsx"
    datarange = "DATA"
    modulename = ""
    hidden = 4
    central = 5
    
    path =  GMpath  #gm.__path__[0]
    os.chdir(path)
    testfilepath = os.path.abspath(os.path.join(path, "..", "test", "testfiles"))
    testfile = os.path.join(testfilepath, filename)
    if not os.path.exists(testfile):
        print( "testfile error : {0}".format(testfile))
    else:    
        moduledir = os.path.abspath(os.path.join(path, "..", "build"))
        if not os.path.exists(moduledir):
            os.makedirs(moduledir)
            sys.stdout.write("creating %s\n"% moduledir)
        print( "running apiDemo")
        print( "\ttestfile :", testfile, "|", datarange)
    
        gmapi.apiDemo(testfile, datarange, modulename=modulename, hidden=hidden, central=central, moduledir=moduledir, debug=demodebug)
    
        print ("apiDemo Done")

    