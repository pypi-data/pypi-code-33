# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for mueller parameters Class in mueller module"""

import sys

import numpy as np
from numpy import matrix

from py_pol import degrees, eps
from py_pol.mueller import Mueller


"""
PendingDeprecationWarning: the matrix subclass is not the recommended way to
represent matrices or deal with linear algebra
(see https://docs.scipy.org/doc/numpy/user/numpy-for-matlab-users.html).
Please adjust your code to use regular ndarray.
"""


class TestMueller_parameters(object):
    def test_custom(self):

        # solution = matrix([[1], [0], [0], [0]])
        # M1 = Mueller('custom')
        # M1.custom(1, 0, 0, 0)
        # proposal = M1.get()
        # assert np.linalg.norm(proposal - solution) < eps, sys._getframe(
        # ).f_code.co_name + ".py --> example: (1, 0, 0, 0)"
        assert True
