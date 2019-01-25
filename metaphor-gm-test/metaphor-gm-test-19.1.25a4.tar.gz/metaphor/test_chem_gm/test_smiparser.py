# $Id: test_smiparser.py 4128 2016-04-30 07:04:12Z jeanluc $
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
Created on 4 nov. 2014

@author: jeanluc
'''

import unittest
import numpy as np
from metaphor.chem_gm.core.metamolecule import MetaMolecule
from collections import defaultdict
from metaphor.chem_gm.core.atoms import centraux0

smilescistrans =  r'O=C(NC/C=C\CN1)CN(CC(O)=O)CCN(CC(O)=O)CCN(CC(O)=O)CC1=O'
smilescistrans2 = r'O=C(NCC=CCN1)CN(CC(O)=O)CCN(CC(O)=O)CCN(CC(O)=O)CC1=O'

delta = \
"""(4) iso 1 / 0
(6) iso 2 / 0"""

dist = np.array(
    [[ 0,  1,  2,  3,  4,  5,  6,  7,  2,  3,  4,  5,  6,  6,  4,  5,  6,  7,  8,  9,  9,  7,  8,  9,  10, 11, 12, 12,  9,  8,  9], 
     [ 1,  0,  1,  2,  3,  4,  5,  6,  1,  2,  3,  4,  5,  5,  3,  4,  5,  6,  7,  8,  8,  6,  7,  8,  9, 10, 11, 11,  8,  7,  8], 
     [ 2,  1,  0,  1,  2,  3,  4,  5,  2,  3,  4,  5,  6,  6,  4,  5,  6,  7,  8,  9,  9,  7,  8,  8,  9, 10, 11, 11,  7,  6,  7], 
     [ 3,  2,  1,  0,  1,  2,  3,  4,  3,  4,  5,  6,  7,  7,  5,  6,  7,  8,  9, 10, 10,  8,  8,  7,  8,  9, 10, 10,  6,  5,  6], 
     [ 4,  3,  2,  1,  0,  1,  2,  3,  4,  5,  6,  7,  8,  8,  6,  7,  8,  9, 10, 11, 11,  8,  7,  6,  7,  8,  9,  9,  5,  4,  5], 
     [ 5,  4,  3,  2,  1,  0,  1,  2,  5,  6,  7,  8,  9,  9,  7,  8,  8,  9, 10, 11, 11,  7,  6,  5,  6,  7,  8,  8,  4,  3,  4], 
     [ 6,  5,  4,  3,  2,  1,  0,  1,  6,  7,  8,  9, 10, 10,  8,  8,  7,  8,  9, 10, 10,  6,  5,  4,  5,  6,  7,  7,  3,  2,  3], 
     [ 7,  6,  5,  4,  3,  2,  1,  0,  7,  8,  9, 10, 11, 11,  8,  7,  6,  7,  8,  9,  9,  5,  4,  3,  4,  5,  6,  6,  2,  1,  2], 
     [ 2,  1,  2,  3,  4,  5,  6,  7,  0,  1,  2,  3,  4,  4,  2,  3,  4,  5,  6,  7,  7,  5,  6,  7,  8,  9, 10, 10,  8,  8,  9], 
     [ 3,  2,  3,  4,  5,  6,  7,  8,  1,  0,  1,  2,  3,  3,  1,  2,  3,  4,  5,  6,  6,  4,  5,  6,  7,  8,  9,  9,  7,  8,  9], 
     [ 4,  3,  4,  5,  6,  7,  8,  9,  2,  1,  0,  1,  2,  2,  2,  3,  4,  5,  6,  7,  7,  5,  6,  7,  8,  9, 10, 10,  8,  9, 10], 
     [ 5,  4,  5,  6,  7,  8,  9, 10,  3,  2,  1,  0,  1,  1,  3,  4,  5,  6,  7,  8,  8,  6,  7,  8,  9, 10, 11, 11,  9, 10, 11], 
     [ 6,  5,  6,  7,  8,  9, 10, 11,  4,  3,  2,  1,  0,  2,  4,  5,  6,  7,  8,  9,  9,  7,  8,  9, 10, 11, 12, 12, 10, 11, 12], 
     [ 6,  5,  6,  7,  8,  9, 10, 11,  4,  3,  2,  1,  2,  0,  4,  5,  6,  7,  8,  9,  9,  7,  8,  9, 10, 11, 12, 12, 10, 11, 12], 
     [ 4,  3,  4,  5,  6,  7,  8,  8,  2,  1,  2,  3,  4,  4,  0,  1,  2,  3,  4,  5,  5,  3,  4,  5,  6,  7,  8,  8,  6,  7,  8], 
     [ 5,  4,  5,  6,  7,  8,  8,  7,  3,  2,  3,  4,  5,  5,  1,  0,  1,  2,  3,  4,  4,  2,  3,  4,  5,  6,  7,  7,  5,  6,  7], 
     [ 6,  5,  6,  7,  8,  8,  7,  6,  4,  3,  4,  5,  6,  6,  2,  1,  0,  1,  2,  3,  3,  1,  2,  3,  4,  5,  6,  6,  4,  5,  6], 
     [ 7,  6,  7,  8,  9,  9,  8,  7,  5,  4,  5,  6,  7,  7,  3,  2,  1,  0,  1,  2,  2,  2,  3,  4,  5,  6,  7,  7,  5,  6,  7], 
     [ 8,  7,  8,  9, 10, 10,  9,  8,  6,  5,  6,  7,  8,  8,  4,  3,  2,  1,  0,  1,  1,  3,  4,  5,  6,  7,  8,  8,  6,  7,  8], 
     [ 9,  8,  9, 10, 11, 11, 10,  9,  7,  6,  7,  8,  9,  9,  5,  4,  3,  2,  1,  0,  2,  4,  5,  6,  7,  8,  9,  9,  7,  8,  9], 
     [ 9,  8,  9, 10, 11, 11, 10,  9,  7,  6,  7,  8,  9,  9,  5,  4,  3,  2,  1,  2,  0,  4,  5,  6,  7,  8,  9,  9,  7,  8,  9], 
     [ 7,  6,  7,  8,  8,  7,  6,  5,  5,  4,  5,  6,  7,  7,  3,  2,  1,  2,  3,  4,  4,  0,  1,  2,  3,  4,  5,  5,  3,  4,  5], 
     [ 8,  7,  8,  8,  7,  6,  5,  4,  6,  5,  6,  7,  8,  8,  4,  3,  2,  3,  4,  5,  5,  1,  0,  1,  2,  3,  4,  4,  2,  3,  4], 
     [ 9,  8,  8,  7,  6,  5,  4,  3,  7,  6,  7,  8,  9,  9,  5,  4,  3,  4,  5,  6,  6,  2,  1,  0,  1,  2,  3,  3,  1,  2,  3], 
     [10,  9,  9,  8,  7,  6,  5,  4,  8,  7,  8,  9, 10, 10,  6,  5,  4,  5,  6,  7,  7,  3,  2,  1,  0,  1,  2,  2,  2,  3,  4], 
     [11, 10, 10,  9,  8,  7,  6,  5,  9,  8,  9, 10, 11, 11,  7,  6,  5,  6,  7,  8,  8,  4,  3,  2,  1,  0,  1,  1,  3,  4,  5], 
     [12, 11, 11, 10,  9,  8,  7,  6, 10,  9, 10, 11, 12, 12,  8,  7,  6,  7,  8,  9,  9,  5,  4,  3,  2,  1,  0,  2,  4,  5,  6], 
     [12, 11, 11, 10,  9,  8,  7,  6, 10,  9, 10, 11, 12, 12,  8,  7,  6,  7,  8,  9,  9,  5,  4,  3,  2,  1,  2,  0,  4,  5,  6], 
     [ 9,  8,  7,  6,  5,  4,  3,  2,  8,  7,  8,  9, 10, 10,  6,  5,  4,  5,  6,  7,  7,  3,  2,  1,  2,  3,  4,  4,  0,  1,  2], 
     [ 8,  7,  6,  5,  4,  3,  2,  1,  8,  8,  9, 10, 11, 11,  7,  6,  5,  6,  7,  8,  8,  4,  3,  2,  3,  4,  5,  5,  1,  0,  1], 
     [ 9,  8,  7,  6,  5,  4,  3,  2,  9,  9, 10, 11, 12, 12,  8,  7,  6,  7,  8,  9,  9,  5,  4,  3,  4,  5,  6,  6,  2,  1,  0]], ndmin=2)


class Test_TokenList(unittest.TestCase):
    
    def setUp(self):
        #print "hello"
        pass
    
    def tearDown(self):
        pass
        #print "bye"

    def test_tokenlist0(self):
        smiles = "CNC"
        tl = MetaMolecule(smiles)
        assert len(tl) == 3, "expected %s"%len(tl)
        assert tl[0].symbol == "C"
        assert tl[1].symbol == "N"
        assert tl[0].symbol == "C"
        assert tl[0].grade == 1
        assert tl[1].grade == 2
        assert tl[0].grade == 1
        assert len(tl[0].bonds) == 1
        assert len(tl[1].bonds) == 2
        assert len(tl[2].bonds) == 1
        assert tl[0].bonds[0].smilesindex == 1
        assert tl[1].bonds[0].smilesindex == 0
        assert tl[1].bonds[1].smilesindex == 2
        assert tl[2].bonds[0].smilesindex == 1
        
    def test_computedistances(self):
        smiles = "CCC"
        tl = MetaMolecule(smiles)
        d = tl.computedistances()
        tt = d - np.asarray([[0, 1, 2], [1, 0, 1], [2, 1, 0]])
        assert not tt.any(), "expecetd %s"% d
        
    def test_computeDistanceIndexes(self):
        smiles = "CC=C"
        tl = MetaMolecule(smiles)
        tl.computedistances()
        assert tl[0].distanceIndex == 5, "expected %s"% tl[0].distanceIndex
        assert tl[1].distanceIndex == 2, "expected %s"% tl[1].distanceIndex
        assert tl[2].distanceIndex == 4, "expected %s"% tl[2].distanceIndex
        tl.tallyDistanceIndexes()
        assert tl[0].distanceIndex == 3, "expected %s"% tl[0].distanceIndex
        assert tl[1].distanceIndex == 0, "expected %s"% tl[1].distanceIndex
        assert tl[2].distanceIndex == 2, "expected %s"% tl[2].distanceIndex
    
    def test_centralatom(self):
        smiles = "O=CC=C"
        tl = MetaMolecule(smiles)
        tl.computedistances()
        tl.tallyDistanceIndexes()
        res = tl.getCentralAtom(centraux=centraux0)
        assert res.smilesindex == 3, "expected %s"% res.smilesindex
    
    def test_isomeriecistrans(self):
        smiles = smilescistrans
        smiles2 = smilescistrans2
        tl = MetaMolecule(smiles)
        tl2 = MetaMolecule(smiles2)
        assert len(tl) == 31, "expected %d"% len(tl)
        assert len(tl2) == 31, "expected %d"% len(tl)
        mat1 = tl.computedistances()
        tl.tallyDistanceIndexes()
        mat2 = tl2.computedistances()
        assert not (mat1 - mat2).any(), "distances should be equal"
        tl2.tallyDistanceIndexes()
        st1 = tl.getdiff(tl2)
        #assert not (mat1 - dist).any()  # a reprendre dist
        #assert(st1 == delta), "expected %s"% st1  # a reprendre
        res = tl.getCentralAtom(centraux=centraux0)
        res2 = tl2.getCentralAtom(centraux=centraux0)
        assert res.numero == res2.numero
        assert res.smilesindex == 26, "expected %s"% res.smilesindex
        assert res2.smilesindex == 24, "expected %s"% res2.smilesindex
    
    def test_analysetokenlist(self):
        smiles = "CC=N"
        tokens = MetaMolecule(smiles)
        occurmols = defaultdict(lambda:0)
        occurmols['C'] = 4
        occurmols['N'] = 2
        atoms, grade, iso, chiral, occurs, occurmols, cycleloc, _ = tokens.analyse(occurmols=occurmols)
        assert occurmols['C'] == 5
        assert occurmols['N'] == 3
        #1print "occurs =", occurs
        #print "occurmols =", occurmols
    
    def test_analysetokenlistcistrans(self):
        smiles = smilescistrans    
        tokens = MetaMolecule(smiles)
        #atoms, grade, iso, chiral, occurs, occurmols, cycleloc
        atoms, grade, iso, chiral, occurs, _, cycleloc, _ = tokens.analyse()
        assert len(atoms) == 3
        assert 'C' in atoms
        assert 'N' in atoms
        assert 'O' in atoms
        assert grade == 4
        assert iso == 2
        assert chiral == 0
        assert cycleloc == 1 # ?? 0 ??
        assert occurs['C'] == 18
        assert occurs['N'] == 5
        assert occurs['O'] == 8
        #print "res =", res
        #print "grade =", grade
        #print "iso =", iso
        #print "chiral =", chiral
        #print "occurs =", occurs
        #print "occurmols =", occurmols
        #print "cycleloc =", cycleloc
        

#def test_smicistrans():
#    smiles1 = 'O=C(NC/C=C\CN1)CN(CC(O)=O)CCN(CC(O)=O)CCN(CC(O)=O)CC1=O'    
#    smiles2 = u"O=C(NCC=CCN1)CN(CC(O)=O)CCN(CC(O)=O)CCN(CC(O)=O)CC1=O"
#    lst1 = MetaMolecule(smiles1)
#    mat1 = lst1.computedistances()
#    lst2 = MetaMolecule(smiles2)
#    mat2 = lst2.computedistances()
#    res = mat2 - mat1
#    assert not res.any()
    
#    for m in lst2:
#        print m

    
if __name__ == "__main__":
    unittest.main()
    
