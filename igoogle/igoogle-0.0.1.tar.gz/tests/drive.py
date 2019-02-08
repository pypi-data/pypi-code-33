
from tests import *

from igoogle.drive import *
#from . import dbg

import unittest




class SheetReaderTestCase(unittest.TestCase):

    def test_init(self):
        print(f"\n\n testfuncname : {inspect.stack()[0][3]}")
        url = 'https://docs.google.com/spreadsheets/d/1MM2_bUcb1vDt-9epfmP9CN5Oj62idoxzCHIUQn4CVck/edit#gid=0'
        s = SheetReader(url)
        dbg.print_obj(s)
        #sheets = s.get_sheets()


def main():
    unittest.main()
