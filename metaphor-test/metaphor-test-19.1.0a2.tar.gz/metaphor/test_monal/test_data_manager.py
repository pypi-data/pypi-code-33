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
Created on 22 avr. 2011

@author: jeanluc
'''
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from metaphor.monal.driver import DataManager
from metaphor.monal.datareader.excelsource import get_dataframe

import unittest
from io import StringIO
import numpy
import os
from metaphor.monal.datareader.check_sigs import check_sig, compile_sigs

testFileDir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testFiles'))
FileData_L153 = os.path.join(testFileDir, 'L_153.csv')
fileData_Base321E_chem = os.path.join(testFileDir, "Base321E_chem.xlsx")

# class TestSignatures(unittest.TestCase):
#     def test_xls(self):
#         filename = fileData_Base321E_chem
#         compile_sigs()
#         check_sig(filename)

class TestXLS(unittest.TestCase):
    def test_loadDataFrame(self):
        filename = fileData_Base321E_chem
        frame = get_dataframe(filename, datarange="DATA")
        self.assertEqual(frame.shape, (321, 4))
        self.assertEqual(frame.columns[0], "Noms")
        self.assertEqual(frame.columns[1], "Smiles")
        self.assertEqual(frame.columns[3], "M")
        self.assertEqual(frame.columns[2], "LogP")
        self.assertEqual(frame["Noms"][0], "PROPANE")
    
class TestCSV(unittest.TestCase):
    def test_loadDataFrame(self):
        filename = FileData_L153
        frame = get_dataframe(filename, filetype='csv')
        self.assertEqual(frame.shape, (153, 6))
        self.assertEqual(frame.columns[0], "X1")
        self.assertEqual(frame.columns[4], "X5")
        self.assertEqual(frame.columns[5], "Y")
        self.assertEqual(frame["Y"][0], 32)

class TestNdArrayBasedDataManager (unittest.TestCase):
    def test_not_failing_with_empty_input (self):
        s = numpy.asarray ([[]], float)
        man = DataManager (data = s, style="array")
        self.assertEqual (None, man.titles)
        self.assertEqual (0, len (man))
        self.assertEqual (0, man.width)
        self.assertEqual (False, man.has_titles())

    def test_not_failing_with_cell_input (self):
        s = numpy.asarray ([[1.1]], float)
        man = DataManager (data = s, style="array")
        self.assertEqual (None, man.titles)
        self.assertEqual (1, man.length)
        self.assertEqual (1, man.width)
        self.assertEqual (False, man.has_titles())

class TestOtherStyleBasedDataManager (unittest.TestCase):
    def test_failing_with_unknown_style (self):
        "Raises an exception if the style in unknown"
        s = StringIO (u"")
        self.assertRaises (NotImplementedError, DataManager, datasource = s, style="foo")

class TestCsvBasedDataManager (unittest.TestCase):
    def test_not_failing_with_empty_input (self):
        s = StringIO (u"")
        man = DataManager (datasource = s)
        self.assertEqual (None, man.titles)
        self.assertEqual (0, man.length)
        self.assertEqual (0, man.width)
        self.assertEqual (False, man.has_titles())

    def test_title_with_only_2_titles (self):
        s = StringIO (u"foo,bar\n")
        man = DataManager (datasource = s)
        self.assertEqual (["foo", "bar"], man.titles)
        self.assertEqual (0, man.length)
        self.assertEqual (2, man.width)
        self.assertEqual (True, man.has_titles())

    def test_title_with_2_titles_and_data (self):
        s = StringIO (u"foo,bar\n1.1,2.2\n3.3,4.4\n3.6,4.1\n")
        man = DataManager (datasource = s)
        self.assertEqual (['foo', 'bar'], list(man.titles))
        self.assertEqual (3, man.length)
        self.assertEqual (2, man.width)
        self.assertEqual (True, man.has_titles())

    def test_title_with_2_titles_and_data_semicolumn (self):
        s = StringIO (u"foo;bar\n1.1;2.2\n3.3;4.4\n3.6;4.1\n")
        man = DataManager (datasource = s)
        self.assertEqual (["foo", "bar"], man.titles)
        self.assertEqual (3, man.length)
        self.assertEqual (2, man.width)
        self.assertEqual (True, man.has_titles())

    def test_title_with_2_titles_and_data_tab (self):
        s = StringIO (u"foo\tbar\n1.1\t2.2\n3.3\t4.4\n3.6\t4.1\n")
        man = DataManager (datasource = s)
        self.assertEqual (["foo", "bar"], man.titles)
        self.assertEqual (3, man.length)
        self.assertEqual (2, man.width)
        self.assertEqual (True, man.has_titles())

    def test_title_with_2_titles_and_data_space (self):
        s = StringIO (u"foo bar\n1.1 2.2\n3.3 4.4\n3.6 4.1\n")
        man = DataManager (datasource = s)
        self.assertEqual (["foo", "bar"], man.titles)
        self.assertEqual (3, man.length)
        self.assertEqual (2, man.width)
        self.assertEqual (True, man.has_titles())

    def test_extract_ndarray_first_column (self):
        s = StringIO (u"foo,bar\n1.1,2.2\n3.3,4.4\n5.5,6.6\n")
        man = DataManager (datasource = s)
        extracted = man.as_array (indexes = (0,))
        self.assertEqual (1.1, extracted [0][0])
        self.assertEqual (1, len (extracted [0]))
        self.assertEqual (3, len (extracted))
        self.assertEqual (numpy.ndarray, type (extracted))

    def test_extract_ndarray_second_first_column (self):
        s = StringIO (u"foo,bar\n1.1,2.2\n3.3,4.4\n5.5,6.6\n")
        man = DataManager (datasource = s)
        extracted = man.as_array (indexes = (1, 0))
        self.assertEqual (1.1, extracted [0][1])
        self.assertEqual (2.2, extracted [0][0])
        self.assertEqual (2, len (extracted [0]))
        self.assertEqual (3, len (extracted))
        self.assertEqual (numpy.ndarray, type (extracted))

    def test_title_with_2_titles_and_data_and_empty_lines (self):
        s = StringIO (u"foo,bar\n\n1.1,2.2\n3.3,4.4\n\n3.6,4.1\n")
        man = DataManager (datasource = s)
        self.assertEqual (["foo", "bar"], man.titles)
        self.assertEqual (3, man.length)
        self.assertEqual (2, man.width)
        self.assertEqual (True, man.has_titles())

    def test_title_with_no_title_and_data (self):
        s = StringIO (u"1.1,2.2\n3.3,4.4\n3.6,4.1\n")
        man = DataManager (datasource = s)
        self.assertEqual (None, man.titles)
        self.assertEqual (3, man.length)
        self.assertEqual (2, man.width)
        self.assertEqual (False, man.has_titles())

if __name__ == "__main__":    
    unittest.main()