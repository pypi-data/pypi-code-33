"""
A module that provides utlitiy functions that are helpful to manipulate the data in the TimeSeriesDataFrame object.
"""

import numpy as np
import pandas as pd
import collections
import datetime

import ftk.verify
from ftk.utils import _range
from ftk.exception import NotTimeSeriesDataFrameException
from ftk.constants import *

### NOTE:
# Do not import TimeSeriesDataFrame or ForecastDataFrame at the top of this 
# file, because both of them import this file as well, and circular references
# emerge. It is ok to import TSDF or FDF inside a function instead.
###
def detect_seasonality(ts_values):
    """
    Detect a dominant seasonality in a scalar valued time-series.

    A "seasonality" refers to a lag value with a significant peak
    in the autocorrelation function of the series.

    :param ts_values: series values sorted by ascending time
    :type ts_values: numpy.ndarray

    :return: 
        Lag value associated with the strongest autocorrelation peak.
        If no significant peaks can be found, then the function returns
        the value 1
    :rtype: int
    """

    from statsmodels.tsa.tsatools import detrend
    from statsmodels.tsa.stattools import acf

    # Don't bother trying to find a seasonality for very short series
    ts_len = len(ts_values) 
    if ts_len < SEASONAL_DETECT_MIN_OBS:
        return 1

    # Define the autocorr threshold above which a lag is considered "seasonal"
    # Here, we use a combination of a statistical significance level 
    #  (stat_thresh) and a constant correlation value (min_thresh): 
    #  thresh = max(stat_thresh, min_thresh)
    # Null hypothesis for stat_thresh assumes a white noise, gaussian process.
    # The constant, min_thresh, was subjectively determined to be a reasonable
    #  threshold (it is used in the .NET seasonality detector as well)
    z_95 = 1.96
    z_thresh = z_95/np.sqrt(ts_len)
    min_thresh = 0.45
    autocorr_thresh = z_thresh if z_thresh > min_thresh else min_thresh

    # Compute autocorr for lags up to half the data size
    # i.e. Shannon-Nyquist Sampling Theorem
    nlags = int(np.floor(ts_len/2.0))

    # If the data has trend, this biases the autocorr estimate
    # Attempt to remove any linear trend in the series 
    ts_values_detrend = detrend(ts_values, order=1)

    # Compute the autocorr function
    # Plain autocorr is n^2, FFT is nlog(n). So use FFT for long series
    use_FFT = ts_len > SEASONAL_DETECT_FFT_THRESH_SIZE
    ts_values_acf = acf(ts_values_detrend, nlags=nlags, fft=use_FFT)

    # Find the lag (other than 0) with the maximum autocorr
    max_acf_lag = np.argmax(ts_values_acf[1:]) + 1
    max_acf = ts_values_acf[max_acf_lag]

    return max_acf_lag if max_acf >= autocorr_thresh else 1


def last_n_periods_split(tsdf, test_size):
    """
    .. py:method:: last_n_periods_split
    Split input dataset into training and testing datasets such that, for each grain,
    assign last ``test_size`` number of data points into a test dataset and 
    hold off the initial data points for training dataset.
    If origin_time is not set in ``tsdf``, then each data point corresponds to a single time step (period).  

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
    
    from ftk.time_series_data_frame import TimeSeriesDataFrame
    
    # checking inputs
    ftk.verify.type_is_numeric(type(test_size), '');
    ftk.verify.type_is_one_of(type(tsdf), [TimeSeriesDataFrame], "Input");

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
    train_data = grouped_data.apply(lambda x: x[:(len(x)-test_size)])   
    
    # Call deduplicate just in case groupby/apply duplicated grain index levels
    train_data.deduplicate_index(inplace=True)

    test_data  = grouped_data.apply(lambda x: x[(len(x)-test_size):])
    test_data.deduplicate_index(inplace=True)
    
    
    return train_data, test_data


def construct_day_of_quarter(X):
    """
    .. py:method:: construct_day_of_quarter
    Compute day of quarter for ``time_index`` column in ``X`` which is an
    instance of TimeSeriesDataFrame. Also compute information that could be derived from 
    ``time_index`` column, e.g., year, quarter, first day of the quarter.

    :param X:
        Input dataframe to compute day of quarter on.
    :type X: 
        TimeSeriesDataFrame.
    :return: 
        A data frame containing a ```day_of_quarter``` column and a few
        other time related columns used for computing ```day_of_quarter```.
    """
    from ftk.time_series_data_frame import TimeSeriesDataFrame

    if not isinstance(X, TimeSeriesDataFrame):
        raise NotTimeSeriesDataFrameException(
            ftk.verify.Messages.XFORM_INPUT_IS_NOT_TIMESERIESDATAFRAME)
    df = pd.DataFrame({'date': X.time_index})
    df['year'] = df['date'].dt.year
    df['quarter'] = df['date'].dt.quarter
    df['first_month_of_quarter'] = (df['quarter'] - 1) * 3 + 1
    df['first_day_of_quarter'] = pd.to_datetime(
        df['year'].map(str) + "/" + \
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
    .. py:method:: datetime_is_date
    Test whether input datetime object has any hour/minute/second components.

    :param x:
        Input datetime object to be checked.
    :type x: 
        pandas.core.indexes.datetimes.DatetimeIndex
    :return: 
        Return ``True``  if an input date is without any hour/minute/second components otherwise return ``False``.
    """
    result = _range((x- x.normalize()).values).astype(int) == 0
    return result

def formatted_int_to_date(n):
    """
    .. py:method:: formatted_int_to_date
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

    return datetime.date(y,m,d)