# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for stokes module"""

from py_pol.utils import *
"""
PendingDeprecationWarning: the matrix subclass is not the recommended way to
represent matrices or deal with linear algebra
(see https://docs.scipy.org/doc/numpy/user/numpy-for-matlab-users.html).
Please adjust your code to use regular ndarray.
"""


class Test_Utils(object):
    def test_rotation_matrix_Mueller(self):
        solution = np.matrix(
            np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0,
                                                                  1]]))
        proposal = rotation_matrix_Mueller(45 * degrees)
        assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        ).f_code.co_name + "@ Rotation 45 deg"
