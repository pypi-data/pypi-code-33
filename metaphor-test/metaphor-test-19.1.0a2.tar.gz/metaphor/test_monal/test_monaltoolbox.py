# $Id: test_monaltoolbox.py 4242 2016-09-29 16:01:42Z jeanluc $
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
Created on 30 oct. 2014

@author: jeanluc
'''
import numpy as np
#from .. import nntoolbox
from metaphor.nntoolbox.utils import floatEx
from metaphor.monal.util.monaltoolbox import *
from numpy import isnan
import unittest

class TestMonalToolbox(unittest.TestCase):

    def test_multidot(self):
        a = np.ones((3, 4))
        b = np.ones((4, 5))    
        c = np.ones((5, 3))
        val = multidot(a, b, c)
        res = val - np.ones((3, 3))*20
        assert not res.any()
        val = multidot(a.T, b.T, c.T, reverse=True)
        res = val - np.ones((3, 3))*20
        assert not res.any()
    
    def test_isStrNum(self):
        assert isStrNum("12.5")
        assert isStrNum("12.5E-5")
        assert not isStrNum("12 5E-5")
    
    def test_sign(self):
        assert sign(1, 2) == 1
        assert sign(1, -2) == -1
    
    def test_floatEx(self):
        assert floatEx("7.5") == 7.5
        assert floatEx("7,5") == 7.5
        assert np.isnan(floatEx("7 5"))
    
    #def runTest(self):
        #unittest.main()
     

if __name__ == "__main__":
    unittest.main()
