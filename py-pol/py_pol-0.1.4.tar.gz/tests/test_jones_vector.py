# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for Jones_vector module"""

import sys

import numpy as np
from numpy import matrix

from py_pol import degrees, eps
from py_pol.jones_vector import Jones_vector
from py_pol.stokes import Stokes


"""
PendingDeprecationWarning: the matrix subclass is not the recommended way to
represent matrices or deal with linear algebra
(see https://docs.scipy.org/doc/numpy/user/numpy-for-matlab-users.html).
Please adjust your code to use regular ndarray.
"""


class TestJonesVector(object):
    def test_sum(self):

        solution = matrix([[1.], [1.]])
        M1 = Jones_vector('M1')
        M1.linear_light(angle=0 * degrees)
        J2 = Jones_vector('J2')
        J2.linear_light(angle=90 * degrees)
        J3 = M1 + J2
        proposal = J3.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: +"

    def test_substraction(self):

        solution = matrix([[1.], [-1.]])
        M1 = Jones_vector('M1')
        M1.linear_light(angle=0 * degrees)
        J2 = Jones_vector('J2')
        J2.linear_light(angle=90 * degrees)
        J4 = M1 - J2
        proposal = J4.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: -"

    def test_multiplication(self):

        solution = matrix([[2], [0.]])
        M1 = Jones_vector('M1')
        M1.linear_light(angle=0 * degrees)
        J2 = 2 * M1
        proposal = J2.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: 2*J"

        solution = matrix([[2], [0.]])
        M1 = Jones_vector('M1')
        M1.linear_light(angle=0 * degrees)
        J2 = M1 * 2
        proposal = J2.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: J*2"

        solution = matrix([[3], [2]])
        M1 = Jones_vector('M1')
        M1.linear_light(angle=0 * degrees)
        J2 = Jones_vector('J2')
        J2.linear_light(angle=90 * degrees)
        J3 = 3 * M1 + 2 * J2
        proposal = J3.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: 3 * M1 + 2 * J2"

    def test_rotate(self):

        solution = matrix([[1 / np.sqrt(2)], [1 / np.sqrt(2)]])
        M1 = Jones_vector('M1')
        M1.linear_light(angle=0 * degrees)
        M1.rotate(angle=45 * degrees)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: 45*degrees"

    def test_clear(self):

        solution = matrix([[0.], [0.]])
        M1 = Jones_vector('M1')
        M1.linear_light(angle=0 * degrees)
        M1.clear()
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: clear"

    def test_from_elements(self):

        solution = matrix([[1.], [0.]])
        M1 = Jones_vector()
        M1.from_elements(1, 0)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: (1,0)"

        solution = matrix([[2], [2 + 2j]])
        M1 = Jones_vector()
        M1.from_elements(2, 2 + 2j)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: (2, 2j)"

    def test_from_matrix(self):

        solution = matrix([[1.], [0.]])
        J1 = np.matrix([[1.], [0.]])
        M1 = Jones_vector()
        M1.from_matrix(J1)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: (1,0)"

    def test_from_Stokes(self):

        solution = matrix([[1.], [0.]])
        S = Stokes()
        S.from_elements(1, 1, 0, 0)
        M1 = Jones_vector('J1')
        M1.from_Stokes(S)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: (1, 1, 0, 0)"

        solution = matrix([[0.], [1.]])
        S = Stokes()
        S.from_elements(1, -1, 0, 0)
        M1 = Jones_vector('J1')
        M1.from_Stokes(S)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: (1, -1, 0, 0)"

        solution = matrix([[1 / np.sqrt(2)], [1 / np.sqrt(2)]])
        S = Stokes()
        S.from_elements(1, 0, 1, 0)
        M1 = Jones_vector('J1')
        M1.from_Stokes(S)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: (1, 0, 1, 0)"

        solution = matrix([[1 / np.sqrt(2)], [-1 / np.sqrt(2)]])
        S = Stokes()
        S.from_elements(1, 0, -1, 0)
        M1 = Jones_vector('J1')
        M1.from_Stokes(S)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: (1, 0, -1, 0)"

        solution = matrix([[1.], [1j]])
        S = Stokes()
        S.from_elements(1, 0, 0, 1)
        M1 = Jones_vector('J1')
        M1.from_Stokes(S)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: (1, 0, 0, 1)"

        solution = matrix([[1.], [-1j]])
        S = Stokes()
        S.from_elements(1, 0, 0, -1)
        M1 = Jones_vector('J1')
        M1.from_Stokes(S)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: (1, 0, 0, -1)"

    def test_linear_light(self):

        solution = matrix([[1.], [0.]])
        M1 = Jones_vector()
        M1.linear_light(angle=0 * degrees)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: 0*degrees"

        solution = matrix([[1 / np.sqrt(2)], [1 / np.sqrt(2)]])
        M1 = Jones_vector()
        M1.linear_light(angle=45 * degrees)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: 45*degrees"

        solution = matrix([[0.], [1.]])
        M1 = Jones_vector()
        M1.linear_light(angle=90 * degrees)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: 90*degrees"

    def test_circular_light(self):

        solution = matrix([[1.], [1j]])
        M1 = Jones_vector()
        M1.circular_light(amplitude=np.sqrt(2), kind='r')
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: 'r'"

        solution = matrix([[1.], [-1j]])
        M1 = Jones_vector()
        M1.circular_light(amplitude=np.sqrt(2), kind='l')
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: 'l'"

    def test_elliptical_light(self):

        solution = matrix([[1.], [1.]])
        M1 = Jones_vector()
        M1.elliptical_light(a=1, b=1, phase=0 * degrees, angle=0 * degrees)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: (1,1,0,0)"

        solution = matrix([[1.], [1j]])
        M1 = Jones_vector()
        M1.elliptical_light(a=1, b=1, phase=90 * degrees, angle=0 * degrees)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: (1,1,90*degrees,0)"

        solution = matrix([[1 + 1j], [-1 + 1j]])
        M1 = Jones_vector()
        M1.elliptical_light(
            a=np.sqrt(2), b=np.sqrt(2), phase=90 * degrees, angle=45 * degrees)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: sqrt(2), sqrt(2), 90 * degrees, 45 * degrees"

        solution = matrix([[1.], [-1.]])
        M1 = Jones_vector()
        M1.elliptical_light(
            a=np.sqrt(2), b=0, phase=0 * degrees, angle=45 * degrees)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: sqrt(2),0, 90 * degrees, 45 * degrees"

    def test_general_azimuth_ellipticity(self):

        solution = matrix([[1.], [0.]])
        M1 = Jones_vector()
        M1.general_azimuth_ellipticity(az=0 * degrees, el=0, amplitude=1)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: (0,0,1)"

        solution = matrix([[1 / np.sqrt(2)], [1 / np.sqrt(2)]])
        M1 = Jones_vector()
        M1.general_azimuth_ellipticity(az=45 * degrees, el=0, amplitude=1)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: (45,0,1)"

        solution = matrix([[0.5 - 0.5j], [0.5 + 0.5j]])
        M1 = Jones_vector()
        M1.general_azimuth_ellipticity(
            az=45 * degrees, el=45 * degrees, amplitude=1)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: (45,45,1)"

        solution = matrix([[0], [1j]])
        M1 = Jones_vector()
        M1.general_azimuth_ellipticity(
            az=0 * degrees, el=90 * degrees, amplitude=1)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: (45,45,1)"

    def test_general_carac_angles(self):

        solution = matrix([[1.], [0.]])
        M1 = Jones_vector()
        M1.general_carac_angles(alpha=0, delay=0, amplitude=1)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: (0,0,1)"

        solution = matrix([[1 / np.sqrt(2)], [1 / np.sqrt(2)]])
        M1 = Jones_vector()
        M1.general_carac_angles(alpha=45 * degrees, delay=0, amplitude=1)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: (45,0,1)"

        solution = matrix([[0.5 - 0.5j], [0.5 + 0.5j]])
        M1 = Jones_vector()
        M1.general_carac_angles(
            alpha=45 * degrees, delay=90 * degrees, amplitude=1)
        proposal = M1.get()
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: (45,90,1)"
