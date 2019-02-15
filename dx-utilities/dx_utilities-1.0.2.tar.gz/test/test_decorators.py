import unittest

from dx_utilities.decorators import tolerate_input


class TestInputTolerance(unittest.TestCase):

    @tolerate_input('x')
    def single_arg_float(self, x):
        return x + 3.

    @tolerate_input('x', cast=int)
    def single_arg_int(self, x):
        return x + 3.

    @tolerate_input('x')
    @tolerate_input('y')
    def double_arg_float(self, x, y):
        return x + y

    @tolerate_input('x', cast=int)
    @tolerate_input('y', cast=float)
    def double_arg_mixed(self, x, y):
        return x + y

    def test_single_arg_float(self):
        self.assertAlmostEqual(self.single_arg_float(x="4"), 7)
        with self.assertRaises(TypeError):
            self.assertAlmostEqual(self.single_arg_float("4"), 7)
        with self.assertRaises(ValueError):
            self.assertAlmostEqual(self.single_arg_float(x="asdf"), 7)

    def test_single_arg_int(self):
        self.assertAlmostEqual(self.single_arg_int(x="4"), 7)
        with self.assertRaises(TypeError):
            self.assertAlmostEqual(self.single_arg_int("4"), 7)

    def test_double_arg_float(self):
        self.assertAlmostEqual(self.double_arg_float(x="4", y="3"), 7)
        with self.assertRaises(TypeError):
            self.assertAlmostEqual(self.double_arg_float("4", y="3"), 7)

    def test_double_arg_mixed(self):
        self.assertAlmostEqual(self.double_arg_mixed(x="4", y="3"), 7)
        with self.assertRaises(TypeError):
            self.assertAlmostEqual(self.double_arg_mixed("4", y="3"), 7)
