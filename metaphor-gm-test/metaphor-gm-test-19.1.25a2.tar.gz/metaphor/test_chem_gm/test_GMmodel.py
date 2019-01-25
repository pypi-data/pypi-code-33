# $Id: test_GMmodel.py 4129 2016-05-01 03:34:44Z jeanluc $
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
import unittest, os
from metaphor.chem_gm.core.GMmodel import smiles2model
from metaphor.chem_gm.core.metamolecule import MetaMolecule
from metaphor.monal.util.utils import appdatadir
from metaphor.monal.model import PseudoMatrix
from metaphor.monal.monalconst import ID_COMPUTE, ID_DIFF #, ID_DIFF_SEC
#from itertools import izip
from time import time
import tempfile, shutil

smilescistrans = r'O=C(NC/C=C\CN1)CN(CC(O)=O)CCN(CC(O)=O)CCN(CC(O)=O)CC1=O'
smilescistrans2 = r'O=C(NCC=CCN1)CN(CC(O)=O)CCN(CC(O)=O)CCN(CC(O)=O)CC1=O'

def timeit(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print('%r (%r, %r) %2.2f sec' % (method.__name__, args, kw, te-ts))
        return result

    return timed

class Test_TokenList(unittest.TestCase):
    
    def setUp(self):
        self.workingdir = tempfile.mkdtemp()
 
    def tearDown(self):
        if os.path.exists(self.workingdir):
            shutil.rmtree(self.workingdir)

#     def setUp(self):
#         self.workingdir = appdatadir("", "autotest")
#         pass
#     
#     def tearDown(self):
#         pass
#         #print "bye"

    def test_smiles2model1(self):
        smiles = smilescistrans    
        tokens = MetaMolecule(smiles, 1)
        unitfile = os.path.join(self.workingdir, "model", "unit.nml")
        outputindex = 3
        name = "MyTest"
        atoms, grade, iso, chiral, occurs, occurmols, cycleloc, _ = tokens.analyse()
        diststruct, tokens = smiles2model( 
            smiles, 
            outputindex=outputindex,
            modelname = name,
            unitfilename=unitfile, 
            hidden=2,
            maxgrade=grade, 
            centraux=atoms, 
            atoms =atoms,
            isomer=iso)
        first = [16, 15, 14, 9, 8, 1, 0, 3, 4]
        #first = [9, 8, 1, 0, 3, 4, 5, 6, 7, 26]
        for ind, val in enumerate(diststruct):
            assert val[0].numero == first[ind], "(%d, %s / %s)"%(ind, val[0].numero, first[ind])

    def test_smiles2model2(self):
        smiles = smilescistrans    
        unitfile = os.path.join(self.workingdir, "model", "unit.nml")
        outputindex = 6
        name = "MyTest"
        diststruct, tokens, atomlist = smiles2model( 
            smiles, 
            outputindex=outputindex,
            modelname = name,
            unitfilename=unitfile, 
            centraux=1)
        first = [16, 15, 14, 9, 8, 1, 0, 3, 4]
        #first = [9, 8, 1, 0, 3, 4, 5, 6, 7, 26]
        for ind, val in enumerate(diststruct):
            assert val[0].numero == first[ind], "(%d, %s / %s)"%(ind, val[0].numero, first[ind])
        assert not hasattr(tokens, "brokenbonds") or not len(tokens.brokenbonds)
        assert len(atomlist) == 3  #["C", "N", "O"]

    def test_smiles2model3(self):
        smiles = smilescistrans    
        unitfile = os.path.join(self.workingdir, "model", "unit.nml")
        outputindex = 8
        name = "MyTest"
        diststruct, tokens, atomlist, driver = smiles2model( 
            smiles, 
            outputindex=outputindex,
            modelname = name,
            #outputname = "pkA",
            unitfilename=unitfile,
            isomer=2,
            #hidden=2,
            #maxgrade=grade, 
            centraux=1) 
            #atoms =3)
            #isomer=iso)
        #first = [16, 15, 14, 9, 8, 1, 0, 3, 4]
        #for ind, val in enumerate(diststruct):
        #    assert val[0].numero == first[ind], "(%s / %s)"%(val[0].numero, first[ind])
        #for val in tokens:
        #    print val
        #for val in diststruct:
        #    print val
        assert not hasattr(tokens, "brokenbonds") or not len(tokens.brokenbonds)
        assert len(atomlist) == 3  #["C", "N", "O"]
        
        #print driver.NMLstring
    def test_matrixModel(self):
        smiles = smilescistrans    
        unitfile = os.path.join(self.workingdir, "model", "unit.nml")
        outputindex = 8
        name = "MyTest"
        diststruct, tokens, atomlist, driver = smiles2model( 
            smiles, 
            outputindex=outputindex,
            modelname = name,
            unitfilename=unitfile,
            isomer=2,
            centraux=1,
            compactness=1) 
        model0 = driver.mainModel
        model0.initWeights()
        model1 = PseudoMatrix(master=model0)
        # model1 est cree avant initialisation des poids de model0
        model0.initWeights(seed=1947)
        #print model0.weights
        #model1.initWeights(seed=1947)
        
        model1.weights = model0.weights
        # les poids de model0 sont copies dans model1
        #print model1.weights
        res0 = model0(computelevel=ID_DIFF, original=False)
        res1 = model1(computelevel=ID_DIFF, original=False)
#         print(res0[0])
#         print(res1[0])
#         assert res0[0] == res1[0]
#         print res0[1]
#         print res1[1]
#         print res0[1] - res1[1]
#         for ind, (r0, r1) in enumerate(zip(res0[1], res1[1])):
#             print(ind, "\t", r1-r0)
        nb = 1000
        t0 = time()
        for i in range(nb):
            model0.initWeights()
            res0 = model0(computelevel=ID_DIFF, original=False)
        t1 = time()
        for i in range(nb):
            model1.initWeights()
            res0 = model0(computelevel=ID_DIFF, original=False)
        t2 = time()
#         print("Network", t1 - t0)
#         print("PMatrix", t2 - t1)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.Test_TokenList']
    unittest.main()