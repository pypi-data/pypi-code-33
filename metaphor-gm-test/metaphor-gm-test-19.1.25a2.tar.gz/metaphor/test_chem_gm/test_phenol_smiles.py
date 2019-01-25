# $Id: test_phenol_smiles.py 4128 2016-04-30 07:04:12Z jeanluc $
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
Created on 14 oct. 2015

@author: jeanluc
'''

import unittest
from metaphor.monal.datareader._excel import Excel
from metaphor.chem_gm.core.metamolecule import MetaMolecule, stabilizeSmiles, addClassToSmiles
#from graphmachine.core.toolbox import
import os
 
folder = os.path.dirname(__file__)
testfile = os.path.join(folder, "testfiles", "phenol.xlsx")
#testfile = os.path.abspath("../../test/testfiles/phenol.xlsx")

class Test_Stability_smiles(unittest.TestCase):
    
    def setUp(self):
        #print "hello"
        self.source = Excel(testfile, load=True)
    
    def tearDown(self):
        del self.source
        #print "bye"
        
    def test_FileExists(self):
        assert os.path.exists(testfile)
    
    def test_read(self):
        _, arange = self.source.get_worksheet_normalized_range("DATA")
        assert arange == "$A$1:$C$15"
        #assert self.source.get_field_list("DATA") == ["Noms", "Smiles", "LogP", "M"]
        
    def test_equivalents(self):
        arange = self.source.get_worksheet_normalized_range("DATA")[1]        
        
        for ind, (molname, smilesini) in enumerate(self.source.iterData(arange, [0,1], 0)):
            fullH = True
            mol = MetaMolecule(smilesini, fullH=fullH)
            smiles1 = mol.toSmiles(fullH=fullH, itermax=10)
            mol = MetaMolecule(smiles1, fullH=fullH)
            if not ind:
                self.assertEqual(molname, "4-chloro-2-methoxyphenol")
                self.assertEqual(smilesini, "OC1=CC=C(Cl)C=C1OC")
                self.assertEqual(smiles1, "ClC1=C([H])C([H])=C(O[H])C(=C1[H])OC([H])([H])[H]")
#             print ind, molname
#             print "\t%s" % smilesini 
#             print "\t%s" % smiles1 
#             print "\t%s" % mol.equivalentList() 
    
    def test_SmilesH(self):
        arange = self.source.get_worksheet_normalized_range("DATA")[1]        
        
        for ind, (molname, smilesini) in enumerate(self.source.iterData(arange, [0,1], 0)):
            fullH = True
            smiles1 = MetaMolecule(smilesini, fullH=fullH).toSmiles(fullH=fullH, itermax=10)     #stabilizeSmiles(smilesini)
            res = addClassToSmiles(smiles1, "H", data=1, prefix=2)
            if not ind:
                self.assertEqual(molname, "4-chloro-2-methoxyphenol")
                self.assertEqual(smilesini, "OC1=CC=C(Cl)C=C1OC")
                self.assertEqual(smiles1, "ClC1=C([H])C([H])=C(O[H])C(=C1[H])OC([H])([H])[H]")
            
            # print ind, molname
#             print "\t%s" % smilesini  
#             print "\t%s" % smiles1
#             for ii, val in enumerate(res):
#                 print "\t\t%s_%d %s"% (molname, ii, val)

    def test_SmilesH2(self):
        arange = self.source.get_worksheet_normalized_range("DATA")[1]        
        
        for ind, (molname, smilesini) in enumerate(self.source.iterData(arange, [0,1], 0)):
            fullH = True
            mol = MetaMolecule(smilesini, fullH=fullH)
            smiles1 = mol.toSmiles(fullH=fullH, itermax=10)     #stabilizeSmiles(smilesini)
            res = addClassToSmiles(smiles1, markatom=["H"], data=1, reduced=True, fullH=True, withindex=True)
            if not ind:
                self.assertEqual(molname, "4-chloro-2-methoxyphenol")
                self.assertEqual(smilesini, "OC1=CC=C(Cl)C=C1OC")
                self.assertEqual(smiles1, "ClC1=C([H])C([H])=C(O[H])C(=C1[H])OC([H])([H])[H]")
            
#             print ind, molname
#             print "\t%s" % smilesini  
#             print "\t%s" % smiles1
#             for ii, val in res:
#                 print "\t\t%s_%d %s"% (molname, ii, val)

if __name__ == "__main__":
    unittest.main()
    
