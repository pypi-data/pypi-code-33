from dx_base.forces import NodalForces, NMyMz
import numpy as np
import unittest


class TestNodalForces(unittest.TestCase):

    def test_array_interface(self):
        nf = NodalForces()
        expected = np.zeros((1, 6))
        np.testing.assert_equal(np.array(nf), expected)

    def test_addition(self):
        nf1 = NodalForces(LC='nf1', Rx=1., Mx=1., My=1.)
        nf2 = NodalForces(LC='nf2', Rx=3., Mx=2., My=9.)
        new_nf = nf1 + nf2
        self.assertAlmostEqual(new_nf.Rx, 4.)
        self.assertAlmostEqual(new_nf.Mx, 3.)
        self.assertAlmostEqual(new_nf.My, 10.)
        self.assertEqual(new_nf.LC, 'nf1')


class TestNMyMz(unittest.TestCase):

    def test_lc(self):
        nf = NMyMz()
        self.assertEqual(nf.LC, 'LC0')

    def test_array_interface(self):
        nf = NMyMz()
        expected = np.zeros((1, 3))
        np.testing.assert_equal(np.array(nf), expected)
