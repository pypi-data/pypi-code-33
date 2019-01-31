import os
import unittest

import numpy as np

from chi1chi2.core.property import Vector, Polar, Hyper
from chi1chi2.core.property_reader import PropsMol
from chi1chi2.helpers.read_g09 import transform_g09_to_input, POLAR_W, POLAR_2W, HYPER_W


def file_for_test(file):
    return os.path.join(os.path.dirname(__file__), file)


EXPECTED_PROPERTY_FILE = file_for_test("test_prop.dat")
G09_OUTPUT = file_for_test("bchf.dat")


class TestG09Reader(unittest.TestCase):
    def test_should_produce_the_same_properties(self):
        props_from_converted_file = PropsMol.from_file(EXPECTED_PROPERTY_FILE)
        dipole, raw_properties = transform_g09_to_input(G09_OUTPUT, charged=True)

        self.assertEqual(props_from_converted_file.dipole_moment, Vector(np.array(dipole)))
        for wvl in ("static", "1907.0", "1542.0", "1318.0", "1064.0"):
            self.assertEqual(props_from_converted_file.get_or_static(wvl).polar_w,
                             Polar(np.array(raw_properties.get(wvl).get(POLAR_W))))
            self.assertEqual(props_from_converted_file.get_or_static(wvl).polar_2w,
                             Polar(np.array(raw_properties.get(wvl).get(POLAR_2W))))
            self.assertEqual(props_from_converted_file.get_or_static(wvl).hyper_w,
                             Hyper(np.array(raw_properties.get(wvl).get(HYPER_W))))
