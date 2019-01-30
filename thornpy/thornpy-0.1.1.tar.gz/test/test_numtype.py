"""Tests the functions in the numtype module.
"""
import unittest
from thornpy import numtype

FLOAT_STRING = '1.0'
INT_STRING = '1'

class Test_StrIsFloat(unittest.TestCase):
    """Tests that numtype.str_is_float() returns correct booleans
    """
    def setUp(self):
        return

    def test_float(self):
        """Test that str_is_float() returns true when a float is passed
        """
        self.assertTrue(numtype.str_is_float(FLOAT_STRING))

    def test_int(self):
        """Test that str_is_float() returns false when an int is passed
        """
        self.assertFalse(numtype.str_is_float(INT_STRING))

    def tearDown(self):
        return

class Test_StrIsInt(unittest.TestCase):
    """Tests that numtype.str_is_int() returns correct booleans
    """

    def setUp(self):
        return

    def test_int(self):
        """Test that str_is_int() returns true when an int is passed
        """
        self.assertTrue(numtype.str_is_int(INT_STRING))

    def test_float(self):
        """Test that str_is_int() returns true when an int is passed
        """
        self.assertFalse(numtype.str_is_int(FLOAT_STRING))

    def tearDown(self):
        return
