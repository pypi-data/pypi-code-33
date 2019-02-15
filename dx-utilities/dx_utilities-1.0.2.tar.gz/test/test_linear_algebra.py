import numpy as np
import unittest

from dx_utilities.linear_algebra import project, reflect


class TestLinearAlgebra(unittest.TestCase):

    def test_project_to_single_vector(self):

        source = np.ones((15, 3))
        target = np.array([3., 0., 0.])

        projections = project(source, target)
        expected = source.copy()
        expected[:, 1:] = 0.

        self.assertTrue((projections == expected).all())

    def test_reflect(self):

        source = np.array([(0., 3.), (1., 1.)])
        normal = (0., 3.)
        reflected = reflect(source, normal)
        self.assertTrue(np.allclose(reflected, [(0., -3), (1., -1)]))
