
# Copyright (C) 2019 Frank Sauerburger

from builtins import int   # Compatibility with 2.7

import unittest

from pyveu import join_or_none

class JoinOrNoneTestCase(unittest.TestCase):
    """
    Test for the join_or_none() helper method.
    """

    def test_join_or_none_zero(self):
        """
        Check that both strings are used if neither is None.
        """
        self.assertEqual(join_or_none("Hello", "World"), "HelloWorld")

    def test_join_or_none_first(self):
        """
        Check that only the second string is returned if the first string is
        None.
        """
        self.assertEqual(join_or_none(None, "World"), "World")

    def test_join_or_none_second(self):
        """
        Check that only the first string is returned if the second string is
        None.
        """
        self.assertEqual(join_or_none("Hello", None), "Hello")

    def test_join_or_none_both(self):
        """
        Check that None is returned if both arguments are None.
        """
        self.assertEqual(join_or_none(None, None), None)

