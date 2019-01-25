# $Id: test_token.py 4128 2016-04-30 07:04:12Z jeanluc $
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
Created on 6 nov. 2014

@author: jeanluc
'''
import unittest
from metaphor.chem_gm.core import smitokens


class Test_Token(unittest.TestCase):


    def test_token0(self):
        tok = smitokens.SmiToken(None, 5, "N")
        assert tok.parent is None
        assert tok.numero == 5
        assert tok.symbol == "N", "expected %s"% tok.symbol
        assert tok.smilesindex == -1
        assert tok.aromatic == 0
        assert tok.iso == 0
        assert tok.chiral == 0
        assert tok.atomicMass == 14.0, "expected %s"%tok.atomicMass
        assert tok.atomicNumber == 7, "expected %s"%tok.atomicNumber
        assert tok.charge == 0
        assert tok.richsymbol == "N", "expected %s"% tok.richsymbol 

    def test_token1(self):
        charge = 2
        iso = 2
        chiral = 1
        tok = smitokens.SmiToken(None, 5, "C", index=7, aromatic=0, iso=iso, chiral=chiral, charge=charge)
        assert tok.parent is None
        assert tok.numero == 5
        assert tok.symbol == "C"
        assert tok.smilesindex == 7
        assert tok.aromatic == 0
        assert tok.iso == iso
        assert tok.chiral == chiral
        assert tok.atomicMass == 12.01, "expected %s"%tok.atomicMass
        assert tok.atomicNumber == 6, "expected %s"%tok.atomicNumber
        assert tok.charge == charge
        assert tok.richsymbol == "[C+2]g2@bs", "expected %s"% tok.richsymbol #  [C+2]g2@bs


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()