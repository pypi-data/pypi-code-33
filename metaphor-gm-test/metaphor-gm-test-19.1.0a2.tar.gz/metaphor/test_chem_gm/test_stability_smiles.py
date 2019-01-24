# $Id: test_stability_smiles.py 4128 2016-04-30 07:04:12Z jeanluc $
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
from metaphor.chem_gm.core.metamolecule import MetaMolecule, stabilizeSmiles
import os

#folder = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
folder = os.path.dirname(__file__)
testfile = os.path.join(folder, "testfiles", "Base321E_chem.xlsx")
testfile2 = os.path.join(folder, "testfiles", "phenol.xlsx")

#testfile = os.path.abspath("../../test/testfiles/Base321E_chem.xlsx")
#testfile2 = os.path.abspath("../../test/testfiles/phenol.xlsx")

class Test_Stability_smiles2(unittest.TestCase):
    
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
        assert arange == "$B$1:$E$322"
        assert self.source.get_field_list("DATA") == ["Noms", "Smiles", "LogP", "M"]
        
    def test_Smiles(self):
        arange = self.source.get_worksheet_normalized_range("DATA")[1]
        fieldlist = self.source.get_field_list("DATA")
        cumul = 0
        
        for ind, (molname, smilesini) in enumerate(self.source.iterData(arange, [0,1], 0)):
            if not ind: continue
            smiles1 = stabilizeSmiles(smilesini)#, full=True)
            test = True
            if not test:
                print(ind, cumul, molname)
                print("\t%s" % smilesini)  
                print("\t%s" % smiles1)
#             metamol = MetaMolecule(smilesini, molname)
#             smiles1, indlist1 = metamol.getSmiles(True, True)
#             metamol2 = MetaMolecule(smiles1, molname)
#             smiles2, indlist2 = metamol2.getSmiles(True, True)
#             if (smiles1 != smiles2):# and indlist2[0]:
#                 cumul += 1
#             #print data
#                 print ind, cumul, molname
#                 print "\t%s" % smilesini
#                 print "\t%s" % smiles1, indlist1
#                 print "\t%s" % smiles2, indlist2

if __name__ == "__main__":
    unittest.main()
    
