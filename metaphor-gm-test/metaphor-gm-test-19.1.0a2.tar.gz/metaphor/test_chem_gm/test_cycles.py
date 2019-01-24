# $Id: test_cycles.py 4129 2016-05-01 03:34:44Z jeanluc $
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
import metaphor.chem_gm
from metaphor.chem_gm.core.metamolecule import MetaMolecule


class TestCycles(unittest.TestCase):


    def test_commonbonds(self):
        smiles = "C12=CC=CC=C1C=C3C=CC=CC3=C2"
        mol = MetaMolecule(smiles)
        clist = mol.cycles(commonBonds=True)
        if clist[0].linking(0, 5):
            self.assert_ (clist[1].linking(7, 12))
        else:
            self.assert_ (clist[0].linking(7, 12))
            self.assert_ (clist[1].linking(0, 5))
        
    def test_anthracene(self):
        smiles = "C12=CC=CC=C1C=C3C=CC=CC3=C2"
        mol = MetaMolecule(smiles)
        clist = mol.cycles(True)
        assert(clist[0][0].numero == 0)
        assert(clist[0][1].numero == 1)
        assert(clist[0][2].numero == 2)
        assert(clist[0][3].numero == 3)
        assert(clist[0][4].numero == 4)
        assert(clist[0][5].numero == 5)
        assert(clist[1][0].numero == 0)
        assert(clist[1][1].numero == 5)
        assert(clist[1][2].numero == 6)
        assert(clist[1][3].numero == 7)
        assert(clist[1][4].numero == 12)
        assert(clist[1][5].numero == 13)
        assert(clist[2][0].numero == 7)
        assert(clist[2][1].numero == 8)
        assert(clist[2][2].numero == 9)
        assert(clist[2][3].numero == 10)
        assert(clist[2][4].numero == 11)
        assert(clist[2][5].numero == 12)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_antracene']
    unittest.main()