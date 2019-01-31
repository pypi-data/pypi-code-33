import os
import unittest

import numpy as np

from chi1chi2.core.property import Vector, Polar, Hyper, POLAR, HYPER
from chi1chi2.core.property_reader import PropsMol, PropsWMol, equalize_properties


def for_test(file):
    return os.path.join(os.path.dirname(__file__), file)


TEST_PROP = for_test("prop.dat")
TEST_PROP2 = for_test("prop2.dat")
TEST_PROP_MISSING = for_test("prop3.dat")
DIPOLE = Vector.from_line("0 0 0")
STATIC_POL = Polar.from_lines(["100.719 35.1972 -2.81024",
                               "35.1972 109.533 -41.456",
                               "-2.81024 -41.456 86.4489"])
POL_532 = Polar.from_lines(["112.594 48.1015 -9.25702",
                            "48.1015 132.278 -55.0355",
                            "-9.25702 -55.0355 97.2515"])
HYPER_1064 = Hyper.from_lines(["-210.393 -565.671 361.102",
                               "-565.671 -943.271 628.069",
                               "361.102 628.069 -335.19",
                               "-553.532 -987.824 666.657",
                               "-987.824 -1350.38 870.67",
                               "666.657 870.67 -446.406",
                               "352.848 664.706 -378.63",
                               "664.706 887.183 -476.913",
                               "-378.63 -476.913 186.774"])
ZERO_POLARIZABILITY = np.zeros(9).reshape((3, 3))
ZERO_HYPERPOLARIZABILITY = np.zeros(27).reshape((3, 3, 3))


class TestPropertyReader(unittest.TestCase):
    def test_should_read_properties(self):
        properties = PropsMol.from_file(TEST_PROP)

        self.assertListEqual(properties.wave_lengths, ["static", "1907.0", "1542.0", "1318.0", "1064.0"])
        self.assertEqual(properties.get_or_static("static").polar_w, STATIC_POL)
        self.assertEqual(properties.get_or_static("static").polar_2w, STATIC_POL)
        self.assertEqual(properties.get_or_static("1064.0").polar_2w, POL_532)
        self.assertEqual(properties.get_or_static("1064.0").hyper_w, HYPER_1064)

    def test_zero_properties(self):
        propw = PropsWMol.zero("1907.0", POLAR, HYPER)

        self.assertEqual(propw.polar_w, Polar(ZERO_POLARIZABILITY))
        self.assertEqual(propw.polar_2w, Polar(ZERO_POLARIZABILITY))
        self.assertEqual(propw.hyper_w, Hyper(ZERO_HYPERPOLARIZABILITY))

    def test_property_equalizer_case_equalized(self):
        properties = [PropsMol.from_file(TEST_PROP), PropsMol.from_file(TEST_PROP2)]

        wave_lengths, equalized_properies = equalize_properties(properties)

        self.assertListEqual(properties[0].wave_lengths, wave_lengths)
        _check_property_equality(self, properties, equalized_properies)

    def test_property_equalizer_case_not_equalized(self):
        props_missing = PropsMol.from_file(TEST_PROP_MISSING)
        properties = [PropsMol.from_file(TEST_PROP), props_missing]
        expected_properties = [properties[0],
                               PropsMol(Vector(np.zeros(3)), [
                                   props_missing.get_or_static("static"),
                                   PropsWMol.zero("1907.0", POLAR, HYPER),
                                   PropsWMol.zero("1542.0", POLAR, HYPER),
                                   PropsWMol.zero("1318.0", POLAR, HYPER),
                                   PropsWMol.zero("1064.0", POLAR, HYPER),
                               ])]

        wave_lengths, equalized_properties = equalize_properties(properties)

        self.assertListEqual(properties[0].wave_lengths, wave_lengths)
        _check_property_equality(self, expected_properties, equalized_properties)

    def test_property_equalizer_caes_not_equalized_static(self):
        props_missing = PropsMol.from_file(TEST_PROP_MISSING)
        properties = [PropsMol.from_file(TEST_PROP), props_missing]
        expected_properties = [properties[0],
                               PropsMol(Vector(np.zeros(3)), [
                                   props_missing.get_or_static("static"),
                                   props_missing.get_or_static("static"),
                                   props_missing.get_or_static("static"),
                                   props_missing.get_or_static("static"),
                                   props_missing.get_or_static("static"),
                               ])]

        wave_lengths, equalized_properties = equalize_properties(properties, use_static=True)

        self.assertListEqual(properties[0].wave_lengths, wave_lengths)
        _check_property_equality(self, expected_properties, equalized_properties)


def _check_property_equality(self, expected_properties, actual_properties):
    self.assertEqual(len(expected_properties), len(actual_properties))
    for i in range(len(expected_properties)):
        exptd = expected_properties[i]
        actual = actual_properties[i]
        self.assertEqual(exptd.wave_lengths, actual.wave_lengths)
        for wvl in exptd.wave_lengths:
            self.assertEqual(exptd.get_or_static(wvl).polar_w, actual.get_or_static(wvl).polar_w)
            self.assertEqual(exptd.get_or_static(wvl).polar_2w, actual.get_or_static(wvl).polar_2w)
            self.assertEqual(exptd.get_or_static(wvl).hyper_w, actual.get_or_static(wvl).hyper_w)
