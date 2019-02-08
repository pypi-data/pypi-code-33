
# Copyright (C) 2018-19 Frank Sauerburger

from builtins import int   # Compatibility with 2.7

import unittest

from pyveu import _round, _floor

class MathTestCases(unittest.TestCase):
    """
    This class implements test cases for the _round() and _floor() methods
    which should provided consistent behavior independent of the Python
    version.
    """
    def test_round_pos_half_int(self):
        """
        Check that positive half-integers are rounded towards greater values.
        """
        self.assertEqual(_round(0.5), 1)
        self.assertEqual(_round(1.5), 2)
        self.assertEqual(_round(2.5), 3)
        self.assertEqual(_round(3.5), 4)
        self.assertEqual(_round(120.5), 121)
        self.assertEqual(_round(121.5), 122)
        self.assertEqual(_round(122.5), 123)

    def test_round_pos_int(self):
        """
        Check that positive integers are returned as is.
        """
        self.assertEqual(_round(0), 0)
        self.assertEqual(_round(1), 1)
        self.assertEqual(_round(2), 2)
        self.assertEqual(_round(3), 3)
        self.assertEqual(_round(120), 120)
        self.assertEqual(_round(121), 121)
        self.assertEqual(_round(122), 122)

    def test_round_pos_upper(self):
        """
        Check that floats with the first decimal digit in the upper half
        (0.5-0.9) are rounded towards greater values.
        """
        self.assertEqual(_round(0.501), 1)
        self.assertEqual(_round(1.6), 2)
        self.assertEqual(_round(2.92), 3)
        self.assertEqual(_round(3.82), 4)
        self.assertEqual(_round(120.6), 121)
        self.assertEqual(_round(121.9), 122)
        self.assertEqual(_round(122.902), 123)

    def test_round_pos_lower(self):
        """
        Check that floats with the first decimal digit in the lower half
        (0.1-0.4) are rounded towards smaller values.
        """
        self.assertEqual(_round(0.49), 0)
        self.assertEqual(_round(1.3), 1)
        self.assertEqual(_round(2.1), 2)
        self.assertEqual(_round(3.01), 3)
        self.assertEqual(_round(120.39), 120)
        self.assertEqual(_round(121.109), 121)
        self.assertEqual(_round(122.401), 122)

    def test_round_pos_position(self):
        """
        Check that the second argument controls the rounding position.
        """
        self.assertEqual(_round(57721.5664901532,  7),  57721.5664902)
        self.assertEqual(_round(57721.5664901532,  6),  57721.566490)
        self.assertEqual(_round(57721.5664901532,  5),  57721.56649)
        self.assertEqual(_round(57721.5664901532,  4),  57721.5665) 
        self.assertEqual(_round(57721.5664901532,  3),  57721.566)
        self.assertEqual(_round(57721.5664901532,  2),  57721.57)
        self.assertEqual(_round(57721.5664901532,  1),  57721.6)
        self.assertEqual(_round(57721.5664901532,  0),  57722)
        self.assertEqual(_round(57721.5664901532, -1),  57720)
        self.assertEqual(_round(57721.5664901532, -2),  57700)
        self.assertEqual(_round(57721.5664901532, -3),  58000)
        self.assertEqual(_round(57721.5664901532, -4),  60000)
        self.assertEqual(_round(57721.5664901532, -5), 100000)
        self.assertEqual(_round(57721.5664901532, -6),      0)

        self.assertEqual(_round(0, -6),      0)
        self.assertEqual(_round(0,  6),      0)

    def test_round_pos_return_type(self):
        """
        Check that the return type is an integer for positive numbers.
        """
        self.assertIsInstance(_round(12.32), int)
        self.assertIsInstance(_round(1.0), int)
        self.assertIsInstance(_round(1), int)
        self.assertIsInstance(_round(0), int)

    def test_round_neg_half_int(self):
        """
        Check that negative half-integers are rounded towards greater
        magnitudes, i.e., smaller values.
        """
        self.assertEqual(_round(-0.5), -1)
        self.assertEqual(_round(-1.5), -2)
        self.assertEqual(_round(-2.5), -3)
        self.assertEqual(_round(-3.5), -4)
        self.assertEqual(_round(-120.5), -121)
        self.assertEqual(_round(-121.5), -122)
        self.assertEqual(_round(-122.5), -123)

    def test_round_neg_int(self):
        """
        Check that negative integers are returned as is.
        """
        self.assertEqual(_round(-0), -0)
        self.assertEqual(_round(-1), -1)
        self.assertEqual(_round(-2), -2)
        self.assertEqual(_round(-3), -3)
        self.assertEqual(_round(-120), -120)
        self.assertEqual(_round(-121), -121)
        self.assertEqual(_round(-122), -122)

    def test_round_neg_lower(self):
        """
        Check that floats with the first decimal digit in the lower half
        (-0.5 to -0.9) are rounded towards greater magnitudes, i.e., smaller
        values.
        """
        self.assertEqual(_round(-0.501), -1)
        self.assertEqual(_round(-1.6), -2)
        self.assertEqual(_round(-2.92), -3)
        self.assertEqual(_round(-3.82), -4)
        self.assertEqual(_round(-120.6), -121)
        self.assertEqual(_round(-121.9), -122)
        self.assertEqual(_round(-122.902), -123)

    def test_round_neg_upper(self):
        """
        Check that floats with the first decimal digit in the lower half
        (-0.1 to -0.4) are rounded towards smaller magnitudes, i.e., greater
        values.
        """
        self.assertEqual(_round(-0.49), -0)
        self.assertEqual(_round(-1.3), -1)
        self.assertEqual(_round(-2.1), -2)
        self.assertEqual(_round(-3.01), -3)
        self.assertEqual(_round(-120.39), -120)
        self.assertEqual(_round(-121.109), -121)
        self.assertEqual(_round(-122.401), -122)

    def test_round_neg_position(self):
        """
        Check that the second argument controls the rounding position.
        """
        self.assertEqual(_round(-57721.5664901532,  7),  -57721.5664902)
        self.assertEqual(_round(-57721.5664901532,  6),  -57721.566490)
        self.assertEqual(_round(-57721.5664901532,  5),  -57721.56649)
        self.assertEqual(_round(-57721.5664901532,  4),  -57721.5665) 
        self.assertEqual(_round(-57721.5664901532,  3),  -57721.566)
        self.assertEqual(_round(-57721.5664901532,  2),  -57721.57)
        self.assertEqual(_round(-57721.5664901532,  1),  -57721.6)
        self.assertEqual(_round(-57721.5664901532,  0),  -57722)
        self.assertEqual(_round(-57721.5664901532, -1),  -57720)
        self.assertEqual(_round(-57721.5664901532, -2),  -57700)
        self.assertEqual(_round(-57721.5664901532, -3),  -58000)
        self.assertEqual(_round(-57721.5664901532, -4),  -60000)
        self.assertEqual(_round(-57721.5664901532, -5), -100000)
        self.assertEqual(_round(-57721.5664901532, -6),       0)

        self.assertEqual(_round(-0, -6),      0)
        self.assertEqual(_round(-0,  6),      0)

    def test_round_neg_return_type(self):
        """
        Check that the return type is an integer for negative numbers.
        """
        self.assertIsInstance(_round(-12.32), int)
        self.assertIsInstance(_round(-1.0), int)
        self.assertIsInstance(_round(-1), int)
        self.assertIsInstance(_round(-0), int)

    def test_floor_pos_half_int(self):
        """
        Check that positive half-integers are floored.
        """
        self.assertEqual(_floor(0.5), 0)
        self.assertEqual(_floor(1.5), 1)
        self.assertEqual(_floor(2.5), 2)
        self.assertEqual(_floor(3.5), 3)
        self.assertEqual(_floor(120.5), 120)
        self.assertEqual(_floor(121.5), 121)
        self.assertEqual(_floor(122.5), 122)

    def test_floor_pos_int(self):
        """
        Check that positive integers are returned as is.
        """
        self.assertEqual(_floor(0), 0)
        self.assertEqual(_floor(1), 1)
        self.assertEqual(_floor(2), 2)
        self.assertEqual(_floor(3), 3)
        self.assertEqual(_floor(120), 120)
        self.assertEqual(_floor(121), 121)
        self.assertEqual(_floor(122), 122)

    def test_floor_pos_upper(self):
        """
        Check that floats with the first decimal digit in the upper half
        (0.5-0.9) are floored.
        """
        self.assertEqual(_floor(0.501), 0)
        self.assertEqual(_floor(1.6), 1)
        self.assertEqual(_floor(2.92), 2)
        self.assertEqual(_floor(3.82), 3)
        self.assertEqual(_floor(120.6), 120)
        self.assertEqual(_floor(121.9), 121)
        self.assertEqual(_floor(122.902), 122)

    def test_floor_pos_lower(self):
        """
        Check that floats with the first decimal digit in the lower half
        (0.1-0.4) are floored.
        """
        self.assertEqual(_floor(0.49), 0)
        self.assertEqual(_floor(1.3), 1)
        self.assertEqual(_floor(2.1), 2)
        self.assertEqual(_floor(3.01), 3)
        self.assertEqual(_floor(120.39), 120)
        self.assertEqual(_floor(121.109), 121)
        self.assertEqual(_floor(122.401), 122)

    def test_floor_pos_position(self):
        """
        Check that the second argument controls the 'rounding' position.
        """
        self.assertEqual(_floor(57721.5664901532,  7),  57721.5664901)
        self.assertEqual(_floor(57721.5664901532,  6),  57721.566490)
        self.assertEqual(_floor(57721.5664901532,  5),  57721.56649)
        self.assertEqual(_floor(57721.5664901532,  4),  57721.5664) 
        self.assertEqual(_floor(57721.5664901532,  3),  57721.566)
        self.assertEqual(_floor(57721.5664901532,  2),  57721.56)
        self.assertEqual(_floor(57721.5664901532,  1),  57721.5)
        self.assertEqual(_floor(57721.5664901532,  0),  57721)
        self.assertEqual(_floor(57721.5664901532, -1),  57720)
        self.assertEqual(_floor(57721.5664901532, -2),  57700)
        self.assertEqual(_floor(57721.5664901532, -3),  57000)
        self.assertEqual(_floor(57721.5664901532, -4),  50000)
        self.assertEqual(_floor(57721.5664901532, -5),      0)
        self.assertEqual(_floor(57721.5664901532, -6),      0)

        self.assertEqual(_floor(0, -6),      0)
        self.assertEqual(_floor(0,  6),      0)

    def test_floor_pos_return_type(self):
        """
        Check that the return type is an integer for positive numbers.
        """
        self.assertIsInstance(_floor(12.32), int)
        self.assertIsInstance(_floor(1.0), int)
        self.assertIsInstance(_floor(1), int)
        self.assertIsInstance(_floor(0), int)

    def test_floor_neg_half_int(self):
        """
        Check that negative half-integers are floored.
        """
        self.assertEqual(_floor(-0.5), -1)
        self.assertEqual(_floor(-1.5), -2)
        self.assertEqual(_floor(-2.5), -3)
        self.assertEqual(_floor(-3.5), -4)
        self.assertEqual(_floor(-120.5), -121)
        self.assertEqual(_floor(-121.5), -122)
        self.assertEqual(_floor(-122.5), -123)

    def test_floor_neg_int(self):
        """
        Check that negative integers are returned as is.
        """
        self.assertEqual(_floor(-0), -0)
        self.assertEqual(_floor(-1), -1)
        self.assertEqual(_floor(-2), -2)
        self.assertEqual(_floor(-3), -3)
        self.assertEqual(_floor(-120), -120)
        self.assertEqual(_floor(-121), -121)
        self.assertEqual(_floor(-122), -122)

    def test_floor_neg_upper(self):
        """
        Check that floats with the first decimal digit in the upper half
        (0.5-0.9) are floored.
        """
        self.assertEqual(_floor(-0.501), -1)
        self.assertEqual(_floor(-1.6), -2)
        self.assertEqual(_floor(-2.92), -3)
        self.assertEqual(_floor(-3.82), -4)
        self.assertEqual(_floor(-120.6), -121)
        self.assertEqual(_floor(-121.9), -122)
        self.assertEqual(_floor(-122.902), -123)

    def test_floor_neg_lower(self):
        """
        Check that floats with the first decimal digit in the lower half
        (0.1-0.4) are floored.
        """
        self.assertEqual(_floor(-0.49), -1)
        self.assertEqual(_floor(-1.3), -2)
        self.assertEqual(_floor(-2.1), -3)
        self.assertEqual(_floor(-3.01), -4)
        self.assertEqual(_floor(-120.39), -121)
        self.assertEqual(_floor(-121.109), -122)
        self.assertEqual(_floor(-122.401), -123)

    def test_floor_neg_position(self):
        """
        Check that the second argument controls the 'rounding' position.
        """
        self.assertEqual(_floor(-57721.5664901532,  7),   -57721.5664902)
        self.assertEqual(_floor(-57721.5664901532,  6),   -57721.566491)
        self.assertEqual(_floor(-57721.5664901532,  5),   -57721.56650)
        self.assertEqual(_floor(-57721.5664901532,  4),   -57721.5665) 
        self.assertEqual(_floor(-57721.5664901532,  3),   -57721.567)
        self.assertEqual(_floor(-57721.5664901532,  2),   -57721.57)
        self.assertEqual(_floor(-57721.5664901532,  1),   -57721.6)
        self.assertEqual(_floor(-57721.5664901532,  0),   -57722)
        self.assertEqual(_floor(-57721.5664901532, -1),   -57730)
        self.assertEqual(_floor(-57721.5664901532, -2),   -57800)
        self.assertEqual(_floor(-57721.5664901532, -3),   -58000)
        self.assertEqual(_floor(-57721.5664901532, -4),   -60000)
        self.assertEqual(_floor(-57721.5664901532, -5),  -100000)
        self.assertEqual(_floor(-57721.5664901532, -6), -1000000)

        self.assertEqual(_floor(0, -6),      0)
        self.assertEqual(_floor(0,  6),      0)

    def test_floor_neg_return_type(self):
        """
        Check that the return type is an integer for negative numbers.
        """
        self.assertIsInstance(_floor(-12.32), int)
        self.assertIsInstance(_floor(-1.0), int)
        self.assertIsInstance(_floor(-1), int)
        self.assertIsInstance(_floor(-0), int)
