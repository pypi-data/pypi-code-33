# $Id: test_smiparser2.py 4128 2016-04-30 07:04:12Z jeanluc $
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
Created on 14 avr. 2015

@author: jeanluc
'''

import os
from metaphor.chem_gm.core.metamolecule import MetaMolecule
from metaphor.monal.datareader._excel import Excel
from metaphor.chem_gm.core.gmprograms import dataiterator

path0 = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

#testfile1 = os.path.join(path0, "test", "testfiles", "SmileCasTab-JLP.xlsx")NCI_Problemes.rtf
testfile0 = os.path.join(path0, "test", "testfiles", "NCI_Problemes.txt")
testfile1 = os.path.join(path0, "test", "testfiles", "NCI_aug00_SMI.txt")
testfile2 = os.path.join(path0, "test", "testfiles", "SmileCasTabIso.txt")
#targetfile = os.path.join(path0, "test", "testfiles", "SmileCasTabIso.txt") 

if __name__ == '__main__':
    assert os.path.exists(testfile1)
    assert os.path.exists(testfile2)
    #iter = dataiterator(testfile, filetype="xlsx", datarange="A1C10")
    
    no = 0
#     source = Excel(testfile, load=True)
#     with open(targetfile, "w") as ff:
#         for no, row in enumerate(source.iterData("A1:C115408")):
#             if not (no % 1000):
#                 print no
#             try:
#                 sname = row[1].strip()
#                 smiles = row[2].strip()
#                 if ('@' in smiles) or ('/' in smiles) or ('\\' in smiles):
#                     st = "%s\t%s\t%s\n"%(smiles, (no+1), sname)
#                     ff.write(st.encode('utf-8'))
#             except:
#                 pass
    
    
#     source = Excel(testfile1, load=True)
#     for no, row in enumerate(source.iterData("A1:C115408")):
#         if not(no % 100):
#             #print no
#             pass
#         smiles = row[2]
#         sname = row[0]
#         try:
#             MetaMolecule(smiles, sname)
#         except Exception, err:
#             lst0 = err.message.split(":")
#             try:
#                 lst1 = lst0[1].split(";")
#                 #if not lst1[1].startswith("H)"):
#                 print no, lst1[0], " ->  ", lst1[1]
#             except Exception, err:
#                 print no, err
                
                
    with open(testfile2, "r") as ff:
        for no, line in enumerate(ff.readlines()):
            lst = line.split("\t")
            if len(lst) < 2:
                continue
            try:
                smiles = lst[0].strip()
                if not smiles.startswith("#"):
                    smilst = MetaMolecule(smiles, "m_%s"% lst[1])
                if not (no % 1000):
                    print(no)
            except Exception as err:
                print( no, lst[1], err)
    print( "Done %d" % (no))
                
    with open(testfile1, "r") as ff:
        for no, line in enumerate(ff.readlines()):
            lst = line.split("\t")
            if len(lst) < 2:
                continue
            try:
                smiles = lst[0].strip()
                smilst = MetaMolecule(smiles, "m_%s"% lst[1])
                if not (no % 1000):
                    print(no)
            except Exception as err:
                print(no, lst[1], err)
                
    print("Done %d" % (no))
    print()