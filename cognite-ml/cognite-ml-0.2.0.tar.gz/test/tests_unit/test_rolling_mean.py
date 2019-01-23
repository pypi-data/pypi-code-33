import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_array_equal

from cognite_ml.filters import RollingMeanSmoother

inp = pd.Series([1, 2, 3, 4, 3, 2, 1])

class TestClassRollingMean:
    def test_even(self):
        expected = pd.Series([5/4, 7/4, 10/4, 12/4, 12/4, 10/4, 7/4])
        assert_array_equal(RollingMeanSmoother(window=4).transform(inp), expected)

    def test_odd(self):
        expected = pd.Series([4/3, 6/3, 9/3, 10/3, 9/3, 6/3, 4/3])
        assert_array_equal(RollingMeanSmoother(window=3).transform(inp), expected)

    def test_fit(self):
        spikes = pd.Series([5, 5, 10, 5, 5, 5, 10, 5, 5])
        rs1 = RollingMeanSmoother().fit(spikes, max_mean_err=0)
        rs2 = RollingMeanSmoother().fit(spikes, max_mean_err=5)
        rs3 = RollingMeanSmoother().fit(spikes)
        assert rs1.window == 1
        assert rs2.window == 8
        assert rs3.window == 2

    def test_lag(self):
        expected = pd.Series([3/3, 4/3, 6/3, 9/3, 10/3, 9/3, 6/3])
        rs = RollingMeanSmoother(window=3, center=False)
        assert_array_equal(rs.transform(inp), expected)

    def test_nofit(self):
        rs = RollingMeanSmoother(window=42)
        assert rs.fit(inp).window == 42

    def test_fit_edge(self):
        mean = np.abs(inp).mean()
        rs = RollingMeanSmoother().fit(inp, max_mean_err=mean)
        assert rs.window == len(inp) - 1
