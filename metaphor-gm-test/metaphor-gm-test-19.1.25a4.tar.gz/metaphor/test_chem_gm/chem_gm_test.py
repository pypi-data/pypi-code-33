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
Created on 29 sept. 2016

@author: jeanluc
'''

import unittest

try:
    import metaphor.chem_gm
except:
    import os, sys
    pth = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    pth = os.path.join(pth, 'GM_API', 'src')
    if not pth in sys.path:
        sys.path.append(pth)
#     for val in sys.path:
#         print val

from test_cycles import TestCycles
from test_GMmodel import Test_TokenList
from test_molecule import TestMolecule
from test_phenol_smiles import Test_Stability_smiles
from test_smiparser import Test_TokenList
from test_stability_smiles import Test_Stability_smiles2
from test_token import Test_Token

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

caselist = (TestCycles, 
            Test_TokenList, 
            TestMolecule, 
            Test_Stability_smiles,
            Test_TokenList, 
            Test_Stability_smiles2, 
            Test_Token, )

def run():
    suite = unittest.TestSuite()
    for test_class in caselist:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    run()
