# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for Jones_vector module"""

import sys

import numpy as np

from py_pol import degrees, eps
from py_pol.jones_vector import Jones_vector


"""
PendingDeprecationWarning: the matrix subclass is not the recommended way to
represent matrices or deal with linear algebra
(see https://docs.scipy.org/doc/numpy/user/numpy-for-matlab-users.html).
Please adjust your code to use regular ndarray.
"""


def params_to_list(J, verbose=False):

    params = J.parameters.dict_params

    intensity = params['intensity']
    alpha = params['alpha']
    delay = params['delay']
    azimuth = params['azimuth']
    ellipticity_angle = params['ellipticity_angle']
    a, b = params['length_axes'][0], params['length_axes'][1]

    if verbose is True:
        print("({}, {}, {}, {}, {}, {}, {})".format(
            intensity, alpha, delay, azimuth, ellipticity_angle, a, b))

    return intensity, alpha, delay, azimuth, ellipticity_angle, a, b


# TODO: quitar los números pequeños y radianes, etc
class TestJonesVectorParameters(object):
    def test_linear_light(self):

        solution = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
        solution = np.array(solution)
        M1 = Jones_vector('M1')
        M1.linear_light(angle=0 * degrees)
        proposal = params_to_list(M1, verbose=True)
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: 0 degrees"

        solution = [
            1.0, 0.7853981633974483, 0.0, 0.7853981633974482, 0.0, 1.0, 0.0
        ]
        solution = np.array(solution)
        M1 = Jones_vector('M1')
        M1.linear_light(angle=45 * degrees)
        proposal = params_to_list(M1, verbose=True)
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: 45 degrees"

        solution = [
            1.0, 1.5707963267948966, 0.0, 1.5707963267948966, 0.0, 1.0, 0.0
        ]
        solution = np.array(solution)
        M1 = Jones_vector('M1')
        M1.linear_light(angle=90 * degrees)
        proposal = params_to_list(M1, verbose=True)
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: 90 degrees"

        solution = [
            1.0, 0.7853981633974484, 0, 0.7853981633974484,
            6.123233995736766e-17, 0.0, 1.0
        ]
        solution = np.array(solution)
        M1 = Jones_vector('M1')
        M1.linear_light(angle=135 * degrees)
        proposal = params_to_list(M1, verbose=True)
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: 135 degrees"
        # TODO: delay está mal
        solution = [
            1.0, 1.2246467991473532e-16, 0, 0.0, 1.4997597826618576e-32, 1.0,
            1.2246467991473532e-16
        ]
        solution = np.array(solution)
        M1 = Jones_vector('M1')
        M1.linear_light(angle=180 * degrees)
        proposal = params_to_list(M1, verbose=True)
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: 180 degrees"

    def test_circular_light(self):

        solution = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
        solution = np.array(solution)
        M1 = Jones_vector('M1')
        M1.linear_light(angle=0 * degrees)
        proposal = params_to_list(M1, verbose=True)
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + ".py --> example: 0 degrees"
