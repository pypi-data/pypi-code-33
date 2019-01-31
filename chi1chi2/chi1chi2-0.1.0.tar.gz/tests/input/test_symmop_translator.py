from unittest import TestCase

import numpy as np

from chi1chi2.utils.constants import ZERO_TRANSLATION, Symmop

symmop_parameters = [
    ['\'x, y, z\'', np.identity(3), ZERO_TRANSLATION],
    ['-x, y, z', np.array([-1, 0, 0, 0, 1, 0, 0, 0, 1]).reshape((3, 3)), ZERO_TRANSLATION],
    ['x + 1, y, z', np.identity(3), np.array([1, 0, 0]).reshape((3, 1))],
    ['x + 1/2, y - 1, z + 3 / 4', np.identity(3), np.array([.5, -1, .75]).reshape((3, 1))],
    ['-x + 1, - y + 1 / 3, z', np.array([-1, 0, 0, 0, -1, 0, 0, 0, 1]).reshape((3, 3)),
     np.array([1, 1. / 3, 0]).reshape((3, 1))],
    ['-y, x-y, z', np.array([0, -1, 0, 1, -1, 0, 0, 0, 1]).reshape((3, 3)), ZERO_TRANSLATION],
    ['-x + y, -x, z', np.array([-1, 1, 0, -1, 0, 0, 0, 0, 1]).reshape((3, 3)), ZERO_TRANSLATION],
]

symmop_parameters_inverting = [
    ['1/2+x,1/2-y,1/2+z', 'x+1/2, -y+1/2, z+1/2',
     Symmop(np.array([1, 0, 0, 0, -1, 0, 0, 0, 1]).reshape((3, 3)), np.array([0.5, 0.5, 0.5]).reshape((3, 1)))],
    ['1/2 + x, -1 + y, 3 /4 + z', 'x+1/2, y-1, z+3/4',
     Symmop(np.identity(3), np.array([.5, -1, .75]).reshape((3, 1)))],
]


class TestInputPreparator(TestCase):
    def test_symmetry_operation_translator(self):
        for symm_op, exptd_rotation, exptd_translation in symmop_parameters:
            with self.subTest(msg="checking:", symmop=symm_op):
                symmop = Symmop.from_line(symm_op)
                self.assertListEqual(symmop.rotation.tolist(), exptd_rotation.tolist())
                self.assertListEqual(symmop.translation.tolist(), exptd_translation.tolist())

    def test_symmetry_to_line(self):
        for exptd_symmop, rotation, translation in symmop_parameters:
            with self.subTest(msg="checking:", symmop=exptd_symmop):
                symmop = Symmop(rotation, translation)
                self.assertEqual(exptd_symmop.strip('\'').replace(' ', ''), symmop.to_line().replace(' ', ''))

    def test_symmetry_operation_inverting(self):
        for symmop_line, exptd_symmop_line, exptd_symmop in symmop_parameters_inverting:
            with self.subTest(msg="checking:", symmop=symmop_line):
                symmop_from_line = Symmop.from_line(symmop_line)
                symmop_line_from_symmop = symmop_from_line.to_line()
                self.assertEqual(exptd_symmop, symmop_from_line)
                self.assertEqual(exptd_symmop_line, symmop_line_from_symmop)
