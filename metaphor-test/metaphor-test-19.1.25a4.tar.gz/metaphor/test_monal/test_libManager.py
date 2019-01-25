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
Created on 17 oct. 2016

@author: jeanluc
'''
import unittest
import os
from metaphor.monal import driver as dr, model as ml, monalconst as C
from metaphor.monal.library import libmanager as lm
from six import PY3
from ctypes import create_string_buffer, c_void_p, byref
import numpy as np
from tempfile import mkdtemp
import shutil

VERBOSE = 3

testFileDir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testFiles'))


# testSO_1 = os.path.join(testFileDir, "libbase321e_chem_chi1_grds1_1n_ce4.so")

def newModel(ne=1, ns=1, nc=3, activ='TANH', APolyType=0,
             ILayer=0, INeuron=0, NState=0, modelname="model_0"):
    return ml.Network(modelname=modelname, inputs=ne, outputs=ns, hidden=nc, 
                 activfunc=activ, polytype=APolyType, nosynapse=0)

def newDriver(ne=1, ns=1, nc=3, activ='TANH', APolyType=0,
             ILayer=0, INeuron=0, NState=0, modelname="model_0"):
    return dr.Driver(modelname=modelname, inputs=ne, outputs=ns, hidden=nc, 
                 activfunc=activ, polytype=APolyType, nosynapse=0)
      
class TestLibManager(unittest.TestCase):
    modulename = ""
    def setUp(self):
        self.tempdir = mkdtemp()
        driver = newDriver(ne=5, nc=4)
        self.tempdir = mkdtemp(suffix='monal_test')
        modulename = driver.saveModel(filename="", savingformat=C.SF_DLL, 
            count=0, savedir=self.tempdir, tempdir=self.tempdir, package="", 
            modeltemplate="m%d_", keeptemp=0, verbose=VERBOSE, compiler="", 
            forcelib=False, appliname="nn1")
        
        self.modulename = os.path.join(self.tempdir, modulename)
        pass
    
    def tearDown(self):
        shutil.rmtree(self.tempdir)
        self.modulename = ""

    def testLibmanager(self):
        res = lm.libCheck(self.modulename, "paramCount")
        self.assertEqual(res["paramCount"], 29)
        
#     def testlibManager2(self):
#         res = lm.libCheck(self.modulename, baselen=None)
#         self.assertEqual(res["baselen"], 321)
#         
#     def testBase(self):
#         res = lm.libCheck(self.modulename, base=None, keep=True)
#         dim = res["base"]
#         lib = res['lib']
#         
#         rtyp = create_string_buffer(dim + 1)
#         res = lm.libCheck("", base=byref(rtyp), lib=lib)
#         result = rtyp.value
#         if PY3:
#             self.assertEqual(result, b'Base321E_chem')
#         else:
#             self.assertEqual(result, "Base321E_chem")
        
    def testNorm(self):
        res = lm.libCheck(self.modulename, getnorm=0, keep=True)
        lib = res['lib']
        # lecture de la dimension de la normalisation
        dim = res["getnorm"]
        self.assertEqual(dim, 2)
        target = np.zeros((dim,), dtype=np.double)
        target_p = c_void_p(target.ctypes.data)
        
        res = lm.libCheck("", getnorm=target_p, lib=lib, keep=True)
        # lecture de la normalisation par defaut
        self.assertEqual(res["getnorm"], 0)
        self.assertEqual(target[0], 1.0)
        self.assertEqual(target[1], 0.0)
        
        source = np.asarray((1.25, 2.55))
        source_p = c_void_p(source.ctypes.data)
        res = lm.libCheck("", setnorm=source_p, lib=lib, keep=True)
        # affectation d'une normalisation
        self.assertEqual(res["setnorm"], 0)
        
        res = lm.libCheck("", getnorm=target_p, lib=lib)
        # lecture de la nouvelle normalisation
        self.assertEqual(res["getnorm"], 0)
        self.assertEqual(target[0], 1.25)
        self.assertEqual(target[1], 2.55)

if __name__ == "__main__":
    unittest.main()