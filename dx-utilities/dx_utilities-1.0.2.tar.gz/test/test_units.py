from unittest import TestCase

import dx_utilities.physical_constants as CONSTANTS
from dx_utilities.units import *


class TestWeight(TestCase):

    def test_instatiation(self):
        w = Weight(3.)
        self.assertIsInstance(w, Weight)

    def test_to_mass(self):
        w = Weight(3.)
        m = w.to_mass()
        expected = w / CONSTANTS.g
        self.assertAlmostEqual(m, expected)

    def test_from_mass(self):
        m = 20.
        w = Weight.from_mass(m)
        self.assertIsInstance(w, Weight)
        expected = m * CONSTANTS.g
        self.assertAlmostEqual(w, expected)


class TestMass(TestCase):

    def test_instatiation(self):
        m = Mass(3.)
        self.assertIsInstance(m, Mass)

    def test_to_weight(self):
        m = Mass(3.)
        w = m.to_weight()
        expected = 3. * CONSTANTS.g
        self.assertAlmostEqual(w, expected)

    def test_from_weight(self):
        w = 20.
        m = Mass.from_weight(w)
        self.assertIsInstance(m, Mass)
        expected = w / CONSTANTS.g
        self.assertAlmostEqual(m, expected)


class TestTransform(TestCase):

    def setUp(self):
        def numerical():
            return 3
        def non_numerical():
            return 'none'

        self.numerical = numerical
        self.non_numerical = non_numerical

    def test_transform_value_raises(self):
        with self.assertRaises(UnrecognizedUnitPrefix):
            transform_value(3., prefix='whatever')

        with self.assertRaises(ValueError):
            transform_value('none')

    def test_transform_units_raises(self):
        with self.assertRaises(ValueError):
            transform_units()(self.non_numerical)()

    def test_transform_units(self):
        self.assertAlmostEqual(
                transform_units(prefix='k')(self.numerical)(),
                3e+03
                )

    def test_transform_value(self):
        self.assertAlmostEqual(
                transform_value(3., prefix='k'),
                3e+03
                )

    def test_transform_units_inverse(self):
        self.assertAlmostEqual(
                transform_units(prefix='k', inverse=True)(self.numerical)(),
                3e-03
                )

    def test_inverse_transform_value(self):
        self.assertAlmostEqual(
                inverse_transform_value(3., prefix='k'),
                3e-03
                )
