#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Filters based on calculating rolling means.
@author: Dmytro Shynkevych
"""

import numpy as np
import pandas as pd

from sklearn.base import TransformerMixin


class RollingMeanSmoother(TransformerMixin):
    """A rolling mean smoother with switchable kernel.

    Args:
        window (int, optional): Number of timestamps to include in the window.
            If not given, the smoother will have to be fitted before use.
        center: (bool, optional): Whether the window should be centered on current datum.
            If False, the window will lag behind (ending at current datum). Default is True.
        kernel: (str, optional): If given, the mean will be weighted according to the kernel.
            Otherwise, an unweighted mean will be used.
            The value must be one of the `win_type`s supported by scipy.signal.
        **kwargs: Kernel-specific keyword arguments.
    """

    def __init__(self, window=None, center=True, kernel=None, **kwargs):
        self.center = center
        self.kernel = kernel
        self._kernel_kwargs = kwargs
        self.window = window

    def fit(self, data, max_mean_err=None):
        """
        Fit the window size to given time series with given error budget.

        Args:
            data (pd.Series): The data to fit to. Index must be monotonic.
            max_mean_err (float, optional): Maximal allowable deviation from original.
                The default is 20% of the average magnitude, which is empirically reasonable.

        Returns:
            RollingMeanSmoother: A fitted smoother.
        """
        if self.window is not None:  # explicitly given or already fitted
            return self
        if max_mean_err is None:
            max_mean_err = np.abs(data).mean() * 0.2

        # Bisect on rmse of transformed data
        lo, hi = 1, data.shape[0]
        while lo < hi:
            mid = (lo + hi) // 2
            self.window = mid
            transformed = self.transform(data)
            mean_err = np.mean(np.abs(data - transformed))
            if mean_err > max_mean_err:
                hi = mid
            else:
                lo = mid + 1
        self.window = lo - 1  # lo is the least such that rmse(lo) > max

        return self

    def transform(self, data):
        """Apply smoothing to given time series.
        The series is padded in both directions with the first and the last datum
        respectively so that the mean can be calculated everywhere.

        Args:
            data (pd.Series): The data to smoothen. Index must be monotonic.

        Returns:
            pd.Series: Smoothened output of the same shape as input data.
        """
        if self.center:
            left = self.window // 2
            right = (self.window - 1) // 2
            lpad = pd.Series([data.iloc[0]] * left)
            rpad = pd.Series([data.iloc[-1]] * right)
            data = lpad.append(data).append(rpad)
        else:
            data = pd.Series([data.iloc[0]] * self.window).append(data)

        res = data.rolling(self.window, win_type=self.kernel, center=self.center).mean(**self._kernel_kwargs)

        if self.center:
            if right > 0:  # [...:-0] is not a valid range
                return res.iloc[left:-right]
            else:
                return res.iloc[left:]
        else:
            return res.iloc[self.window :]
