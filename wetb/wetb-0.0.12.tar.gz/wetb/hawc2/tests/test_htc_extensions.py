'''
Created on 17/07/2014

@author: MMPE
'''
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from io import open
from builtins import str
from builtins import zip
from future import standard_library
standard_library.install_aliases()
import os
import unittest

from datetime import datetime
from wetb.hawc2.htc_file import HTCFile, HTCLine

import numpy as np


tfp = os.path.join(os.path.dirname(__file__), 'test_files/htcfiles/')  # test file path
class TestHtcFile(unittest.TestCase):

    def test_get_shear(self):
        htc = HTCFile(tfp+'test.htc')
        self.assertEqual(htc.get_shear()(100), 10*(100/119)**.2)
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
