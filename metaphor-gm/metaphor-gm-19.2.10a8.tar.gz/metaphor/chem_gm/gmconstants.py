#-------------------------------------------------------------------------------
# $Id: gmconstants.py 4238 2016-09-27 11:27:39Z jeanluc $
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
#-------------------------------------------------------------------------------

from ..monal.util.utils import getapplibase, getFile

# constantes algorithmiques
ISOALGO_0 = 0
ISOALGO_PAIR = 1
#-------------------------------------------------------------------------------
FULLH = 0

#USE_SQL_SAVING = 1
DEBUG_SQL_SAVING = 0
USE_SQL_SAVING_LOO = 1

FORCE_START_PARAM = 0
USE_PARALLEL_REGISTER = 1

USE_PARALLEL_USAGE = 0 # pas de parallel en usage a cause de la compilation JIT

(IS_STD, IS_BS, IS_LOO, IS_SUPER) = range(4)

filedict = {}

def getMainDir(high=False):
    import os
    dir = os.path.dirname(__file__)
    if not dir:
        dir = os.getcwd()
    if high:
        hdir = os.path.dirname(dir)
        while hdir.startswith("graphmachine"):
            dir = hdir
            hdir = os.path.dirname(hdir)
    return dir

# def get File(mainDir, filename="graphmachine.cfg"):
#     import os, sys
#     for path, dirs, files in os.walk(mainDir):
#         if filename in files:
#             return os.path.join(path, filename)
#     for valDir in sys.path:
#         test = os.path.join(valDir, filename)
#         if os.path.exists(test):
#             return test
#     test = os.path.join(getapplibase("graphmachine"), filename)
#     if os.path.exists(test):
#         return test
#     return ""

def checkinstall(mainDir="", filelist=[]):
    import os
    global filedict
    mainDir = mainDir if mainDir else getMainDir(False)
    badinstall = []
    for val in filelist: 
        res = getFile(mainDir, val, ("graphmachine", "chem_gm", "monal"))
        if res:
            filedict[val] = res
        else:
            badinstall.append(val)
    return badinstall

# def doCheck():
#     global filedict   
#     global badlist 
#     filedict = {}
#     maindir = getMainDir()
#     badlist = checkinstall(maindir, ("GM.bmp", "graphmachine.cfg", "atoms.cfg"))

#doCheck()

if __name__ == "__main__":
    print(getMainDir())
