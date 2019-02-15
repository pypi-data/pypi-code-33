import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from alcathous.nodatabehavior import NoDataBehavior


class TestNoDataBehaviorEnum(unittest.TestCase):
    def test_enum(self):
        self.assertEqual(NoDataBehavior.LAST_VALID, NoDataBehavior.get_enum("last_valid"))
        self.assertEqual(NoDataBehavior.LAST_VALID, NoDataBehavior.get_enum("LAST_VALID"))
        self.assertEqual(NoDataBehavior.EMPTY_MESSAGE, NoDataBehavior.get_enum("EMPTY_MESSAGE"))
        self.assertEqual(NoDataBehavior.MUTE, NoDataBehavior.get_enum("mute"))
        self.assertRaises(ValueError, NoDataBehavior.get_enum, "")
        self.assertRaises(ValueError, NoDataBehavior.get_enum, "lastvalid")

if __name__ == '__main__':
    unittest.main()
