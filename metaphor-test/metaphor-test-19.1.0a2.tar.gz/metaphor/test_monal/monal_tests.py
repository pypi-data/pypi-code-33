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
'''
Created on 27 sept. 2016

@author: jeanluc

Ce module rassemble tous les tests du package monal.
'''

import sys, os
import unittest
pth = os.getcwd()
if not pth in sys.path:
    sys.path.append(pth)
filepth = os.path.dirname(__file__)
if not filepth in sys.path:
    sys.path.append(filepth)
if filepth != pth:
    os.chdir(filepth)

from test_data_manager import TestNdArrayBasedDataManager, TestOtherStyleBasedDataManager, TestCsvBasedDataManager
from test_monaltoolbox import TestMonalToolbox
from test_toolbox import TestToolbox
from test_utils import TestUtils
from test_linalg import TestLinAlg
from test_property import TestProperty
from test_libManager import TestLibManager
from test_monal_module import TestMonalBase, TestMonal

noLibArg = '--no-lib-test'
DO_TEST_LIBMANAGER = not noLibArg in sys.argv
if not  DO_TEST_LIBMANAGER:
    sys.argv.pop(sys.argv.index(noLibArg))

caselist = (TestMonalToolbox, 
            TestUtils, 
            TestToolbox,
            TestNdArrayBasedDataManager,
            TestOtherStyleBasedDataManager,
            TestCsvBasedDataManager,
            TestMonalBase,
            TestMonal,
            TestLinAlg,
            TestProperty,
            TestLibManager)
    
def run():
    suite = unittest.TestSuite()
    for test_class in caselist:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    import sys
    print("Python", sys.version)  #_info)
#     for val in sys.path:
#         print(val)
    run()
    