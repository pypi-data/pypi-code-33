# -*- coding: utf-8 -*-
#   Copyright (c) 2019 D. de Vries
#
#   This file is part of XFoil.
#
#   XFoil is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   XFoil is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with XFoil.  If not, see <https://www.gnu.org/licenses/>.
import numpy as np
import unittest

from .xfoil import XFoil


class TestXFoil(unittest.TestCase):
    """Test whether the XFOIL module functions properly."""

    def assertNumpyArraysAlmostEqual(self, first, second, decimal, msg=''):
        for i in range(first.size):
            self.assertAlmostEqual(first[i], second[i], decimal, msg)

    def test_a(self):
        """Analyse the NACA 0012 at Re = 1e6, M = 0, α = 10 degrees and verify the results."""
        xf = XFoil()
        xf.naca('0012')
        xf.Re = 1e6
        xf.max_iter = 100
        cl, cd, cm = xf.a(10)

        self.assertAlmostEqual(cl, 1.0809, 4)
        self.assertAlmostEqual(cd, 0.0150, 4)
        self.assertAlmostEqual(cm, 0.0053, 4)

    def test_cl(self):
        """Analyse the NACA 0012 at Re = 1e6, M = 0, C_l = 1 and verify the results."""
        xf = XFoil()
        xf.naca('0012')
        xf.Re = 1e6
        a, cd, cm = xf.cl(1)

        self.assertAlmostEqual(a, 9.0617, 4)
        self.assertAlmostEqual(cd, 0.0135, 4)
        self.assertAlmostEqual(cm, 0.0013, 4)

    def test_aseq(self):
        """Analyse the NACA 0012 at Re = 1e6, M = 0, α = 0, 0.5, ..., 20 and verify the results."""
        xf = XFoil()
        xf.naca('0012')
        xf.Re = 1e6
        xf.max_iter = 40
        a, cl, cd, cm = xf.aseq(0, 20.5, 0.5)

        self.assertNumpyArraysAlmostEqual(a, np.arange(0, 20.5, 0.5), 4)
        self.assertNumpyArraysAlmostEqual(cl, np.array([
            0.0000, 0.0537, 0.1074, 0.1609, 0.2142, 0.2672, 0.3200, 0.3723,
            0.4278, 0.4878, 0.5580, 0.6254, 0.6948, 0.7638, 0.8264, 0.8684,
            0.9099, 0.9511, 0.9948, 1.0363, 1.0809, 1.1224, 1.1666, 1.2067,
            1.2454, 1.2834, 1.3161, 1.3272, 1.3501, 1.3672, 1.3808, 1.3900,
            1.3877, 1.3670, 1.3322, 1.3041, 1.2679, 1.2287, 1.1901, 1.1541]), 4)
        self.assertNumpyArraysAlmostEqual(cd, np.array([
            0.0054, 0.0054, 0.0055, 0.0056, 0.0058, 0.0061, 0.0064, 0.0068,
            0.0073, 0.0078, 0.0085, 0.0091, 0.0097, 0.0104, 0.0109, 0.0115,
            0.0121, 0.0128, 0.0134, 0.0143, 0.0150, 0.0161, 0.0169, 0.0181,
            0.0194, 0.0205, 0.0220, 0.0243, 0.0261, 0.0286, 0.0317, 0.0357,
            0.0417, 0.0509, 0.0629, 0.0745, 0.0879, 0.1023, 0.1171, 0.1321]), 4)
        self.assertNumpyArraysAlmostEqual(cm, np.array([
            -0.0000, +0.0007, +0.0014, +0.0022, +0.0030, +0.0039, +0.0048,
            +0.0058, +0.0060, +0.0051, +0.0017, -0.0011, -0.0043, -0.0074,
            -0.0092, -0.0066, -0.0039, -0.0013, +0.0010, +0.0034, +0.0053,
            +0.0074, +0.0091, +0.0111, +0.0133, +0.0155, +0.0182, +0.0236,
            +0.0267, +0.0294, +0.0310, +0.0315, +0.0302, +0.0264, +0.0208,
            +0.0149, +0.0082, +0.0008, -0.0070, -0.0152]), 4)

    def test_cseq(self):
        """Analyse the NACA 0012 at Re = 1e6, M = 0, C_l = -0.5, -0.45, ..., 0.45 and verify the results."""
        xf = XFoil()
        xf.naca('0012')
        xf.Re = 1e6
        xf.max_iter = 40
        a, cl, cd, cm = xf.cseq(-0.5, 0.5, 0.05)

        self.assertNumpyArraysAlmostEqual(cl, np.arange(-0.5, 0.5, 0.05), 4)
        self.assertNumpyArraysAlmostEqual(a, np.array([
            -4.5879, -4.1765, -3.7446, -3.2848, -2.8112, -2.3371, -1.8666, -1.3981, -0.9324, -0.4659,
            -0.0000, +0.4659, +0.9323, +1.3981, +1.8665, +2.3370, +2.8111, +3.2847, +3.7445, +4.1764]), +4)
        self.assertNumpyArraysAlmostEqual(cd, np.array([
            +0.0079, +0.0075, +0.0070, +0.0066, +0.0063, +0.0060, +0.0058, +0.0056, +0.0055, +0.0054,
            +0.0054, +0.0054, +0.0055, +0.0056, +0.0058, +0.0060, +0.0063, +0.0066, +0.0070, +0.0075]), 4)
        self.assertNumpyArraysAlmostEqual(cm, np.array([
            -0.0045, -0.0055, -0.0058, -0.0054, -0.0045, -0.0036, -0.0028, -0.0020, -0.0013, -0.0007,
            -0.0000, +0.0007, +0.0013, +0.0020, +0.0028, +0.0036,  0.0045, +0.0054, +0.0058, +0.0055]), 4)


if __name__ == '__main__':
    unittest.main()
