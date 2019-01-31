import unittest
from enum import Enum

import numpy as np

from chi1chi2.core.property import Vector, Polar, Hyper
from chi1chi2.utils.constants import ChiException

NUMBER_OF_SUBMOLECULES = 5


class Transformation(Enum):
    IDENTITY = ("identity", np.identity(3))
    INVERSION = ("inversion", - np.identity(3))
    SGM_X = ("symmetry plane perpendicular to x", np.array([-1, 0, 0,
                                                            0, 1, 0,
                                                            0, 0, 1]).reshape((3, 3)))
    SGM_Z = ("symmetry plane perpendicular to z", np.array([1, 0, 0,
                                                            0, 1, 0,
                                                            0, 0, -1]).reshape((3, 3)))
    TWO_X = ("two-fold rotation parallel to x", np.array([1, 0, 0,
                                                          0, -1, 0,
                                                          0, 0, -1]).reshape((3, 3)))
    TWO_Z = ("two-fold rotation parallel to z", np.array([-1, 0, 0,
                                                          0, -1, 0,
                                                          0, 0, 1]).reshape((3, 3)))
    FOUR_X = ("four-fold rotation parallel to x", np.array([1, 0, 0,
                                                            0, 0, -1,
                                                            0, 1, 0]).reshape((3, 3)))
    FOUR_Z = ("four-fold rotation parallel to z", np.array([0, -1, 0,
                                                            1, 0, 0,
                                                            0, 0, 1]).reshape((3, 3)))

    def __init__(self, operation_name: str, operation: np.ndarray):
        self.operation_name = operation_name
        self.operation = operation


class TestVector(unittest.TestCase):
    def test_transformation(self):
        for transf in list(Transformation):
            with self.subTest(msg=transf.operation_name + " for vector"):
                vector = Vector(TEST_VECTOR)
                transformed = vector.transform(transf.operation)

                self.assertEqual(expected_vectors.get(transf), transformed)

    def test_from_line(self):
        line = "1 2 3"

        vector = Vector.from_line(line)

        self.assertEqual(Vector(TEST_VECTOR), vector)


class TestPolar(unittest.TestCase):
    def test_transformation(self):
        for transf in list(Transformation):
            with self.subTest(msg=transf.operation_name + " for polarizability"):
                polar = Polar(TEST_POLAR)
                transformed = polar.transform(transf.operation)

                self.assertEqual(expected_polar.get(transf), transformed)

    def test_transform_distributed(self):
        for transf in list(Transformation):
            with self.subTest(msg=transf.operation_name + " for distributed polarizability"):
                dist_polar = Polar(TEST_POLAR).to_distributed(NUMBER_OF_SUBMOLECULES)
                transformed = dist_polar.transform(transf.operation)

                self.assertEqual(Polar(expected_polar.get(transf).tensor / NUMBER_OF_SUBMOLECULES),
                                 transformed.polar_list[0])
                self.assertEqual(expected_polar.get(transf), transformed.to_molecular_polar())

    def test_from_lines(self):
        lines = [
            "1 2 3",
            "4 5 6",
            "7 8 9",
        ]

        polarizability = Polar.from_lines(lines)

        self.assertEqual(Polar(TEST_POLAR), polarizability)

    def test_should_throw_exception_when_wrong_number_of_lines(self):
        lines = [
            "1 2 3",
            "4 5 6",
        ]

        with self.assertRaises(ChiException):
            Polar.from_lines(lines)


class TestHyper(unittest.TestCase):
    def test_transformation(self):
        for transf in list(Transformation):
            with self.subTest(msg=transf.operation_name + " for hyperpolarizability"):
                hyperpolarizability = Hyper(TEST_HYPER)
                transformed = hyperpolarizability.transform(transf.operation)

                self.assertEqual(expected_hyper.get(transf), transformed)

    def test_transform_distributed(self):
        for transf in list(Transformation):
            with self.subTest(msg=transf.operation_name + " for distributed hyperpolarizability"):
                dist_hyper = Hyper(TEST_HYPER).to_distributed(NUMBER_OF_SUBMOLECULES)
                transformed = dist_hyper.transform(transf.operation)

                self.assertEqual(Hyper(expected_hyper.get(transf).tensor / NUMBER_OF_SUBMOLECULES),
                                 transformed.hyper_list[0])
                self.assertEqual(expected_hyper.get(transf), transformed.to_molecular_hyper())

    def test_from_lines(self):
        lines = [
            "1 2 3",
            "4 5 6",
            "7 8 9",
            "10 11 12",
            "13 14 15",
            "16 17 18",
            "19 20 21",
            "22 23 24",
            "25 26 27",
        ]

        hyper = Hyper.from_lines(lines)

        self.assertEqual(Hyper(TEST_HYPER), hyper)

    def test_should_throw_exception_when_wrong_number_of_lines(self):
        lines = [
            "1 2 3",
            "4 5 6",
            "7 8 9",
            "10 11 12",
            "13 14 15",
            "16 17 18",
            "19 20 21",
            "22 23 24",
            "25 26 27",
            "28 29 30",
        ]

        with self.assertRaises(ChiException):
            Hyper.from_lines(lines)


TEST_VECTOR = np.array([1, 2, 3])
expected_vectors = {
    Transformation.IDENTITY: Vector(TEST_VECTOR),
    Transformation.INVERSION: Vector(-TEST_VECTOR),
    Transformation.SGM_X: Vector(np.array([-1, 2, 3])),
    Transformation.SGM_Z: Vector(np.array([1, 2, -3])),
    Transformation.TWO_X: Vector(np.array([1, -2, -3])),
    Transformation.TWO_Z: Vector(np.array([-1, -2, 3])),
    Transformation.FOUR_X: Vector(np.array([1, 3, -2])),
    Transformation.FOUR_Z: Vector(np.array([2, -1, 3])),
}

TEST_POLAR = np.array(range(1, 10)).reshape((3, 3))
expected_polar = {
    Transformation.IDENTITY: Polar(TEST_POLAR),
    Transformation.INVERSION: Polar(TEST_POLAR),
    Transformation.SGM_X: Polar(np.array([1, -2, -3,
                                          -4, 5, 6,
                                          -7, 8, 9]).reshape((3, 3))),
    Transformation.SGM_Z: Polar(np.array([1, 2, -3,
                                          4, 5, -6,
                                          -7, -8, 9]).reshape((3, 3))),
    Transformation.TWO_X: Polar(np.array([1, -2, -3,
                                          -4, 5, 6,
                                          -7, 8, 9]).reshape((3, 3))),
    Transformation.TWO_Z: Polar(np.array([1, 2, -3,
                                          4, 5, -6,
                                          -7, -8, 9]).reshape((3, 3))),
    Transformation.FOUR_X: Polar(np.array([1, 3, -2,
                                           7, 9, -8,
                                           -4, -6, 5]).reshape((3, 3))),
    Transformation.FOUR_Z: Polar(np.array([5, -4, 6,
                                           -2, 1, -3,
                                           8, -7, 9]).reshape((3, 3))),
}

TEST_HYPER = np.array(range(1, 28)).reshape((3, 3, 3))
expected_hyper = {
    Transformation.IDENTITY: Hyper(TEST_HYPER),
    Transformation.INVERSION: Hyper(-TEST_HYPER),
    Transformation.SGM_X: Hyper(np.array([-1, 2, 3,
                                          4, -5, -6,
                                          7, -8, -9,
                                          10, -11, -12,
                                          -13, 14, 15,
                                          -16, 17, 18,
                                          19, -20, -21,
                                          -22, 23, 24,
                                          -25, 26, 27]).reshape((3, 3, 3))),
    Transformation.SGM_Z: Hyper(np.array([1, 2, -3,
                                          4, 5, -6,
                                          -7, -8, 9,
                                          10, 11, -12,
                                          13, 14, -15,
                                          -16, -17, 18,
                                          -19, -20, 21,
                                          -22, -23, 24,
                                          25, 26, -27]).reshape((3, 3, 3))),
    Transformation.TWO_X: Hyper(np.array([1, -2, -3,
                                          -4, 5, 6,
                                          -7, 8, 9,
                                          -10, 11, 12,
                                          13, -14, -15,
                                          16, -17, -18,
                                          -19, 20, 21,
                                          22, -23, -24,
                                          25, -26, -27]).reshape((3, 3, 3))),
    Transformation.TWO_Z: Hyper(np.array([-1, -2, 3,
                                          -4, -5, 6,
                                          7, 8, -9,
                                          -10, -11, 12,
                                          -13, -14, 15,
                                          16, 17, -18,
                                          19, 20, -21,
                                          22, 23, -24,
                                          -25, -26, 27]).reshape((3, 3, 3))),
    Transformation.FOUR_X: Hyper(np.array([1, 3, -2,
                                           7, 9, -8,
                                           -4, -6, 5,
                                           19, 21, -20,
                                           25, 27, -26,
                                           -22, -24, 23,
                                           -10, -12, 11,
                                           -16, -18, 17,
                                           13, 15, -14]).reshape((3, 3, 3))),
    Transformation.FOUR_Z: Hyper(np.array([14, -13, 15,
                                           -11, 10, -12,
                                           17, -16, 18,
                                           -5, 4, -6,
                                           2, -1, 3,
                                           -8, 7, -9,
                                           23, -22, 24,
                                           -20, 19, -21,
                                           26, -25, 27]).reshape((3, 3, 3))),

}
