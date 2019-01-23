#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

@author: agleim
"""

import numpy as np
from sklearn.utils.validation import check_array
from sklearn.base import BaseEstimator, TransformerMixin


__all__ = ["SlidingWindows"]


class SlidingWindows(TransformerMixin):
    def __init__(self, window_size=2, step_size=1):
        self.window_size = window_size
        self.step_size = step_size

    def fit(self, *_):
        return self

    def transform(self, X, *_):

        X = check_array(X)

        (num_samples, num_dims) = X.shape
        window_size = self.window_size
        step_size = self.step_size

        assert num_samples >= window_size, "The window size can't exceed number of samples."

        windows = np.zeros((int(np.ceil((num_samples - window_size + 1) / step_size)), num_dims * window_size))

        for i in range(0, num_samples, step_size):
            if i + window_size > num_samples:
                break

            w = X[i : i + window_size, :].ravel()
            windows[int(np.ceil(i / step_size)), :] = w

        return windows
