#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

@author: agleim
"""

import pytest
import numpy as np
from numpy.testing import assert_array_equal

from cognite_ml.timeseries import SlidingWindows


class TestClassSlidingWindow(object):
    def test_1D_data_step_1(self):
        X = np.array(np.array([1, 2, 3, 4, 5]).reshape(-1, 1))
        win = SlidingWindows(window_size=2, step_size=1).transform(X)
        assert_array_equal(win, np.array([[1, 2], [2, 3], [3, 4], [4, 5]]))

    def test_1D_data_step_3(self):
        X = np.array(np.array([1, 2, 3, 4, 5]).reshape(-1, 1))
        win = SlidingWindows(window_size=2, step_size=3).transform(X)
        assert_array_equal(win, np.array([[1, 2], [4, 5]]))

    def test_1D_data_too_large_windowsize(self):
        X = np.array(np.array([1, 2, 3, 4, 5]).reshape(-1, 1))
        with pytest.raises(AssertionError):
            win = SlidingWindows(window_size=7, step_size=1).transform(X)

    def test_2D_data_step_1(self):
        X = np.array([[1, 10, 100], [2, 20, 200], [3, 30, 300]])
        win = SlidingWindows(window_size=2, step_size=1).transform(X)
        assert_array_equal(win, np.array([[1., 10., 100., 2., 20., 200.], [2., 20., 200., 3., 30., 300.]]))
