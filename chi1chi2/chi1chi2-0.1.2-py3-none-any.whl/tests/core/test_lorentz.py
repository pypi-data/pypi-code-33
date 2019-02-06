import os
import unittest

import numpy as np

from chi1chi2.core.property import Lorentz
from chi1chi2.utils.constants import ChiException


def file_for_test(file):
    return os.path.join(os.path.dirname(__file__), file)


LORENTZ_OUTPUT = file_for_test("L.dat")
LORENTZ_NOT_CONVERGED = file_for_test("L_not_conv.dat")
ACTUAL_LORENTZ = file_for_test("actual_lorentz.dat")

LORENTZ_SIMPLE = file_for_test("L_simple.dat")


class TestLorentzRead(unittest.TestCase):
    def test_read_simple_from_file(self):
        lorentz_tensor = Lorentz.from_file(LORENTZ_SIMPLE)

        self.assertEqual(Lorentz(1. / 3. * np.identity(3)), lorentz_tensor)

    def test_should_raise_exception_if_not_converged(self):
        with self.assertRaises(ChiException):
            Lorentz.from_file(LORENTZ_NOT_CONVERGED)

    def test_shoud_read_full_lorentz_tensor(self):
        actual_lorentz = _get_actual_lorentz(ACTUAL_LORENTZ)

        lorentz_tensor = Lorentz.from_file(LORENTZ_OUTPUT)

        self.assertEqual(actual_lorentz, lorentz_tensor)


def _get_actual_lorentz(file):
    with open(file) as f:
        lines = f.readlines()
    dim = len(lines)
    tmp_list = []
    for i in range(dim):
        tmp_list.extend(float(u) for u in lines[i].split())
    return Lorentz(np.array(tmp_list).reshape((dim, dim)))
