import unittest

from dx_utilities.checks import check_positive, check_numerical_value


class TestChecks(unittest.TestCase):

    def test_check_positive(self):
        self.assertIsNone(check_positive(1.0, 2.0))

        with self.assertRaises(ValueError):
            check_positive(0., 1.)

        with self.assertRaises(ValueError):
            check_positive(-1., 1.)

    def test_check_numerical(self):

        with self.assertRaises(ValueError):
            check_numerical_value('none')

        self.assertIsNone(check_numerical_value(3))
        self.assertIsNone(check_numerical_value(3.))
