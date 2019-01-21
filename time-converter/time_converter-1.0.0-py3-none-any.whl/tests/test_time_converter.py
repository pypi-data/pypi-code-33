"""
This module includes tests for the time_Timeer module
"""

from time_converter import Time
from pytest import approx, raises
import datetime as dt
import numpy as np


def test_consistency():
    assert Time(1000, 'sol').to('sol') == approx(1000)
    assert Time(dt.datetime(2018, 1, 1)).to('dt') == dt.datetime(2018, 1, 1)
    assert Time(6e8, 'sclk').to('sclk') == approx(6e8)
    assert Time((2018, 2.5), 'doy').to('doy') == (2018, 2.5)
    assert Time(2018.5, 'decimalyear').to('decimalyear') == approx(2018.5)
    assert Time(1517742867, 'posix').to('posix') == 1517742867


def test_values():
    time = Time(dt.datetime(2018, 1, 15))
    assert time.to('sol') == approx(1935.221950230014)
    assert time.to('sclk') == approx(569244654.78994048)
    assert time.to('doy') == (2018, approx(15))
    assert time.to('decimalyear') == approx(2018.0383561643835)
    assert time.to('posix') == 1515974400


def test_empty():
    time = Time([])
    assert np.array_equal(time.to('sol'), [])


def test_error():
    with raises(ValueError):
        Time(1, 'foo')


def test_pandas():
    import pandas as pd
    series = pd.Series([1, 2])
    converted = Time(series, 'sol').to('sol')
    assert (converted == series).all()
    assert type(converted) == pd.core.series.Series
