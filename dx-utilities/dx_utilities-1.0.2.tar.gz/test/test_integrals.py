import unittest

from math import pi

from dx_utilities.geometry import PlanarShape
from dx_utilities.integrals import line_moment


class TestIntegrals(unittest.TestCase):

    def test_line_moment_rectangle_path(self):
        basic_shape = PlanarShape.create_rectangle_by_dimensions(bx=1., by=2.)

        d = 1.
        derived_shape = basic_shape.offset_convex_hull(distance=2*d)
        path = derived_shape.boundary

        bx = basic_shape.bx
        by = basic_shape.by
        n = 100

        ref_vector = (4., 0.)
        expected = by**2/2. + 2*pi*d*by + 16*d**2 + bx*by + 4*bx*d
        numerical = line_moment(path, ref_vector, n=n)

        self.assertAlmostEqual(expected, numerical, delta=0.001*expected)

        ref_vector = (0., 4.)
        by = basic_shape.bx
        bx = basic_shape.by
        expected = by**2/2. + 2*pi*d*by + 16*d**2 + bx*by + 4*bx*d
        numerical = line_moment(path, ref_vector, n=n)
        self.assertAlmostEqual(expected, numerical, delta=0.001*expected)

    def test_line_moment_circle_path(self):
        basic_shape = PlanarShape.create_circle(r=1.)

        d = 1.
        derived_shape = basic_shape.offset_convex_hull(distance=d)
        path = derived_shape.boundary
        n = None

        ref_vector = (4., 0.)
        expected = 4*(basic_shape.bx/2 + d)**2
        numerical = line_moment(path, ref_vector, n=n)

        self.assertAlmostEqual(expected, numerical, delta=0.001*expected)

        ref_vector = (64., 4.)
        numerical = line_moment(path, ref_vector, n=n)

        self.assertAlmostEqual(expected, numerical, delta=0.001*expected)
