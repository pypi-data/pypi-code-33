# $Id: test_toolbox.py 4242 2016-09-29 16:01:42Z jeanluc $
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
from metaphor.nntoolbox import utils as tb
#from monal.util import toolbox as tb
import os, shutil, tempfile
import numpy as np
from io import StringIO
import time
import unittest

class TestToolbox(unittest.TestCase):

    def test_sandardDeviation(self):
        nx, ny = 5, 10
        data = np.zeros((nx, ny))
        for ind in range(nx):
            vv = data[ind]
            vv[1] = ind
            vv[4] = 2*ind
        res = tb.sandardDeviation(data, 1, 4)
        assert abs(res - 2.45) < 0.01
        
    def test_splitsecs(self):
        res = tb.splitsecs(178851)
        assert res == (51, 40, 1, 2)
    
    def test_deltatime2str(self):
        d1 = tb.strToDateTime("25/03/1975 11:25:10" )
        d2 = tb.strToDateTime("31/12/2014 12:30:00" ) 
        d3 = d2 - 0.01256
        res = tb.deltaDateTimeToStr(d2 - d1)
        assert res == "14526 days 1 h. 4 min."
        res2 = tb.deltaDateTimeToStr(d2 - d3)
        assert res2 == "12 msec."
    
    def test_findinlist(self):
        lst = list(range(10))
        assert tb.findinlist(lst, 5) == 5
        assert tb.findinlist(lst, 20) == -1
    
    def test_splitFileName(self):
        val = tb.splitFileName("a.b.c")
        assert val == ("a.b", "c")
    
    def test_fillstr(self):
        val = tb.fillstr(5, 'n')
        assert val == "nnnnn"
    
    def test_rightjustify(self):
        val = tb.rightjustify("aa", 4)
        assert val == "  aa"
        val = tb.rightjustify("aaa", 1)
        assert val == "aaa"
        
    def test_leftjustify(self):
        val = tb.leftjustify("aa", 4)
        assert val == "aa  "
        val = tb.leftjustify("aaa", 1)
        assert val == "aaa"
    
    def test_Null(self):
        o = tb.Null()
        assert len(o) == 0
        assert o() == o
        assert repr(o) == "Null()"
        assert o.anything == o
        assert o * 5 == 0
        assert o + 5 == 5
        assert o - 5 == -5

    def test_swapextension(self):  #filename, before, after, forceafter=False
        val = tb.swapextension("toto.txt", None, ".csv")
        assert val == "toto.csv"
        val = tb.swapextension("toto.txt", None, "")
        assert val == "toto"
        val = tb.swapextension("toto.txt", ".txt", "")
        assert val == "toto"
        val = tb.swapextension("toto.txt", "txt", "")
        assert val == "toto."
        val = tb.swapextension("toto.txt", ".asl", ".csv")
        assert val == "toto.txt"
        val = tb.swapextension("toto.txt", ".asl", ".csv", True)
        assert val == "toto.txt.csv"
    
    def test_changeChar(self): #source, oldc, newc, nodoublenew=False
        val = tb.changeChar("abcdef", 'b', 'z')
        assert val == "azcdef"
        val = tb.changeChar("abbdef", 'b', 'z')
        assert val == "azzdef"
        val = tb.changeChar("abbdef", 'b', 'z', True)
        assert val == "azdef"
    
    def test_quote(self):
        val = tb.quote("abcd")
        assert val == "'abcd'"
        val = tb.quote("abcd", '"')
        assert val == '"abcd"'
        val = tb.quote('"abcd"', '"')
        assert val == '"abcd"'
    
    def test_unquote(self):
        val = tb.unquote("'abcd'")
        assert val == 'abcd'
        val2 = tb.unquote('"abcd"')
        assert val2 == "abcd"
        val = tb.unquote(b"'abcd'")
        assert val == 'abcd'.encode()
    
    def test_splitex(self):
        val = tb.splitex("abcdef", "cd")
        assert val == ["ab", "ef"]
        val = tb.splitex("abcdef", "c\\d")
        assert val == ["abcdef"]
    
    def test_listEqual(self):
        val = tb.listEqual(list(range(8)), list(range(8)))
        assert val
        val = tb.listEqual(list(range(8)), [0, 1, 2, 2, 4, 5, 6, 7])
        assert not val

def run():
    unittest.main()
    
if __name__ == "__main__":
    run()
#     import nose
#     nose.runmodule()
    