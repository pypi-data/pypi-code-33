# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for stokes module"""
import sys

from numpy import matrix, sqrt

from py_pol import degrees, np
from py_pol.jones_matrix import Jones_matrix
from py_pol.mueller import Mueller, Stokes

eps = 1e-6
"""
PendingDeprecationWarning: the matrix subclass is not the recommended way to
represent matrices or deal with linear algebra
(see https://docs.scipy.org/doc/numpy/user/numpy-for-matlab-users.html).
Please adjust your code to use regular ndarray.
"""


class TestMueller(object):
    def test_mul(self):
        """ Test for matrix multiplication."""
        solution = np.matrix(
            np.array([[96, 68, 69, 69], [24, 56, 18, 52], [58, 95, 71, 92],
                      [90, 107, 81, 142]]))

        M1 = np.matrix(
            np.array([[5, 2, 6, 1], [0, 6, 2, 0], [3, 8, 1, 4], [1, 8, 5, 6]]))
        M2 = np.matrix(
            np.array([[7, 5, 8, 0], [1, 8, 2, 6], [9, 4, 3, 8], [5, 3, 7, 9]]))
        Mueller1 = Mueller()
        Mueller1.from_matrix(M1)
        Mueller2 = Mueller()
        Mueller2.from_matrix(M2)
        Mueller3 = Mueller1 * Mueller2
        proposal = Mueller3.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Multiplication of random matrices"

        solution = np.matrix(
            np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]))
        M1 = Mueller('M1')
        M1.diattenuator_linear(p1=1, p2=0, angle=0 * degrees)
        M2 = Mueller('M2')
        M2.diattenuator_linear(p1=1, p2=0, angle=90 * degrees)
        M3 = M1 * M2
        proposal = M3.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Multiplication of cross polarizers"

        solution = np.matrix(np.array([[0], [0], [0], [0]]))
        M1 = Mueller('M1')
        M1.diattenuator_linear(p1=1, p2=0, angle=0 * degrees)
        S1 = Stokes('S1')
        S1.general_azimuth_ellipticity(az=90 * degrees, el=0, intensity=1)
        S2 = M1 * S1
        proposal = S2.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Matrix by stokes vector"

    def test_divide_in_blocks(self):
        """Test for the method divide_in_blocks"""
        solution1 = np.matrix(np.array([2, 3, 4]))
        solution2 = np.matrix(np.array([[5], [9], [13]]))
        solution3 = np.matrix(
            np.array([[6, 7, 8], [10, 11, 12], [14, 15, 16]]))
        solution4 = 1
        M = np.matrix(
            np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12],
                      [13, 14, 15, 16]]))
        M1 = Mueller('M1')
        M1.from_elements(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)
        (proposal1, proposal2, proposal3, proposal4) = M1.divide_in_blocks()
        assert np.linalg.norm(proposal1 - solution1) < eps, sys._getframe(
        ).f_code.co_name + "@ Block D"
        assert np.linalg.norm(proposal2 - solution2) < eps, sys._getframe(
        ).f_code.co_name + "@ Block D"
        assert np.linalg.norm(proposal3 - solution3) < eps, sys._getframe(
        ).f_code.co_name + "@ Block D"
        assert np.linalg.norm(proposal4 - solution4) < eps, sys._getframe(
        ).f_code.co_name + "@ Block D"

    def test_rotate(self):
        """Test for the method rotate"""
        solution = np.matrix(
            np.array([[0.5, 0.5, 0, 0], [0.5, 0.5, 0, 0], [0, 0, 0, 0],
                      [0, 0, 0, 0]]))
        M = solution
        M1 = Mueller('M1')
        M1.from_matrix(M)
        M1.rotate(0)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Rotation 0 deg"

        solution = np.matrix(
            np.array([[0.5, 0, 0.5, 0], [0, 0, 0, 0], [0.5, 0, 0.5, 0],
                      [0, 0, 0, 0]]))
        M1 = Mueller('M1')
        M1.from_matrix(M)
        M1.rotate(45 * degrees)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Rotation 45 deg"

        r3 = sqrt(3)
        solution = np.matrix(
            np.array([[0.5, -0.25, r3 / 4, 0], [-0.25, 0.125, -r3 / 8, 0],
                      [r3 / 4, -r3 / 8, 0.375, 0], [0, 0, 0, 0]]))
        M1 = Mueller('M1')
        M1.from_matrix(M)
        M1.rotate(60 * degrees)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Rotation 60 deg"

        solution = np.matrix(
            np.array([[0.5, -0.5, 0, 0], [-0.5, 0.5, 0, 0], [0, 0, 0, 0],
                      [0, 0, 0, 0]]))
        M1 = Mueller('M1')
        M1.from_matrix(M)
        M1.rotate(90 * degrees)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Rotation 90 deg"

    def test_from_elements(self):
        """Test for the method from_elements"""
        solution = np.matrix(
            np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12],
                      [13, 14, 15, 16]]))
        M1 = Mueller('M1')
        M1.from_elements(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Ordered 1 to 16"

    def test_from_matrix(self):
        """Test for the method from_elements"""
        solution = np.matrix(
            np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12],
                      [13, 14, 15, 16]]))
        M1 = Mueller('M1')
        M1.from_matrix(solution)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Ordered 1 to 16"

    def test_from_Jones(self):
        """Test for the method from_Jones"""
        solution = np.matrix(
            np.array([[0.5, 0.5, 0, 0], [0.5, 0.5, 0, 0], [0, 0, 0, 0],
                      [0, 0, 0, 0]]))
        JM = np.matrix(np.array([[1, 0], [0, 0]]))
        J1 = Jones_matrix('J')
        J1.from_matrix(JM)
        M1 = Mueller('M1')
        M1.from_Jones(J1)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Linear polarizer at 0 deg"

    def test_from_blocks(self):
        """Test for the method from_blocks"""
        solution = np.matrix(
            np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12],
                      [13, 14, 15, 16]]))
        D = np.matrix(np.array([2, 3, 4]))
        P = np.matrix(np.array([[5], [9], [13]]))
        m = np.matrix(np.array([[6, 7, 8], [10, 11, 12], [14, 15, 16]]))
        m00 = 1
        M1 = Mueller('M1')
        M1.from_blocks(D, P, m, m00)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Ordered 1 to 16"

    def test_diattenuator_linear(self):
        """Test for the method diattenuator_linear"""
        solution = np.matrix(
            np.array([[0.5, 0.5, 0, 0], [0.5, 0.5, 0, 0], [0, 0, 0, 0],
                      [0, 0, 0, 0]]))
        M1 = Mueller('M1')
        M1.diattenuator_linear(p1=1, p2=0, angle=0 * degrees)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Ideal polarizer 0 deg"

    def test_diattenuator_linear_depolarizer(self):
        """Test for the method diattenuator_linear_depolarizer"""
        M1 = Mueller('M1')
        try:
            M1.diattenuator_linear_depolarizer(
                p1=1, p2=0, d=0.5, angle=0 * degrees, verbose=True)
            assert False, sys._getframe(
            ).f_code.co_name + "@ Depolarizer polarizer impossible"
        except:
            assert True

    def test_diattenuator_carac_angles_from_Jones(self):
        """Test for the method diattenuator_carac_angles_from_Jones"""
        solution = np.matrix(
            np.array([[0.5, 0.5, 0, 0], [0.5, 0.5, 0, 0], [0, 0, 0, 0],
                      [0, 0, 0, 0]]))
        M1 = Mueller('M1')
        M1.diattenuator_carac_angles_from_Jones(p1=1, p2=0, alpha=0, delay=0)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Linear polarizer 0 deg"

        solution = np.matrix(
            np.array([[0.5, 0, -0.5, 0], [0, 0, 0, 0], [-0.5, 0, 0.5, 0],
                      [0, 0, 0, 0]]))
        M1 = Mueller('M1')
        M1.diattenuator_carac_angles_from_Jones(
            p1=1, p2=0, alpha=45 * degrees, delay=180 * degrees)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Linear polarizer 135 deg"

        solution = np.matrix(
            np.array([[0.5, 0, 0, 0.5], [0, 0, 0, 0], [0, 0, 0, 0],
                      [0.5, 0, 0, 0.5]]))
        M1 = Mueller('M1')
        M1.diattenuator_carac_angles_from_Jones(
            p1=1, p2=0, alpha=45 * degrees, delay=90 * degrees)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Circular polarizer 0 deg"

    def test_diattenuator_azimuth_ellipticity_from_Jones(self):
        """Test for the method diattenuator_azimuth_ellipticity_from_Jones"""
        solution = np.matrix(
            np.array([[0.5, 0.5, 0, 0], [0.5, 0.5, 0, 0], [0, 0, 0, 0],
                      [0, 0, 0, 0]]))
        M1 = Mueller('M1')
        M1.diattenuator_azimuth_ellipticity_from_Jones(p1=1, p2=0, az=0, el=0)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Linear polarizer 0 deg"

        solution = np.matrix(
            np.array([[0.5, 0, -0.5, 0], [0, 0, 0, 0], [-0.5, 0, 0.5, 0],
                      [0, 0, 0, 0]]))
        M1 = Mueller('M1')
        M1.diattenuator_azimuth_ellipticity_from_Jones(
            p1=1, p2=0, az=135 * degrees, el=0)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Linear polarizer 135 deg"

        solution = np.matrix(
            np.array([[0.5, 0, 0, 0.5], [0, 0, 0, 0], [0, 0, 0, 0],
                      [0.5, 0, 0, 0.5]]))
        M1 = Mueller('M1')
        M1.diattenuator_azimuth_ellipticity_from_Jones(
            p1=1, p2=0, az=45 * degrees, el=45 * degrees)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Circular polarizer 0 deg"

    def test_diattenuator_carac_angles_from_vector(self):
        """Test for the method diattenuator_carac_angles_from_vector"""
        solution = np.matrix(
            np.array([[0.5, 0.5, 0, 0], [0.5, 0.5, 0, 0], [0, 0, 0, 0],
                      [0, 0, 0, 0]]))
        M1 = Mueller('M1')
        M1.diattenuator_carac_angles_from_vector(p1=1, p2=0, alpha=0, delay=0)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Linear polarizer 0 deg"

        solution = np.matrix(
            np.array([[0.5, 0, -0.5, 0], [0, 0, 0, 0], [-0.5, 0, 0.5, 0],
                      [0, 0, 0, 0]]))
        M1 = Mueller('M1')
        M1.diattenuator_carac_angles_from_vector(
            p1=1, p2=0, alpha=45 * degrees, delay=180 * degrees)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Linear polarizer 135 deg"

        solution = np.matrix(
            np.array([[0.5, 0, 0, 0.5], [0, 0, 0, 0], [0, 0, 0, 0],
                      [0.5, 0, 0, 0.5]]))
        M1 = Mueller('M1')
        M1.diattenuator_carac_angles_from_vector(
            p1=1, p2=0, alpha=45 * degrees, delay=90 * degrees)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Circular polarizer 0 deg"

    def test_diattenuator_azimuth_ellipticity_from_vector(self):
        """Test for the method diattenuator_carac_angles_from_vector"""
        solution = np.matrix(
            np.array([[0.5, 0.5, 0, 0], [0.5, 0.5, 0, 0], [0, 0, 0, 0],
                      [0, 0, 0, 0]]))
        M1 = Mueller('M1')
        M1.diattenuator_azimuth_ellipticity_from_vector(p1=1, p2=0, az=0, el=0)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Linear polarizer 0 deg"

        solution = np.matrix(
            np.array([[0.5, 0, -0.5, 0], [0, 0, 0, 0], [-0.5, 0, 0.5, 0],
                      [0, 0, 0, 0]]))
        M1 = Mueller('M1')
        M1.diattenuator_azimuth_ellipticity_from_vector(
            p1=1, p2=0, az=135 * degrees, el=0)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Linear polarizer 135 deg"

        solution = np.matrix(
            np.array([[0.5, 0, 0, 0.5], [0, 0, 0, 0], [0, 0, 0, 0],
                      [0.5, 0, 0, 0.5]]))
        M1 = Mueller('M1')
        M1.diattenuator_azimuth_ellipticity_from_vector(
            p1=1, p2=0, az=45 * degrees, el=45 * degrees)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Circular polarizer 0 deg"

    def test_diattenuator_from_vector(self):
        """Test for the method diattenuator_from_vector"""
        solution = np.matrix(
            np.array([[0.5, 0.5, 0, 0], [0.5, 0.5, 0, 0], [0, 0, 0, 0],
                      [0, 0, 0, 0]]))
        M1 = Mueller('M1')
        D = np.matrix(np.array([1, 0, 0]))
        m00 = 0.5
        M1.diattenuator_from_vector(D, m00)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Linear polarizer 0 deg"

        solution = np.matrix(
            np.array([[0.5, 0, -0.5, 0], [0, 0, 0, 0], [-0.5, 0, 0.5, 0],
                      [0, 0, 0, 0]]))
        M1 = Mueller('M1')
        D = np.matrix(np.array([0, -1, 0]))
        M1.diattenuator_from_vector(D, m00)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Linear polarizer 135 deg"

        solution = np.matrix(
            np.array([[0.5, 0, 0, 0.5], [0, 0, 0, 0], [0, 0, 0, 0],
                      [0.5, 0, 0, 0.5]]))
        M1 = Mueller('M1')
        D = np.matrix(np.array([0, 0, 1]))
        m00 = 0.5
        M1.diattenuator_from_vector(D, m00)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Circular polarizer 0 deg"

    def test_retarder_carac_angles_from_Jones(self):
        """Test for the method retarder_carac_angles_from_Jones"""
        solution = np.matrix(
            np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0,
                                                                  -1]]))
        M1 = Mueller('M1')
        M1.retarder_carac_angles_from_Jones(
            D=180 * degrees, alpha=0, delta=0, m00=1)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Half-waveplate 0 deg"

        r2 = sqrt(2) / 2
        solution = np.matrix(
            np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, r2, r2],
                      [0, 0, -r2, r2]]))
        M1 = Mueller('M1')
        M1.retarder_carac_angles_from_Jones(
            D=45 * degrees, alpha=0, delta=0, m00=1)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Linear retarder, delay = 45 deg, angle = 0 deg"

        r2 = sqrt(2) / 2
        solution = np.matrix(
            np.array([[1, 0, 0, 0], [0, r2, r2, 0], [0, -r2, r2, 0],
                      [0, 0, 0, 1]]))
        M1 = Mueller('M1')
        M1.retarder_carac_angles_from_Jones(
            D=45 * degrees, alpha=45 * degrees, delta=90 * degrees, m00=1)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Circular (right) retarder, delay = 45 deg, angle = 0 deg"

    def test_retarder_azimuth_ellipticity_from_Jones(self):
        """Test for the method retarder_azimuth_ellipticity_from_Jones"""
        solution = np.matrix(
            np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0,
                                                                  -1]]))
        M1 = Mueller('M1')
        M1.retarder_azimuth_ellipticity_from_Jones(
            D=180 * degrees, az=0, el=0, m00=1)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Half-waveplate 0 deg"

        r2 = sqrt(2) / 2
        solution = np.matrix(
            np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, r2, r2],
                      [0, 0, -r2, r2]]))
        M1 = Mueller('M1')
        M1.retarder_azimuth_ellipticity_from_Jones(
            D=45 * degrees, az=0 * degrees, el=0, m00=1)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Linear retarder, delay = 45 deg, angle = 0 deg"

        r2 = sqrt(2) / 2
        solution = np.matrix(
            np.array([[1, 0, 0, 0], [0, r2, r2, 0], [0, -r2, r2, 0],
                      [0, 0, 0, 1]]))
        M1 = Mueller('M1')
        M1.retarder_azimuth_ellipticity_from_Jones(
            D=45 * degrees, az=0, el=45 * degrees, m00=1)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Circular (right) retarder, delay = 45 deg, angle = 0 deg"

    def test_retarder_carac_angles_from_vector(self):
        """Test for the method retarder_carac_angles_from_vector"""
        solution = np.matrix(
            np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0,
                                                                  -1]]))
        M1 = Mueller('M1')
        M1.retarder_carac_angles_from_vector(
            D=180 * degrees, alpha=0, delta=0, m00=1)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Half-waveplate 0 deg"

        r2 = sqrt(2) / 2
        solution = np.matrix(
            np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, r2, r2],
                      [0, 0, -r2, r2]]))
        M1 = Mueller('M1')
        M1.retarder_carac_angles_from_vector(
            D=45 * degrees, alpha=0, delta=0, m00=1)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Linear retarder, delay = 45 deg, angle = 0 deg"

        r2 = sqrt(2) / 2
        solution = 0.8 * np.matrix(
            np.array([[1, 0, 0, 0], [0, r2, r2, 0], [0, -r2, r2, 0],
                      [0, 0, 0, 1]]))
        M1 = Mueller('M1')
        M1.retarder_carac_angles_from_vector(
            D=45 * degrees, alpha=45 * degrees, delta=90 * degrees, m00=0.8)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Circular (right) retarder, trans = 0.8, delay = 45 deg, angle = 0 deg"

    def test_retarder_azimuth_ellipticity_from_vector(self):
        """Test for the method retarder_azimuth_ellipticity_from_vector"""
        solution = np.matrix(
            np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0,
                                                                  -1]]))
        M1 = Mueller('M1')
        M1.retarder_azimuth_ellipticity_from_vector(
            D=180 * degrees, az=0, el=0, m00=1)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Half-waveplate 0 deg"

        r2 = sqrt(2) / 2
        solution = np.matrix(
            np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, r2, r2],
                      [0, 0, -r2, r2]]))
        M1 = Mueller('M1')
        M1.retarder_azimuth_ellipticity_from_vector(
            D=45 * degrees, az=0 * degrees, el=0, m00=1)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Linear retarder, delay = 45 deg, angle = 0 deg"

        r2 = sqrt(2) / 2
        solution = 0.8 * np.matrix(
            np.array([[1, 0, 0, 0], [0, r2, r2, 0], [0, -r2, r2, 0],
                      [0, 0, 0, 1]]))
        M1 = Mueller('M1')
        M1.retarder_azimuth_ellipticity_from_vector(
            D=45 * degrees, az=0, el=45 * degrees, m00=0.8)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Circular (right) retarder, trans = 0.8, delay = 45 deg, angle = 0 deg"

    def test_retarder_azimuth_ellipticity_from_vector(self):
        """Test for the method retarder_azimuth_ellipticity_from_vector"""
        solution = np.matrix(
            np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0,
                                                                  -1]]))
        M1 = Mueller('M1')
        M1.retarder_from_vector(D=180 * degrees, ur=None, m00=1)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Half-waveplate 0 deg"

        r2 = sqrt(2) / 2
        solution = np.matrix(
            np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, r2, r2],
                      [0, 0, -r2, r2]]))
        M1 = Mueller('M1')
        M1.retarder_from_vector(D=45 * degrees, ur=np.array([1, 0, 0]), m00=1)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Linear retarder, delay = 45 deg, angle = 0 deg"

        r2 = sqrt(2) / 2
        solution = 0.8 * np.matrix(
            np.array([[1, 0, 0, 0], [0, r2, r2, 0], [0, -r2, r2, 0],
                      [0, 0, 0, 1]]))
        M1 = Mueller('M1')
        M1.retarder_from_vector(
            D=45 * degrees, ur=np.array([0, 0, 1]), m00=0.8)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Circular (right) retarder, trans = 0.8, delay = 45 deg, angle = 0 deg"

    def test_retarder_from_vector(self):
        """Test for the method retarder_from_vector"""
        solution = np.matrix(
            np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0,
                                                                  -1]]))
        try:
            M1 = Mueller('M1')
            M1.retarder_from_vector(D=180 * degrees, ur=None, m00=1)
            proposal = M1.M
            assert False, sys._getframe(
            ).f_code.co_name + "@ Half-waveplate 0 deg"
        except:
            assert True, sys._getframe(
            ).f_code.co_name + "@ Half-waveplate 0 deg"

        r2 = sqrt(2) / 2
        solution = np.matrix(
            np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, r2, r2],
                      [0, 0, -r2, r2]]))
        M1 = Mueller('M1')
        M1.retarder_from_vector(D=45 * degrees, ur=np.array([1, 0, 0]), m00=1)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Linear retarder, delay = 45 deg, angle = 0 deg"

        r2 = sqrt(2) / 2
        solution = 0.8 * np.matrix(
            np.array([[1, 0, 0, 0], [0, r2, r2, 0], [0, -r2, r2, 0],
                      [0, 0, 0, 1]]))
        M1 = Mueller('M1')
        M1.retarder_from_vector(
            D=45 * degrees, ur=np.array([0, 0, 1]), m00=0.8)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Circular (right) retarder, trans = 0.8, delay = 45 deg, angle = 0 deg"

    def test_diattenuator_retarder_linear(self):
        """Test for the method diattenuator_retarder_linear"""
        r3p2 = sqrt(3) / 2
        solution = 0.5 * np.matrix(
            np.array([[1.25, 0.75, 0, 0], [0.75, 1.25, 0, 0],
                      [0, 0, 0.5, r3p2], [0, 0, -r3p2, 0.5]]))
        M1 = Mueller('M1')
        M1.diattenuator_retarder_linear(
            p1=1, p2=sqrt(0.25), D=60 * degrees, angle=0)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Linear retarder, p1=1, p2**2=0.25, delay=60 deg, angle = 0 deg"

    def test_quarter_wave(self):
        """test for quarter plate using Mueller formalism.
        We have checked 0, 45 and 90 degrees"""

        solution = matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1],
                           [0, 0, -1, 0]])

        M1 = Mueller()
        proposal = M1.quarter_wave(angle=0 * degrees)
        proposal = M1.M
        print(solution)
        print(proposal)
        print(type(solution), type(proposal))
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ 0 grados"

        solution = matrix([[1., 0., 0., 0.], [0., 0., 0., -1.],
                           [0., 0., 1., 0.], [0., 1., -0., 0.]])

        M1 = Mueller()
        proposal = M1.quarter_wave(angle=45 * degrees)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ 45 grados"

        solution = matrix([[1., 0., 0., 0.], [0., 1., -0., -0.],
                           [0., -0., 0., -1.], [0., 0., 1., 0.]])

        M1 = Mueller()
        proposal = M1.quarter_wave(angle=90 * degrees)
        proposal = M1.M
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ 90 grados"

    def test_multiplication_Matrix_vector(self):

        solution = matrix([[1], [1], [0], [0]])

        M1 = Mueller('M1')
        M1.from_elements(1, 1, 0, 0)

        J1 = Stokes('J1')
        J1.from_elements(1, 1j)
        J2 = M1 * J1
        proposal = J2.get()
        assert np.linalg.norm(proposal -
                              solution) < eps, sys._getframe().f_code.c
