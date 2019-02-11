# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utlitiy functions for manipulating data in a TimeSeriesDataFrame object."""
import datetime

import pandas as pd

from .forecasting_exception import NotTimeSeriesDataFrameException
from .forecasting_utils import _range

from . import forecasting_verify as verify

# NOTE:
# Do not import TimeSeriesDataFrame or ForecastDataFrame at the top of this
# file, because both of them import this file as well, and circular references
# emerge. It is ok to import TSDF or FDF inside a function instead.


def last_n_periods_split(tsdf, test_size):
    """
    Split input dataset into training and testing datasets.

    The split is such that, for each grain, this function
    assign last ``test_size`` number of data points into a test dataset and
    hold off the initial data points for training dataset.
    If origin_time is not set in ``tsdf``, then each data point corresponds to
    a single time step (period).

    :param tsdf:
        Input dataset to generate the test dataset from.
    :type tsdf:
        TimeSeriesDataFrame.
    :param test_size:
        The number of data points per grain to set aside for test dataset.
    :type test_size:
        int.
    :return:
        A 2-tuple of TimeSeriesDataFrames, first element is training dataset and
        second element is test dataset.
    """
    from .time_series_data_frame import TimeSeriesDataFrame

    # checking inputs
    verify.type_is_numeric(type(test_size), '')
    verify.type_is_one_of(type(tsdf), [TimeSeriesDataFrame], "Input")

    if test_size < 0:
        raise ValueError("Expected 'test_size' > 0, got {}".format(test_size))

    grouped_data = tsdf.groupby_grain()

    # check if test_size is too small
    min_rows_per_grain = grouped_data.size().min()
    if (test_size > min_rows_per_grain - 1):
        raise ValueError(
            "With 'test_size' of {}, some grains won't have enough data!".format(
                test_size))

    # continue with the split
    train_data = grouped_data.apply(lambda x: x[:(len(x) - test_size)])

    # Call deduplicate just in case groupby/apply duplicated grain index levels
    train_data.deduplicate_index(inplace=True)

    test_data = grouped_data.apply(lambda x: x[(len(x) - test_size):])
    test_data.deduplicate_index(inplace=True)

    return train_data, test_data


def construct_day_of_quarter(X):
    """
    Compute day of quarter from the time index in the input.

    Also compute information that could be derived from
    ``time_index`` column, e.g., year, quarter, first day of the quarter.

    :param X:
        Input dataframe to compute day of quarter on.
    :type X:
        TimeSeriesDataFrame.
    :return:
        A data frame containing a ```day_of_quarter``` column and a few
        other time related columns used for computing ```day_of_quarter```.
    """
    from .time_series_data_frame import TimeSeriesDataFrame

    if not isinstance(X, TimeSeriesDataFrame):
        raise NotTimeSeriesDataFrameException(
            verify.Messages.XFORM_INPUT_IS_NOT_TIMESERIESDATAFRAME)
    df = pd.DataFrame({'date': X.time_index})
    df['year'] = df['date'].dt.year
    df['quarter'] = df['date'].dt.quarter
    df['first_month_of_quarter'] = (df['quarter'] - 1) * 3 + 1
    df['first_day_of_quarter'] = pd.to_datetime(
        df['year'].map(str) + "/" +
        df['first_month_of_quarter'].map(str) + "/1")
    # must set time zone to day_of_quarter, else date arithmetic fails
    # when index is tz-aware
    df['first_day_of_quarter'] = df['first_day_of_quarter'].dt.tz_localize(
        X.time_index.tz)
    df['day_of_quarter'] = \
        (df['date'] - df['first_day_of_quarter']).dt.days + 1

    return df


def datetime_is_date(x):
    """
    Test if input datetime object has any hour/minute/second components.

    :param x:
        Input datetime object to be checked.
    :type x:
        pandas.core.indexes.datetimes.DatetimeIndex
    :return:
        Return ``True``  if an input date is without any hour/minute/second components otherwise return ``False``.
    """
    result = _range((x - x.normalize()).values).astype(int) == 0
    return result


def formatted_int_to_date(n):
    """
    Convert a formatted integer datetime (like n=20180425) to date.

    6-digit (180413) formatted integer will be interpreted as being in the 21st century (2018-04-13).
    5-digit (80413) formatted integer will be interpreted as being in 2000-2009 (2008-04-13).

    :param n:
        Formatted integer representing a date.
    :type n:
        int.
    :return:
        A datetime.date object corresponding to the input formatted integer.
    """
    if n >= 10**2 and n < 10**4:
        y = 2000
    elif n >= 10**4 and n < 10**6:
        y = 2000 + n // (10**4)
    elif n >= 10**7 and n < 10**8:
        y = n // (10**4)
    else:
        raise ValueError("{} does not look like a formated date integer to us.".format(n))

    md = n % (10**4)
    m = md // (10**2)
    d = md % (10**2)

    return datetime.date(y, m, d)
