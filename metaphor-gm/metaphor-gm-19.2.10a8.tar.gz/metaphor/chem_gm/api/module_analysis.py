#!python
# -*- coding: ISO-8859-1 -*-
#-------------------------------------------------------------------------------
# $Id$
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
'''Analyse of a compiled module content
'''

import os, sys
import argparse
from six import string_types
from six.moves import input
from ...chem_gm.api.GM_API import ReadAndCheckModule 

def isiterable(obj):
    return hasattr(obj, '__contains__')

def unQuote(data, quotechar="'" + '"'):
    if isinstance(data, string_types):
        res = data
        for c in quotechar:
            res = res.strip(c)
        return res
    elif isiterable(data):  # cas d'un iterateur data
        return (unQuote(item, quotechar) for item in data)
    else:
        return data

def getOptions(args):
    parser = argparse.ArgumentParser(description='GM module analysis.') 
    parser.add_argument('source', default="nothing", nargs="?", type=str,
        help="module to analyse filename")
    parser.add_argument('-f', '--folder', dest='folder', 
        default="", help="Set working folder")
    return parser.parse_args(args)

def run(argv=[], sub=False):
    """Analysing a module.
    
    argv is supposed to be the argument list given by the system.
    If no argument is given, the program will ask for a module name to analyse.
    
    """
    if not sub:
        curfolder = os.getcwd()
    if not len(argv):
        argv = [""]
    if len(argv) == 1:
        fullmessage = "Enter module to analyse. ('q' to quit):\n"
        res = input(fullmessage)
        while not res.lower() in ("", "q", "quit"):
            argloc = argv + [res]
            run(argloc, True)
            res = input(fullmessage)
        
        if res.lower() in ("", "q", "quit"):
            print("done")
            return
        
        
    elif len(argv) >= 2:
        args = argv[1:]
        options = getOptions(args)
        folder = options.folder
        if not sub and folder:
            os.chdir(folder)
        try:
            module = options.source.strip()
        except: pass
#             if ((module.startswith("'") and module.endswith("'")) or 
#                 (module.startswith('"') and module.endswith('"'))):
#                 module = module[1:-1]
        try:
            error, text, dico = ReadAndCheckModule(module, None, None, verbose=5)
            print( text)
        except: 
            print( "cannot read %s"% module)
    else:
        print( "aborted")
        return
    if not sub:
        print( "Done")
    if not sub:
        os.chdir(curfolder)

if __name__ == '__main__':

    testlist = ["libbjma271emos_si3_h_cn3_grds5_cn4_5n.so",
                 "libbjma271emos_si3_h_grds2_2n.so",
                 "libbjma270t30lvisc_2_5n.so",
                 "libbjma270t30lvisc14sm_5n.so"]

    for test in  testlist:
        module = os.path.join(os.path.dirname(__file__), "demofiles", test)
        run(["", module])
        