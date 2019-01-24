# $Id: test_molecule.py 4128 2016-04-30 07:04:12Z jeanluc $
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
Created on 4 nov. 2015

@author: jeanluc
'''
import unittest
from metaphor.chem_gm.core.metamolecule import MetaMolecule


class TestMolecule(unittest.TestCase):


    def test_Equivalent(self):
        fullH = False
        sname, smiles = "Toluene", "Cc1ccccc1"
        sname, smiles = "xxx", "Cc1cc(C)ccc1"
    
        smilst = MetaMolecule(smiles, sname, fullH=fullH) 
        #smilst.printAll()
#         print
#         for tok in smilst:
#             #if tok.numero in [3, 5]:
#                 
#             print tok.numero, "<=>", smilst.getEquivalents(tok.numero)
       
    


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_Equivalent']
    unittest.main()