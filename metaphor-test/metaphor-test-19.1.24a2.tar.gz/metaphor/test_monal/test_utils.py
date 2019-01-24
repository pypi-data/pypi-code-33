# $Id: test_utils.py 4242 2016-09-29 16:01:42Z jeanluc $
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
Created on 29 oct. 2014

@author: jeanluc
'''

from metaphor.monal.util.utils import*
import os, shutil, tempfile
#from io import StringIO
from metaphor.monal.lcode.ccrypt import run as crun
import unittest

DO_TEST_COMPILE_LIB = 0 # mettre a 0 pour les tests in situ
TEST_FOLDER = tempfile.mkdtemp()
#ORIGINAL_FOLDER = os.getcwd()

sourcedir = ""

class TestUtils(unittest.TestCase):

    def setup(self):
        #TEST_FOLDER = tempfile.mkdtemp()
        global sourcedir
        if is_windows():
            sourcedir = os.path.join(getcurrentsitepackages(), 'metaphor', src)
#             sourcedir = "C:\\Users\jeanluc\workspace\MonalPy\src"
        if is_linux():
            sourcedir = '/Users/jeanluc/Documents/LiClipseWorkspace'
            #"/Users/Shared/workspace"
        if is_mac():
            sourcedir = '/Users/jeanluc/Documents/LiClipseWorkspace'
            #"/Users/Shared/workspace"
            
    def teardown(self):
        if os.path.exists(TEST_FOLDER):
            shutil.rmtree(TEST_FOLDER)
    
    def test_cryptfile(self):
        # prepare ,cryptfiles
        res = crun(False, False)        
#        res = crun(True)
        assert res
    
    def test_compilemonallib(self):
        if DO_TEST_COMPILE_LIB:
            res = compilemonallib(force=True, outputdir=TEST_FOLDER)
            assert res
        
    def test_getapplibase(self):
#         if is_windows():
#             target = "C:/Python27/libs/site-packages/AppData/toto"
#         if is_linux():
#             target = "/Users/jeanluc/Library/Python/2.7/toto"
#         if is_mac():
#             target = "/Users/jeanluc/.local/toto"
            #"/Users/jeanluc/Library/Python/2.7/toto"
    
        cible = os.path.join("metaphor", "monal")
        res = getapplibase(cible, False)
        # ssert res == target, "result=%s"%res
        self.assertTrue(os.path.exists(res), "Monal appli base does not exists")
        
#     def test_appdatadir(self):
# #         if is_windows():
# #             target = os.path.join(getcurrentsitepackages(), 'Appdata')
# #             #"C:/Python27/libs/site-packages/AppData"
# #         elif is_linux():
# #             target = "/Users/jeanluc/appdata/"
# #         elif is_mac():
# #             target = "/Users/jeanluc/Applications/"
#             
#         res = appdatadir(APPNAME="")
#         #print(res)
#         #assert res == target
#         self.assertTrue(os.path.exists(res), "Appli dir does not exists")
        
    def test_CCharOnlys(self):
        res = CCharOnlys("123abcAZ@")
        assert res == "123abcAZ_"
        res = CCharOnlys("123abcAZ@", extended=True)
        assert res == "_123abcAZ_"
        res = CCharOnlys("123abcAZ@", nostartint=True)
        assert res == "_23abcAZ_"
        res = CCharOnlys(u"123abcAZ@#&")
        assert res == u"123abcAZ___"
        res = CCharOnlys(u"123abcAZ@", extended=True)
        assert res == u"_123abcAZ_"
        res = CCharOnlys(u"123abcAZ@#", nostartint=True)
#         assert res == u"_23abcAZ__"
#         res = CCharOnlys()
#         assert res == u"euac"
        res = CCharOnlys(u"--")
        assert res == u"__"
        
     
#     def runTest(self):
#         self.test_CCharOnlys()
#         self.test_appdatadir()
#         self.test_getapplibase()
#         self.test_compilemonallib()

def run():
    unittest.main()

if __name__ == "__main__":
    run()
#     import nose
#     nose.runmodule()
