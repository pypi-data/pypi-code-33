"""
Impute missing data in time-series specific ways, such as interpolation.
"""

from warnings import warn
import os
import pandas as pd
from pandas.tseries.frequencies import to_offset
import numpy as np

from ftk.time_series_data_frame import TimeSeriesDataFrame
from ftk.base_estimator import AzureMLForecastTransformerBase, loggable
from ftk.exception import NotTimeSeriesDataFrameException, \
    NotSupportedException, TransformValueException
from ftk.verify import Messages
from ftk.utils import tick_formatter, get_period_offsets_from_dates, import_plot_and_formatter, get_matplotlib_attr
from ftk.constants import HORIZON_COLNAME

class TimeSeriesImputer(AzureMLForecastTransformerBase):
    """
    .. py:class:: TimeSeriesImputer
    Imputation transformer for imputing the missing values of data frame columns.

    .. _pandas.Series.interpolate: https://pandas.pydata.org/pandas-docs/
                                stable/generated/pandas.Series.interpolate.html
    .. _pandas.Series.fillna: https://pandas.pydata.org/pandas-docs/stable/
                                generated/pandas.Series.fillna.html
    .. _pandas.DateOffset: https://pandas.pydata.org/pandas-docs/stable/timeseries.html#dateoffset-objects


    :param input_column:
        The name(s) of the column(s) need(s) to be imputed.
    :type input_column: str, list of str.

    :param option:
        One of {'interpolate', 'fillna'}.
        The 'interpolate' and 'fillna' options have additional
        parameters that specify their operation. 
    :type option: str

    :param method: 
        Can be used for option 'interpolate' or 'fillna', see
        pandas.Series.interpolate or pandas.Series.fillna respectively
        for more information.
    :type method: str

    :param limit: 
        Can be used for option 'interpolate' or 'fillna', see
        pandas.Series.interpolate or pandas.Series.fillna respectively
        for more information.
    :type limit: str

    :param value:
        Can be used for option 'fillna', see pandas.Series.fillna
        for more information.

    :param limit_direction:
        can be used for option 'interpolate', see pandas.Series.interpolate
        for more information.
    :type limit_direction: str

    :param order:
        can be used for option 'interpolate', see pandas.Series.interpolate
        for more information.
    :type order: str

    :param freq:
        Time series frequency.
        If the freq is string, this string needs to be a pandas Offset Alias.
        See pandas.DateOffset for more information.
    :type freq: str or pandas.DateOffset object

    :param origin:
        If provided, the datetime will be filled back to origin for
        all grains.
    :type origin: str or datetime-like
    :param end:
        If provided, the datetime will be filled up to end for all grains.
    :type end: string or datetime-like

    :param impute_by_horizon:
        See documentation for TimeSeriesImputer.transform() for more
        information.
    :type impute_by_horizon: bool

    Examples:

    Construct a sample dataframe: df1
    Notice that df1 is not a regular time series, because for store 'a', 
    the row for date '2017-01-03' is missing.

    >>> data1 = pd.DataFrame(
    ...  {'store': ['a', 'a', 'b', 'b', 'c', 'c', 'c', 'd', 
    ...            'd', 'd', 'd', 'd', 'd', 'd', 'd'],
    ...   'date': pd.to_datetime(
    ...      ['2017-01-02', '2017-01-04', '2017-01-01', '2017-01-02', 
    ...       '2017-01-01', '2017-01-02', '2017-01-03', '2017-01-01', 
    ...       '2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05', 
    ...       '2017-01-06', '2017-01-07', '2017-01-08']),
    ...   'sales': [1, np.nan, 2, np.nan, 6, 7, np.nan, 10, 11, 15, 13, 14, 
    ...             np.nan, np.nan, 15],
    ...   'price': [np.nan, 3, np.nan, 4, 3, 6, np.nan, 2, 6, 3, 5, 5, 
    ...             np.nan, np.nan, 6]})
    >>> df1 = TimeSeriesDataFrame(data1, grain_colnames=['store'], 
    ...                           time_colname='date', ts_value_colname='sales')
    >>> df1
    >>>                price  sales
    >>> date       store
    2017-01-02 a        nan   1.00
    2017-01-04 a       3.00    nan
    2017-01-01 b        nan   2.00
    2017-01-02 b       4.00    nan
    2017-01-01 c       3.00   6.00
    2017-01-02 c       6.00   7.00
    2017-01-03 c        nan    nan
    2017-01-01 d       2.00  10.00
    2017-01-02 d       6.00  11.00
    2017-01-03 d       3.00  15.00
    2017-01-04 d       5.00  13.00
    2017-01-05 d       5.00  14.00
    2017-01-06 d        nan    nan
    2017-01-07 d        nan    nan
    2017-01-08 d       6.00  15.00

    If you run infer_freq, the 'regular_ts' attribute is False,
    with inferred frequency 'D'.

    >>> df1.infer_freq() # doctest: +SKIP
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    {'regular_ts': False, 'freq': 'D'}

    >>> sorted(df1.infer_freq().items())
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    [('freq', 'D'), ('regular_ts', False)]

    Impute df1 for single column 'sales' with option 'default'
    Notice here, for store 'a', the missing row for date '2017-01-03' 
    is added and imputed as well.
    Also by default, the freq that is used to fill in the missing date 
    is the inferred frequency from df1.infer_freq(), in this case: 'D'

    >>> imputer1 = TimeSeriesImputer(input_column='sales', option='default')
    >>> imputer1.transform(df1)
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred. 
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
 

    >>>      date  price      sales store
    0  2017-01-02    NaN   1.000000     a
    1  2017-01-03    NaN   1.000000     a
    2  2017-01-04    3.0   1.000000     a
    3  2017-01-01    NaN   2.000000     b
    4  2017-01-02    4.0   2.000000     b
    5  2017-01-01    3.0   6.000000     c
    6  2017-01-02    6.0   7.000000     c
    7  2017-01-03    NaN   7.000000     c
    8  2017-01-01    2.0  10.000000     d
    9  2017-01-02    6.0  11.000000     d
    10 2017-01-03    3.0  15.000000     d
    11 2017-01-04    5.0  13.000000     d
    12 2017-01-05    5.0  14.000000     d
    13 2017-01-06    NaN  14.333333     d
    14 2017-01-07    NaN  14.666667     d
    15 2017-01-08    6.0  15.000000     d

    If you want to specify the freq explicitly, you can also use the 
    'freq' key argument to pass the freq, since in some cases the inferred 
    frequency might not be exact, such as no frequency is inferred from 
    any time series, or there are multiple frequencies inferred and the 
    one chosen is not the one you want.

    >>> imputer2 = TimeSeriesImputer(input_column='sales', option='default',
    ...                              freq='D')
    >>> imputer2.transform(df1) 
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
   

    >>>      date  price      sales store
    0  2017-01-02    NaN   1.000000     a
    1  2017-01-03    NaN   1.000000     a
    2  2017-01-04    3.0   1.000000     a
    3  2017-01-01    NaN   2.000000     b
    4  2017-01-02    4.0   2.000000     b
    5  2017-01-01    3.0   6.000000     c
    6  2017-01-02    6.0   7.000000     c
    7  2017-01-03    NaN   7.000000     c
    8  2017-01-01    2.0  10.000000     d
    9  2017-01-02    6.0  11.000000     d
    10 2017-01-03    3.0  15.000000     d
    11 2017-01-04    5.0  13.000000     d
    12 2017-01-05    5.0  14.000000     d
    13 2017-01-06    NaN  14.333333     d
    14 2017-01-07    NaN  14.666667     d
    15 2017-01-08    6.0  15.000000     d

    The default option is just the same as set option='interpolate', 
    method='linear' and limit_direction='both'

    >>> imputer3 = TimeSeriesImputer(input_column='sales', 
    ...                              option='interpolate', method='linear', 
    ...                              limit_direction='both')
    >>> imputer3.transform(df1)  
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
   

    >>>      date  price  sales store
    0  2017-01-02    NaN   1.000000     a
    1  2017-01-03    NaN   1.000000     a
    2  2017-01-04    3.0   1.000000     a
    3  2017-01-01    NaN   2.000000     b
    4  2017-01-02    4.0   2.000000     b
    5  2017-01-01    3.0   6.000000     c
    6  2017-01-02    6.0   7.000000     c
    7  2017-01-03    NaN   7.000000     c
    8  2017-01-01    2.0  10.000000     d
    9  2017-01-02    6.0  11.000000     d
    10 2017-01-03    3.0  15.000000     d
    11 2017-01-04    5.0  13.000000     d
    12 2017-01-05    5.0  14.000000     d
    13 2017-01-06    NaN  14.333333     d
    14 2017-01-07    NaN  14.666667     d
    15 2017-01-08    6.0  15.000000     d

    You can also impute for list of columns. Here, impute df1 for both 
    'sales' and 'price' columns.

    >>> imputer4 = TimeSeriesImputer(input_column=['sales', 'price'], 
    ...                              option='default')
    >>> imputer4.transform(df1)
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.

    >>>      date  price  sales store
    0  2017-01-02  3.000000   1.000000     a
    1  2017-01-03  3.000000   1.000000     a
    2  2017-01-04  3.000000   1.000000     a
    3  2017-01-01  4.000000   2.000000     b
    4  2017-01-02  4.000000   2.000000     b
    5  2017-01-01  3.000000   6.000000     c
    6  2017-01-02  6.000000   7.000000     c
    7  2017-01-03  6.000000   7.000000     c
    8  2017-01-01  2.000000  10.000000     d
    9  2017-01-02  6.000000  11.000000     d
    10 2017-01-03  3.000000  15.000000     d
    11 2017-01-04  5.000000  13.000000     d
    12 2017-01-05  5.000000  14.000000     d
    13 2017-01-06  5.333333  14.333333     d
    14 2017-01-07  5.666667  14.666667     d
    15 2017-01-08  6.000000  15.000000     d

    You can also set options to 'interpolate' and use key arguments such as 
    'method', 'limit', 'limit_direction' and 'order' 
    from pandas.Series.interpolate
    Note if the specific method used does not apply to some of the grains, 
    the default linear interpolation is used for those grains.

    >>> imputer5 = TimeSeriesImputer(input_column=['sales'], 
    ...                              option='interpolate', method='barycentric')
    >>> imputer5.transform(df1)
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
   
    >>>      date  price  sales store
    0  2017-01-02    NaN   1.000000     a
    1  2017-01-03    NaN   1.000000     a
    2  2017-01-04    3.0   1.000000     a
    3  2017-01-01    NaN   2.000000     b
    4  2017-01-02    4.0   2.000000     b
    5  2017-01-01    3.0   6.000000     c
    6  2017-01-02    6.0   7.000000     c
    7  2017-01-03    NaN   8.000000     c
    8  2017-01-01    2.0  10.000000     d
    9  2017-01-02    6.0  11.000000     d
    10 2017-01-03    3.0  15.000000     d
    11 2017-01-04    5.0  13.000000     d
    12 2017-01-05    5.0  14.000000     d
    13 2017-01-06    NaN  26.904762     d
    14 2017-01-07    NaN  42.428571     d
    15 2017-01-08    6.0  15.000000     d

    You can also set options to 'fillna' and use use key arguments such as 
    'method', 'value' and 'limit'methods from pandas.Series.fillna

    >>> imputer6 = TimeSeriesImputer(input_column=['sales'], option='fillna', method='ffill')
    >>> imputer6.transform(df1)
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.

    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.

    >>>      date  price  sales store
    0  2017-01-02    NaN    1.0     a
    1  2017-01-03    NaN    1.0     a
    2  2017-01-04    3.0    1.0     a
    3  2017-01-01    NaN    2.0     b
    4  2017-01-02    4.0    2.0     b
    5  2017-01-01    3.0    6.0     c
    6  2017-01-02    6.0    7.0     c
    7  2017-01-03    NaN    7.0     c
    8  2017-01-01    2.0   10.0     d
    9  2017-01-02    6.0   11.0     d
    10 2017-01-03    3.0   15.0     d
    11 2017-01-04    5.0   13.0     d
    12 2017-01-05    5.0   14.0     d
    13 2017-01-06    NaN   14.0     d
    14 2017-01-07    NaN   14.0     d
    15 2017-01-08    6.0   15.0     d

    >>> imputer7 = TimeSeriesImputer(input_column=['sales'], option='fillna', 
    ...                              value=0)
    >>> imputer7.transform(df1)
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
   

    >>>      date  price  sales store
    0  2017-01-02    NaN    1.0     a
    1  2017-01-03    NaN    0.0     a
    2  2017-01-04    3.0    0.0     a
    3  2017-01-01    NaN    2.0     b
    4  2017-01-02    4.0    0.0     b
    5  2017-01-01    3.0    6.0     c
    6  2017-01-02    6.0    7.0     c
    7  2017-01-03    NaN    0.0     c
    8  2017-01-01    2.0   10.0     d
    9  2017-01-02    6.0   11.0     d
    10 2017-01-03    3.0   15.0     d
    11 2017-01-04    5.0   13.0     d
    12 2017-01-05    5.0   14.0     d
    13 2017-01-06    NaN    0.0     d
    14 2017-01-07    NaN    0.0     d
    15 2017-01-08    6.0   15.0     d

    Sometime, you might want to fill values up to some eariler date or down 
    to some later date, you can use the origin and end property 
    for the purpose.

    >>> imputer8 = TimeSeriesImputer(input_column=['sales'], option='fillna', 
    ...                              value=0, origin='2016-12-28')
    >>> imputer8.transform(df1)
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
  

    >>>      date  price  sales store
    0  2016-12-28    NaN    0.0     a
    1  2016-12-29    NaN    0.0     a
    2  2016-12-30    NaN    0.0     a
    3  2016-12-31    NaN    0.0     a
    4  2017-01-01    NaN    0.0     a
    5  2017-01-02    NaN    1.0     a
    6  2017-01-03    NaN    0.0     a
    7  2017-01-04    3.0    0.0     a
    8  2016-12-28    NaN    0.0     b
    9  2016-12-29    NaN    0.0     b
    10 2016-12-30    NaN    0.0     b
    11 2016-12-31    NaN    0.0     b
    12 2017-01-01    NaN    2.0     b
    13 2017-01-02    4.0    0.0     b
    14 2016-12-28    NaN    0.0     c
    15 2016-12-29    NaN    0.0     c
    16 2016-12-30    NaN    0.0     c
    17 2016-12-31    NaN    0.0     c
    18 2017-01-01    3.0    6.0     c
    19 2017-01-02    6.0    7.0     c
    20 2017-01-03    NaN    0.0     c
    21 2016-12-28    NaN    0.0     d
    22 2016-12-29    NaN    0.0     d
    23 2016-12-30    NaN    0.0     d
    24 2016-12-31    NaN    0.0     d
    25 2017-01-01    2.0   10.0     d
    26 2017-01-02    6.0   11.0     d
    27 2017-01-03    3.0   15.0     d
    28 2017-01-04    5.0   13.0     d
    29 2017-01-05    5.0   14.0     d
    30 2017-01-06    NaN    0.0     d
    31 2017-01-07    NaN    0.0     d
    32 2017-01-08    6.0   15.0     d

    >>> imputer9 = TimeSeriesImputer(input_column=['sales'], option='fillna', 
    ...                              value=0, end='2017-01-10')
    >>> imputer9.transform(df1)
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
   
    >>>      date  price  sales store
    0  2017-01-02    NaN    1.0     a
    1  2017-01-03    NaN    0.0     a
    2  2017-01-04    3.0    0.0     a
    3  2017-01-05    NaN    0.0     a
    4  2017-01-06    NaN    0.0     a
    5  2017-01-07    NaN    0.0     a
    6  2017-01-08    NaN    0.0     a
    7  2017-01-09    NaN    0.0     a
    8  2017-01-10    NaN    0.0     a
    9  2017-01-01    NaN    2.0     b
    10 2017-01-02    4.0    0.0     b
    11 2017-01-03    NaN    0.0     b
    12 2017-01-04    NaN    0.0     b
    13 2017-01-05    NaN    0.0     b
    14 2017-01-06    NaN    0.0     b
    15 2017-01-07    NaN    0.0     b
    16 2017-01-08    NaN    0.0     b
    17 2017-01-09    NaN    0.0     b
    18 2017-01-10    NaN    0.0     b
    19 2017-01-01    3.0    6.0     c
    20 2017-01-02    6.0    7.0     c
    21 2017-01-03    NaN    0.0     c
    22 2017-01-04    NaN    0.0     c
    23 2017-01-05    NaN    0.0     c
    24 2017-01-06    NaN    0.0     c
    25 2017-01-07    NaN    0.0     c
    26 2017-01-08    NaN    0.0     c
    27 2017-01-09    NaN    0.0     c
    28 2017-01-10    NaN    0.0     c
    29 2017-01-01    2.0   10.0     d
    30 2017-01-02    6.0   11.0     d
    31 2017-01-03    3.0   15.0     d
    32 2017-01-04    5.0   13.0     d
    33 2017-01-05    5.0   14.0     d
    34 2017-01-06    NaN    0.0     d
    35 2017-01-07    NaN    0.0     d
    36 2017-01-08    6.0   15.0     d
    37 2017-01-09    NaN    0.0     d
    38 2017-01-10    NaN    0.0     d

    The imputer works not only for TimeSeriesDataFrame with time_index 
    column of type DatetimeIndex, but also TimeSeriesDataFrame with 
    time_index column of PeriodIndex as well.

    >>> data2 = pd.DataFrame(
    ...   {'store': ['a', 'a', 'a', 'b', 'b'],
    ...    'brand': ['a', 'a', 'a', 'b', 'b'],
    ...    'date': pd.PeriodIndex(
    ...      ['2011-12', '2012-02', '2012-03', '2012-02', '2012-03'], 
    ...      dtype = 'period[M]', freq = 'M'),
    ...    'sales': [1, np.nan, 5, 2, np.nan],
    ...    'price': [np.nan, 2, 3, np.nan, 4]})
    >>> df2 = TimeSeriesDataFrame(data2, grain_colnames=['store', 'brand'], 
    ...                          time_colname='date', ts_value_colname='sales')
    >>> df2
      brand    date  price  sales store
    0     a 2011-12    NaN    1.0     a
    1     a 2012-02    2.0    NaN     a
    2     a 2012-03    3.0    5.0     a
    3     b 2012-02    NaN    2.0     b
    4     b 2012-03    4.0    NaN     b
    >>> imputer10 = TimeSeriesImputer(input_column=['sales'], 
    ...                               option='fillna', value=0)
    >>> imputer10.transform(df2)
      brand    date  price  sales store
    0     a 2011-12    NaN    1.0     a
    1     a 2012-01    NaN    0.0     a
    2     a 2012-02    2.0    0.0     a
    3     a 2012-03    3.0    5.0     a
    4     b 2012-02    NaN    2.0     b
    5     b 2012-03    4.0    0.0     b

    """

    def __init__(self, input_column,
                 option='fillna', method=None, value=None, limit=None,
                 limit_direction='forward', order=None, freq=None, 
                 origin=None, end=None, impute_by_horizon=False):

        self.input_column = input_column
        self.option = option
        self.method = method
        self.value = value
        self.limit = limit
        self.limit_direction = limit_direction
        self.order = order
        self.freq = freq
        self.origin = origin
        self.end = end
        self.impute_by_horizon = impute_by_horizon

    @classmethod
    def _impute_with_interpolation_single_group(cls, single_group_data,
                                                **kwargs):
        """
        Impute missing values for all columns in TimeSeriesDataFrame which
        contains single group data, using pandas.DataFrame.interpolate.
        """

        # Need to reset the index for pd.DataFrame.interpolate
        # since only method=linear works when the Series has a multi-index
        interpolation_df = pd.DataFrame(single_group_data).reset_index(
            drop=True)
        interpolation_df = interpolation_df.interpolate(**kwargs)

        # get the index back
        interpolation_df.index = single_group_data.index

        return interpolation_df

    @classmethod
    def _impute_with_fillna_single_group(cls, single_group_data, **kwargs):
        """
        Impute missing values for all columns in TimeSeriesDataFrame which
        contains single group data, using pandas.DataFrame.fillna.
        """
        return single_group_data.fillna(**kwargs)

    @classmethod
    def _impute_missing_value_by_cols(
            cls, input_df, input_column, sort_index_by_col, by_cols=None,
            option='interpolate', freq=None, origin=None, end=None, **kwargs):
        """
        Impute missing vlaue within each group, where groups are defined by
        by_cols.
        """

        if not input_df.check_regularity(freq=freq):
            input_df_filled = input_df.fill_datetime_gap(
                freq=freq, origin=origin, end=end)
            if not input_df_filled.check_regularity(freq=freq):
                raise TransformValueException('The TimeSeriesDataFrame does '
                                              'not have time index with '
                                              'regular datetime gaps even '
                                              'after fill_datetime_gaps.')
            # sort by time
            input_df_filled = input_df_filled.sort_index(
                level=sort_index_by_col)
        else:
            # sort by time
            input_df_filled = input_df.sort_index(
                level=sort_index_by_col)

        if option == 'interpolate':
            if by_cols is None:
                input_df_filled[input_column] = \
                    cls._impute_with_interpolation_single_group(
                        input_df_filled[input_column], **kwargs)
            else:
                input_df_filled[input_column] = input_df_filled.groupby(
                    by=by_cols, group_keys=False)[input_column].apply(
                    lambda x: cls._impute_with_interpolation_single_group(
                        x, **kwargs))
        elif option == 'fillna':
            if by_cols is None:
                input_df_filled[input_column] = \
                    cls._impute_with_fillna_single_group(
                        input_df_filled[input_column], **kwargs)
            else:
                input_df_filled[input_column] = input_df_filled.groupby(
                    by=by_cols, group_keys=False)[input_column].apply(
                    lambda x: cls._impute_with_fillna_single_group(x, **kwargs))
        else:
            raise TransformValueException(
                'please provide the supported option arguments.')
        return input_df_filled

    @classmethod
    def _check_value_same_by_column(cls, input_df, value_col, by_cols):
        """
        Check whether the value_col have same value given by_cols.
        """
        whether_unique = input_df.groupby(by=by_cols).apply(
            lambda x: (len(np.unique(x[value_col].values)) == 1) or np.isnan(
                x[value_col].values).all())
        return whether_unique.values.all()

    @classmethod
    def _condense_values_by_column(cls, input_df, value_cols, by_cols):
        """
        condense the value_cols by by_cols.
        """
        return input_df.groupby(by=by_cols)[value_cols].first()

    @classmethod
    def _join_df_with_multiindex(cls, df, multi_index):
        """
        This helper function is created for scenario when you have a df with
        pandas.MultiIndex which are a subset of indexes in multi_index,
        you want to get a output data frame with index equal to multi_index
        and values joined from the df.
        """
        output_df = pd.DataFrame(df)
        on_cols = df.index.names
        output_df = output_df.reset_index()
        index_df = multi_index.to_frame(index=False)
        output_df = index_df.merge(output_df, on=on_cols, how='left')
        output_df = output_df.set_index(multi_index.names)
        return output_df

    @loggable
    def fit(self, X, y=None):
        """
        Fit is empty for this transform; this method is just a pass-through

        :param X: Ignored.

        :param y: Ignored.

        :return: self
        :rtype: TimeSeriesImputer
        """
        return self

    @loggable
    def transform(self, X):
        """
        Perform imputation on requested data frame columns.

        Here is a brief summary how the TimeSeriesImputer works:
            1. When the input TimeSeriesDataFrame has no property `origin_time`:
                The time series valus will be imputed within each time series
                from single `grain_colnames`.
            2. When the input TimeSeriesDataFrame has property `origin_time`:
                a) If time series from the same `grain_colnames have the same value
                as long as the values of `time_colname` are the same, the time
                series will be condensed to have no `origin_time_colname`,
                and get imputed in the condensed data frame. And the imputed
                values will be joined back to the original data by
                `grain_colnames` and `time_colname`.
                b) If time series from the same `grain_colnames` have the same
                value as long as the values of `origin_time_colname` are the
                same, the time series will be condensed to have no
                `time_colname`, and get imputed in the condensed data frame. And
                the imputed values will be joined back to the original data by
                `grain_colnames` and `origin_time_colname`.
                c) For time series not falling into either a) or b), they will be
                imputed within sub-time-series from single combination of
                `grain_colnames` and `origin_time_colname` if impute_by_horizon
                is True. Otherwise, it will be imputed within sub-time-series from
                single combination of `grain_colnames` and `horizon`.

        :param X: Data frame to transform
        :type X: :class:`ftk.dateframets.TimeSeriesDataFrame`

        :return: A data frame with imputed column(s)
        :rtype: :class:`ftk.dateframets.TimeSeriesDataFrame`
        """

        if not isinstance(X, TimeSeriesDataFrame):            
            raise NotTimeSeriesDataFrameException(
                Messages.INVALID_TIMESERIESDATAFRAME, 
                "Type of the input data frame is {0}".format(type(X)))

        if self.option == 'interpolate':
            kwargs = {'method': self.method, 'limit': self.limit,
                      'limit_direction': self.limit_direction,
                      'order': self.order}
        elif self.option == 'fillna':
            kwargs = {'method': self.method, 'value': self.value,
                      'limit': self.limit}
        else:
            raise TransformValueException(('The option {} is not '
                                           'supported.').format(self.option))

        if self.freq is None:
            freq = X.infer_freq()
            if freq is None:
                raise TransformValueException('The freq cannot be inferred. '
                                              'Please provide freq argument.')
        else:
            freq = self.freq

        if isinstance(self.input_column, str):
            self.input_column = [self.input_column]

        for col in self.input_column:
            if col not in X.columns:
                raise TransformValueException(
                    ('Column {} does not exist in the '
                     'input data.').format(col))

        if X.origin_time_colname is None:
            return self._impute_missing_value_by_cols(
                input_df=X, input_column=self.input_column,
                sort_index_by_col=X.time_colname,
                by_cols=X.grain_colnames, option=self.option, freq=freq,
                origin=self.origin, end=self.end, **kwargs)
        else:
            X_copy = X.copy()
            # To shorten the variable name, in the following code:
            # `got` means grain_and_origin_time
            # `gt` means grain_and_time
            # `ot` means origin_time
            # `t` means time
            cols_same_given_got = []
            cols_same_given_gt = []
            other_cols = []
            for col in self.input_column:
                # check if the column have same value given grain + time
                if self._check_value_same_by_column(
                        input_df=X, value_col=col,
                        by_cols=X.time_and_grain_colnames):
                    cols_same_given_gt += [col]
                # check if the column have same value given grain + origin_time
                elif self._check_value_same_by_column(
                        input_df=X, value_col=col,
                        by_cols=X.slice_key_colnames):
                    cols_same_given_got += [col]
                else:
                    other_cols += [col]

            if len(cols_same_given_gt) > 0:
                # get the condensed data frame which only have grain + time
                gt_condensed_df = self._condense_values_by_column(
                    input_df=X[cols_same_given_gt],
                    value_cols=cols_same_given_gt,
                    by_cols=X.time_and_grain_colnames)
                gt_condensed_df = TimeSeriesDataFrame(
                    gt_condensed_df, time_colname=X.time_colname,
                    grain_colnames=X.grain_colnames)
                # impute missing value
                gt_condensed_df = self._impute_missing_value_by_cols(
                    input_df=gt_condensed_df,
                    input_column=cols_same_given_gt,
                    sort_index_by_col=X.time_colname,
                    by_cols=X.grain_colnames, option=self.option,
                    freq=freq, origin=self.origin, end=self.end, **kwargs)
                # join the condensed data frame back
                X_copy[cols_same_given_gt] = self._join_df_with_multiindex(
                    gt_condensed_df, X.index)

            if len(cols_same_given_got) > 0:
                # get the condensed data frame which only have grain +
                # origin_time
                got_condensed_df = self._condense_values_by_column(
                    input_df=X[cols_same_given_got],
                    value_cols=cols_same_given_got,
                    by_cols=X.slice_key_colnames)
                got_condensed_df = TimeSeriesDataFrame(
                    got_condensed_df, time_colname=X.origin_time_colname,
                    grain_colnames=X.grain_colnames)
                # impute missing value
                got_condensed_df = self._impute_missing_value_by_cols(
                    input_df=got_condensed_df,
                    input_column=cols_same_given_got,
                    sort_index_by_col=X.origin_time_colname,
                    by_cols=X.grain_colnames, option=self.option,
                    freq=freq, origin=self.origin, end=self.end, **kwargs)
                # join the condensed data frame back
                X_copy[cols_same_given_got] = self._join_df_with_multiindex(
                    got_condensed_df, X.index)

            if len(other_cols) > 0:
                if not self.impute_by_horizon:
                    # impute by slice_key_colnames
                    X_copy[other_cols] = self._impute_missing_value_by_cols(
                        input_df=X_copy[other_cols], input_column=other_cols,
                        sort_index_by_col=X.time_colname,
                        by_cols=X.slice_key_colnames, option=self.option,
                        freq=freq, origin=self.origin, end=self.end,
                        **kwargs)
                else:
                    if HORIZON_COLNAME in X_copy.columns:
                        warn(('The column {} will be overwritted to store the '
                              'integer forecasting horizon.').format(
                            HORIZON_COLNAME))
                    X_copy[HORIZON_COLNAME] = get_period_offsets_from_dates(
                        X_copy.index.get_level_values(X_copy.origin_time_colname),
                        X_copy.index.get_level_values(X_copy.time_colname),
                        freq=freq)
                    # impute by grain + horizon
                    if X_copy.grain_colnames is None:
                        grain_and_horizon_colnames = [HORIZON_COLNAME]
                    else:
                        grain_and_horizon_colnames = X_copy.grain_colnames + [
                            HORIZON_COLNAME]

                    X_copy[other_cols] = self._impute_missing_value_by_cols(
                        input_df=X_copy, input_column=other_cols,
                        sort_index_by_col=X.time_colname,
                        by_cols=grain_and_horizon_colnames, option=self.option,
                        freq=freq, origin=self.origin, end=self.end,
                        **kwargs)[other_cols]

            return X_copy

    @classmethod
    def _plot_gaps_and_imputation_single_series(cls, single_grain_data,
                                                column_to_plot,
                                                tsimputer=None,
                                                freq=None, figure_size=(8, 6),
                                                lw=2, marker='o',
                                                save_fig=False,
                                                fig_path=os.getcwd(), **kwargs):

        """
        Plot the datetime gaps for a single grain data, and plot the imputed
        series if a TimeSeriesImputer is provided.

        :param single_grain_data:
            A TimeSeriesDataFrame contains single grain's data.
        :type single_grain_data: TimeSeriesDataFrame
        :param column_to_plot:
            name of the column to plot on
        :type column_to_plot: str
        :param tsimputer:
            The TimeSeriesImputer used to impute the input time series data.
            If this is not None, the result plot will show how the time
            series values get imputed in the missing datetime gaps.
        :type tsimputer: TimeSeriesImputer
        :param freq:
            The frequency of the time series in the data frame
            If freq=None, the frequency will be inferred.
        :type freq: str or pandas.DateOffset object
        :param figure_size:
            width, height in inches.
        :type figure_size: tuple of integers
        :param lw:
            line width
        :type lw: float
        :param marker:
            a valid marker stype.
            See https://matplotlib.org/api/markers_api.html#module-matplotlib.markers
            for details.
        :param save_fig:
            Whether to save the figures produced.
        :type save_fig: bool
        :param fig_path:
            The path where the produced figures to be saved to.
        :type fig_path: str
        :param **kwargs:
            Additional options to be passed to matplotlib.axes.Axes.plot.

        :return:
            Tuple of (figure object, axis object).
            The figure objects can be further customized and saved.
            The axis objects can be used to customize the plots.
        :rtype:
            tuple of (matplotlib.figure.Figure,
            matplotlib.axes._subplots.AxesSubplot)
         """
        plt, FuncFormatter = import_plot_and_formatter()
        if single_grain_data.origin_time_colname is not None:
            # the assumption here is that people usually check the missing
            # data before bring the origin_time into the forecasting scenario.
            # These kinds of charts may become hard to understand when there
            # is origin_time.
            raise NotSupportedException('plot datetime gaps in '
                                        'TimeSeriesDataFrame with '
                                        'origin_time_colname is not supported.')

        if column_to_plot not in single_grain_data.columns:
            raise ValueError(('The column {} is not in the input data '
                             'frame.').format(column_to_plot))

        if freq is None:
            freq = single_grain_data.infer_freq()
            if freq is None:
                raise ValueError('The freq of the input data cannot be '
                                 'inferred. Please provide the freq value.')

        if not isinstance(freq, pd.DateOffset):
            freq = to_offset(freq)

        datetime_gap_filled_series = single_grain_data.fill_datetime_gap(
            freq=freq)[[column_to_plot]]

        missing_timestamps = datetime_gap_filled_series[
            datetime_gap_filled_series[column_to_plot].isnull()].time_index
        missing_timestamps = missing_timestamps.sort_values()

        if tsimputer is not None:
            if column_to_plot not in tsimputer.input_column:
                raise ValueError(
                    ('The {} is not in tsimputer.input_column.').format(
                        column_to_plot))

            imputed_series = tsimputer.fit(
                datetime_gap_filled_series[[column_to_plot]]).transform(
                datetime_gap_filled_series[[column_to_plot]])
            series_to_plot = imputed_series[column_to_plot]
        else:
            series_to_plot = datetime_gap_filled_series[column_to_plot]

        fig, ax = plt.subplots(figsize=figure_size)

        # plot the time series
        if tsimputer is None:
            ax.plot(datetime_gap_filled_series.time_index,
                    series_to_plot.values, lw=lw, marker=marker, color='black',
                    **kwargs)
        else:
            ax.plot(datetime_gap_filled_series.time_index,
                    series_to_plot.values, lw=lw, color='black', alpha=0.5,
                    **kwargs)

            null_sel = datetime_gap_filled_series[column_to_plot].isnull()
            not_null_sel = datetime_gap_filled_series[column_to_plot].notnull()

            scatter_imputed = ax.scatter(
                datetime_gap_filled_series[null_sel].time_index.values,
                series_to_plot[null_sel].values,
                marker=marker, c='r')
            scatter_original = ax.scatter(
                datetime_gap_filled_series[not_null_sel].time_index.values,
                series_to_plot[not_null_sel].values,
                marker=marker, c='black')
            ax.legend((scatter_original, scatter_imputed),
                      ('original data', 'imputed data'),
                      loc=2, bbox_to_anchor=(1.05, 1), ncol=1)

        # plot the missing datetime gaps in red
        for t in missing_timestamps:
            if (t - freq) in missing_timestamps:
                t_min = t
            else:
                t_min = t - freq
            t_max = t + freq
            if t == datetime_gap_filled_series.time_index.min():
                t_min = t
            elif t == datetime_gap_filled_series.time_index.max():
                t_max = t

            ax.axvspan(t_min, t_max, facecolor='r', alpha=0.4)

        # plot attributes: title, labels, etc..
        ax.set_xlabel(datetime_gap_filled_series.time_colname)
        ax.set_ylabel(column_to_plot)

        # set the ticker format to y axis so that it renders properly for large
        # values
        formatter = FuncFormatter(tick_formatter)
        ax.yaxis.set_major_formatter(formatter)

        ax.grid()
        fig.autofmt_xdate()

        if single_grain_data.grain_colnames is None:
            grain_string = ''
        else:
            grain_string = ', '.join(
                [g + ' ' + str(single_grain_data.index.get_level_values(g)[0])
                 for g in single_grain_data.grain_colnames])
            grain_string = ' of ' + grain_string

        if tsimputer is None:
            title_str = ('The time series{} for column {}\nwith missing ' \
                         'datetime gaps in red color').format(grain_string,
                                                              column_to_plot)
        else:
            title_str = ('The imputed time series{} for column {}\nwith ' \
                         'originally missing datetime gaps in red ' \
                         'color').format(grain_string, column_to_plot)

        ax.set_title(title_str)
        plt.tight_layout()

        if save_fig:
            if not os.path.exists(fig_path):
                os.makedirs(fig_path)

            plt.close()
            fig_title = '_'.join(
                [g + '_' + str(single_grain_data.index.get_level_values(g)[0])
                 for g in single_grain_data.grain_colnames])
            fig_title = 'plot_' + fig_title
            fig.savefig(os.path.join(fig_path, fig_title))

        return fig, ax

    @classmethod
    def _plot_gaps_and_imputation_multiple_series(cls, input_data,
                                                  columns_to_plot,
                                                  tsimputer=None,
                                                  freq=None, figure_size=(8, 6),
                                                  lw=2, marker='o',
                                                  save_fig=False,
                                                  fig_path=os.getcwd(),
                                                  **kwargs):

        """
        Plot the datetime gaps for input TimeSeriesDataFrame, and plot the
        imputed series if a TimeSeriesImputer is provided.
        A single plot will be created for combination of each time series in
        the input data and each column in columns_to_plot.

        :param input_data:
            The input TimeSeriesDataFrame to create plots on.
        :type input_data: TimeSeriesDataFrame
        :param columns_to_plot:
            name of the columns to plot on
        :type columns_to_plot: str or list of str
        :param tsimputer:
            The TimeSeriesImputer used to impute the input time series data.
            If this is not None, the result plot will show how the time
            series values get imputed in the missing datetime gaps.
        :type tsimputer: TimeSeriesImputer
        :param freq:
            The frequency of the time series in the data frame
            If freq=None, the frequency will be inferred.
        :type freq: str or pandas.DateOffset object
        :param figure_size:
            width, height in inches.
        :type figure_size: tuple of integers
        :param lw:
            line width
        :type lw: float
        :param marker:
            a valid marker stype.
            See https://matplotlib.org/api/markers_api.html#module-matplotlib.markers
            for details.
        :param save_fig:
            Whether to save the figures produced.
        :type save_fig: bool
        :param fig_path:
            The path where the produced figures to be saved to.
        :type fig_path: str
        :param **kwargs:
         Additional options to be passed to matplotlib.axes.Axes.plot.

        :return:
            List of tuple of (figure object, axis object).
            The figure objects can be further customized and saved.
            The axis objects can be used to customize the plots.
        :rtype:
            list of tuple of (matplotlib.figure.Figure,
            matplotlib.axes._subplots.AxesSubplot)
        """

        rcParams = get_matplotlib_attr('matplotlib', 'rcParams')
        if freq is None:
            freq = input_data.infer_freq()
            if freq is None:
                raise ValueError('The freq of the input data cannot be '
                                 'inferred. Please provide the freq value.')

        if isinstance(columns_to_plot, str):
            columns_to_plot = [columns_to_plot]

        if len(columns_to_plot) == 0:
            raise ValueError('There is no column specified in columns_to_plot.')

        grouped_input_data = input_data.groupby_grain()

        # calculate the number of plots will be produced
        grain_num = len(grouped_input_data)
        column_num = len(columns_to_plot)
        plot_num = grain_num * column_num

        if plot_num >= rcParams['figure.max_open_warning']:
            # figure.max_open_warning is the threshold that matplotlib has
            # if exceeding it, a warning of consuming too much memory by
            # opening too many plots will be thrown
            # we will recommend user to turn save_fig on, if there are lots
            # of plots being generated here.
            warn(('There will be {} plots generated and displayed. '
                  'Displaying large amout of plots could potentially lead to '
                  'memeory issue, try to set save_fig=True if '
                  'you have memory issues.'
                  '').format(plot_num), UserWarning)

        fig_ax_list = []
        for grp_name, grp in grouped_input_data:
            for col in columns_to_plot:
                fig_grp_col, ax_grp_col = \
                    cls._plot_gaps_and_imputation_single_series(
                        single_grain_data=grp, column_to_plot=col,
                        tsimputer=tsimputer, freq=freq,
                        figure_size=figure_size, lw=lw, marker=marker,
                        save_fig=save_fig, fig_path=fig_path, **kwargs)
                fig_ax_list.append((fig_grp_col, ax_grp_col))
        return fig_ax_list

    @classmethod
    def plot_datetime_gaps(cls, input_data, columns_to_plot, freq=None,
                           figure_size=(8, 6), lw=2, marker='o',
                           save_fig=False, fig_path=os.getcwd(), **kwargs):

        """
        Plot the datetime gaps in the input data.
        A single plot will be created for combination of each time series in
        the input data and each column in columns_to_plot.

        :param input_data:
            The input TimeSeriesDataFrame to create plots on.
        :type input_data: TimeSeriesDataFrame
        :param columns_to_plot:
            name of the columns to plot on
        :type columns_to_plot: str or list of str
        :param freq:
            The frequency of the time series in the data frame
            If freq=None, the frequency will be inferred.
        :type freq: str or pandas.DateOffset object
        :param figure_size:
            width, height in inches.
        :type figure_size: tuple of integers
        :param lw:
            line width
        :type lw: float
        :param marker:
            a valid marker stype.
            See https://matplotlib.org/api/markers_api.html#module-matplotlib.markers
            for details.
        :param save_fig:
            Whether to save the figures produced.
        :type save_fig: bool
        :param fig_path:
            The path where the produced figures to be saved to.
        :type fig_path: str
        :param **kwargs:
            Additional options to be passed to matplotlib.axes.Axes.plot.

        :return:
            List of tuple of (figure object, axis object).
            The figure objects can be further customized and saved.
            The axis objects can be used to customize the plots.
        :rtype:
            list of tuple of (matplotlib.figure.Figure,
            matplotlib.axes._subplots.AxesSubplot)
        """
        fig_ax_list = cls._plot_gaps_and_imputation_multiple_series(
            input_data, columns_to_plot, tsimputer=None, freq=freq,
            figure_size=figure_size, lw=lw, marker=marker, save_fig=save_fig,
            fig_path=fig_path, **kwargs)

        return fig_ax_list

    def plot_imputation(self, input_data, columns_to_plot=None, freq=None,
                        figure_size=(8, 6), lw=2, marker='o', save_fig=False,
                        fig_path=os.getcwd(), **kwargs):

        """
        Plot how the input series gets imputed using the TimeSeriesImputer.
        A single plot will be created for combination of each time series in
        the input data and each column in columns_to_plot.

        :param input_data:
            The input TimeSeriesDataFrame to create plots on.
        :type input_data: TimeSeriesDataFrame
        :param columns_to_plot:
            name of the columns to plot on
        :type columns_to_plot: str or list of str
        :param freq:
            The frequency of the time series in the data frame
            If freq=None, the frequency will be inferred.
        :type freq: str or pandas.DateOffset object
        :param figure_size:
            width, height in inches.
        :type figure_size: tuple of integers
        :param lw:
            line width
        :type lw: float
        :param marker:
            a valid marker stype.
            See https://matplotlib.org/api/markers_api.html#module-matplotlib.markers
            for details.
        :param save_fig:
            Whether to save the figures produced.
        :type save_fig: bool
        :param fig_path:
            The path where the produced figures to be saved to.
        :type fig_path: str
        :param **kwargs:
            Additional options to be passed to matplotlib.axes.Axes.plot.

        :return:
            List of tuple of (figure object, axis object).
            The figure objects can be further customized and saved.
            The axis objects can be used to customize the plots.
        :rtype:
            list of tuple of (matplotlib.figure.Figure,
            matplotlib.axes._subplots.AxesSubplot)
        """

        if columns_to_plot is None:
            columns_to_plot = self.input_column

        fig_ax_list = self._plot_gaps_and_imputation_multiple_series(
            input_data, columns_to_plot, tsimputer=self, freq=freq,
            figure_size=figure_size, lw=lw, marker=marker, save_fig=save_fig,
            fig_path=fig_path, **kwargs)

        return fig_ax_list
