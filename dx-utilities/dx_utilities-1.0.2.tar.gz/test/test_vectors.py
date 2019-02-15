import unittest
import numpy as np

from mathutils import Vector
from shapely.geometry import LineString

from dx_utilities.vectors import VectorFactory, mean, rotate


class TestVectorFactory(unittest.TestCase):

    def setUp(self):
        self.points = [(0., 0.), (0.0, 0.4), (0.0, 1.)]
        self.linestring = LineString(self.points)

    def test_from_two_points(self):
        with self.assertRaises(ValueError):
            VectorFactory.from_two_points((0., 0), (0., 0., 0))

        with self.assertRaises(ValueError):
            VectorFactory.from_two_points((0.,), (0., 0., 0))

        with self.assertRaises(ValueError):
            VectorFactory.from_two_points((0., 0., 0., 0.), (0., 0., 0))

        v = VectorFactory.from_two_points((0., 0.), (1., 0))
        self.assertIsInstance(v, VectorFactory)
        self.assertEqual(v.magnitude, 1.)

    def test_from_points(self):

        vectors = list(VectorFactory.from_points(self.points))
        for v in vectors:
            self.assertIsInstance(v, Vector)
        self.assertAlmostEqual(vectors[0].magnitude, 0.4, places=4)
        self.assertAlmostEqual(vectors[1].magnitude, 0.6, places=4)

    def test_from_linestring(self):
        vectors = list(VectorFactory.from_linestring(self.linestring))
        for v in vectors:
            self.assertIsInstance(v, Vector)
        self.assertAlmostEqual(vectors[0].magnitude, 0.4, places=4)
        self.assertAlmostEqual(vectors[1].magnitude, 0.6, places=4)

        with self.assertRaises(TypeError):
            VectorFactory.from_linestring(self.points)


class TestFunctions(unittest.TestCase):

    def test_mean(self):

        v = Vector([1., 2., 3.])
        self.assertAlmostEqual(mean(v), 2.)

        v = Vector([1., 2., 0.])
        self.assertAlmostEqual(mean(v), 1.5)

        v = Vector([18., 0., 0.])
        self.assertAlmostEqual(mean(v), 18.)

    def test_rotate(self):
        v = Vector([1., 0., 0.])
        rotate(v, 45., degrees=True, _2D=False)
        self.assertTrue(np.allclose(v, [0.707, 0.707, 0.], rtol=1e-03))
        rotate(v, -45., degrees=True, _2D=True)
        self.assertTrue(np.allclose(v, [1., 0.]))
