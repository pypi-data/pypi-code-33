"""
Create features as aggregates (e.g. average or maximum) of values from a rolling window.
"""

import numpy as np
import pandas as pd
from pandas.core.series import Series
from pandas.tseries.offsets import DateOffset
from pandas.tseries.frequencies import to_offset
from collections import defaultdict
import warnings, os, sys, inspect

from ftk.transform_utils import OriginTimeMixin
from ftk.base_estimator import AzureMLForecastTransformerBase, loggable
from ftk.time_series_data_frame import TimeSeriesDataFrame
from ftk.exception import (TransformException, NotTimeSeriesDataFrameException,
                           DataFrameIncorrectFormatException)
from ftk.verify import is_iterable_but_not_string, check_cols_exist, Messages
from ftk.constants import *

class RollingWindow(AzureMLForecastTransformerBase, OriginTimeMixin):
    """
    .. py:class:: RollingWindow
    A transformation class for creating rolling window features from the
    columns of a TimeSeriesDataFrame. 

    Rolling windows are temporally defined with respect to origin times
    in the TimeSeriesDataFrame. The origin time in a data frame row
    indicates the right date/time boundary of a window. 

    If the input data frame does not contain origin times, they
    will be created based on the ```max_horizon``` parameter. 

    :param window_size:
         Size of the moving window. 
         Either the number of observations in each window
         or a time-span specified as a pandas.DateOffset.
         Note that when the size is given as a DateOffset,
         the window may contain a variable number of observations.
    :type window_size: int, pandas.DateOffset
    
    :param transform_dict:
        A dictionary specifying the rolling window transformations
        to apply on the columns. The keys are functions
        or names of pre-defined Pandas rolling window methods.
        See https://pandas.pydata.org/pandas-docs/stable/computation.html#method-summary.
        The dict values are columns on which to apply the functions.
        Each value can be a single column name or a list
        of column names.
    :type transform_dict: dict

    :param window_opts: 
        A dictionary of keyword window options.
        These will be passed on to the pandas.Rolling
        constructor as **kwargs.
        See pandas.DataFrame.rolling for details.

        To avoid target leakage, the ```center``` option
        setting here is ignored and always set to False.

        The ```closed``` option is also ignored.
        For integer window size, it is set to `both`.
        For DateOffset window size, it is set to `right`.
    :type window_opts: dict

    :param transform_opts:
        A dictionary of aggregation function options. The keys are aggregation
        function names. The value is again a dictionary with two keys: args
        and kwargs, the value of the 'args' key is the positional arguments
        passed to the aggregation function and the value of the 'kwargs' key
        is the keyword arguments passed to the aggregation function.
    :type transform_opts: dict

    :param max_horizon: 
        Integer horizons defining the origin times to create. 
        Parameter can be a single integer - which indicates a maximum
        horizon to create for all grains - or a dictionary where the keys
        are grain levels and each value is an integer maximum horizon.
    :type max_horizon: int, dict

    :param origin_time_colname:
        Name of origin time column to create in case origin times 
        are not already contained in the input data frame.
        The `origin_time_colname` property of the transform output
        will be set to this parameter value in that case.
        This parameter is ignored if the input data frame contains
        origin times.
    :type origin_time_colname: str

    :param dropna: 
        Should missing values from rolling window feature creation be dropped? 
        Defaults to False.
        Note that the missing values from the test data are not dropped but 
        are instead 'filled in' with values from training data.
    :type dropna: bool    

    Examples:

    >>> data = {'store': [1] * 10 + [2] * 10 + [3] * 10,
                'sales': [250, 150, 300, 200, 400, 300, 150, 200, 350, 100,
                          400, 300, 200, 450, 200, 350, 450, 150, 250, 500,
                          150, 400, 500, 300, 350, 250, 200, 400, 500, 450],
                'customers': [28, 15, 30, 24, 47, 33, 15, 20, 36, 13,
                              38, 30, 25, 43, 20, 35, 46, 17, 28, 44,
                              15, 47, 50, 30, 35, 29, 25, 40, 48, 42],
                'date': pd.to_datetime(
                ['2017-01-01', '2017-01-02', '2017-01-03', '2017-01-04', 
                '2017-01-05', '2017-01-06', '2017-01-07', '2017-01-08', 
                '2017-01-09', '2017-01-10'] * 3)}
    >>> tsdf = TimeSeriesDataFrame(
    data, grain_colnames='store',
    time_colname='date', ts_value_colname='sales')
    >>> window_size = 3
    >>> transform_dict = {'sum': ['sales', 'customers'], 'quantile': 'sales'}
    >>> window_opts = {'min_periods': 2}
    >>> transform_opts = {'quantile': {'args': [0.25],
    'kwargs': {'interpolation': 'lower'}}}
    >>> rolling_window_transformer = RollingWindow(window_size,
    transform_dict, window_opts, transform_opts)
    >>> rolling_window_transformer.fit_transform(tsdf).head(10)
                                 customers  sales  customers_sum_window3  \
    date       store origin                                                
    2017-01-01 1     2016-12-31         28    250                    nan   
    2017-01-02 1     2017-01-01         15    150                    nan   
    2017-01-03 1     2017-01-02         30    300                  43.00   
    2017-01-04 1     2017-01-03         24    200                  73.00   
    2017-01-05 1     2017-01-04         47    400                  69.00   
    2017-01-06 1     2017-01-05         33    300                 101.00   
    2017-01-07 1     2017-01-06         15    150                 104.00   
    2017-01-08 1     2017-01-07         20    200                  95.00   
    2017-01-09 1     2017-01-08         36    350                  68.00   
    2017-01-10 1     2017-01-09         13    100                  71.00   

                                 sales_sum_window3  sales_quantile_window3  
    date       store origin                                                 
    2017-01-01 1     2016-12-31                nan                     nan  
    2017-01-02 1     2017-01-01                nan                     nan  
    2017-01-03 1     2017-01-02             400.00                  150.00  
    2017-01-04 1     2017-01-03             700.00                  150.00  
    2017-01-05 1     2017-01-04             650.00                  150.00  
    2017-01-06 1     2017-01-05             900.00                  200.00  
    2017-01-07 1     2017-01-06             900.00                  200.00  
    2017-01-08 1     2017-01-07             850.00                  150.00  
    2017-01-09 1     2017-01-08             650.00                  150.00  
    2017-01-10 1     2017-01-09             700.00                  150.00  

    """

    def __init__(self, window_size, transform_dict, window_opts={},
                 transform_opts={}, max_horizon=1, 
                 origin_time_colname=ORIGIN_TIME_COLNAME_DEFAULT, 
                 dropna=False):
        self.window_size = window_size
        self.transform_dict = transform_dict
        self.window_opts = window_opts
        self.transform_opts = transform_opts
        self.max_horizon = max_horizon
        self.origin_time_colname = origin_time_colname
        self.dropna = dropna

        self._is_fit = False
        self._cache = None
        self._ts_freq = None
        self._feature_name_map = {}
        self._agg_func_map = {}
        self._func_name_to_func_map = {}

    @property
    def window_size(self):
        """
        See `window_size` parameter
        """
        return self._window_size

    @window_size.setter
    def window_size(self, val):
        if not isinstance(val, int) and not isinstance(val, DateOffset):
            try:
                val = to_offset(val)
            except ValueError:
                raise ValueError('The window_size must be of type '
                                 'integer, a string that can be converted '
                                 'to DateOffset, or DateOffset. Instead '
                                 'got {0}'.format(type(val)))
        self._window_size = val

    @property
    def transform_dict(self):
        """
        See `transform_dict` parameters
        """
        return self._transform_dict

    @transform_dict.setter
    def transform_dict(self, val):
        if not isinstance(val, dict):
            raise ValueError('The transform_dict must be a dictionary. '
                             'Instead got {0}'.format(type(val)))
        self._transform_dict = val

    @property
    def window_opts(self):
        """
        See `window_opts` parameters
        """
        return self._window_opts

    @window_opts.setter
    def window_opts(self, val):
        if not isinstance(val, dict):
            raise ValueError('The window_opts must be a dictionary. '
                             'Instead got {0}'.format(type(val)))

        # Some window options are not supported.
        # Force default values and warn user
        not_configurable = ['center', 'closed']
        for opt in not_configurable:
            if opt in val:
                warnings.warn(('RollingWindow: "{0}" is not ').format(opt) + \
                    'a configurable window option.')
                val.pop(opt)

        self._window_opts = val

    @property
    def transform_opts(self):
        """
        See `transform_opts` parameters
        """
        return self._transform_opts

    @transform_opts.setter
    def transform_opts(self, val):
        if not isinstance(val, dict):
            raise ValueError('The transform_opts must be a dictionary. '
                             'Instead got {0}'.format(type(val)))
        self._transform_opts = val

    def _make_func_name_to_func_map(self):
        """
        Create a map, function name -> function,
        for the functions in the transform_dict property.

        This method is used when when we need to lookup a *possibly* callable
        function from a column name in pandas.Rolling.agg output 
        """

        func_map = {(func.__name__ if callable(func) else func): func 
                    for func in self.transform_dict}

        return func_map

    def _make_feature_name(self, col, func):
        """
        Get the name of the rolling window feature
        associated with column 'col' and function 'func.'
        'func' can be a callable function or a string.
        """

        window_sz_str = (self.window_size.freqstr 
                         if isinstance(self.window_size, pd.DateOffset) 
                         else str(self.window_size))
        func_name = func.__name__ if callable(func) else func
        
        feat_name = col + '_' + func_name + \
            '_window' + window_sz_str

        return feat_name

    def _make_feature_name_map(self, X):
        """
        Make a mapping from (column, func) pairs
        to feature names from the transform_dict property.
        'func' can be a callable function or a string.
        
        Column names must exist in the data frame, X.
        """
        new_feature_dict = {}
        for func, cols in self.transform_dict.items():
            check_cols_exist(X, cols)
            if is_iterable_but_not_string(cols):
                for c in cols:
                    new_feature_dict[(c, func)] = \
                        self._make_feature_name(c, func)
            elif isinstance(cols, str):
                new_feature_dict[(cols, func)] = \
                    self._make_feature_name(cols, func)
            else:
                pass

        return new_feature_dict

    def _make_agg_func_map(self, feature_name_map):
        """
        Starting from a feature name map,
        create a map: column -> list of functions to apply to column.

        This method creates a dictionary compatible with
        the Pandas "agg" function input.  
        """

        agg_func_map = defaultdict(list)
        for col, func in feature_name_map:
            agg_func_map[col].append(func)
            
        return agg_func_map

    def preview_column_names(self, X):
        """
        Get a list of new columns that would be created by this transform.
        This method does not add any columns to X, it just previews what
        the transform would add if it were applied.

        :param X: Input data for the transform
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`

        :return: List of new column names
        :rtype: list
        """

        name_map = self._make_feature_name_map(X)

        return list(name_map.values())

    def _cache_training_data(self, X_train):
        """
        Cache an appropriate amount of training data so that a
        test set can be featurized without unnecessarily dropping
        observations
        """

        def get_tail_by_grain(gr, df):

            # Need grab an extra period for each horizon
            #  past 1
            h_max = self.max_horizon_from_key_safe(gr, self.max_horizon)
            extra_tail_for_horizon = h_max - 1

            if isinstance(self.window_size, pd.DateOffset):
                # Figure out the date boundaries of the window
                tail_start = df.time_index.max() - self.window_size - \
                    extra_tail_for_horizon * self._ts_freq
                
            else:
                # Get the last 'window_size' periods.
                # Some complication here because there may 
                #  be duplicate dates if the feature set is multi-horizon.
                # To handle this case, extract the last window from
                #  the underlying time-series and find the start date
                #  of the window from there
                val_series = df.ts_value.sort_index(level=df.time_colname)
                tail_periods = self.window_size + extra_tail_for_horizon
                tail_series = val_series.iloc[-tail_periods:]
                tail_start = (tail_series.index
                              .get_level_values(df.time_colname).min())
    
            return df[df.time_index >= tail_start]           
        
        if X_train.grain_colnames is None:
            self._cache = get_tail_by_grain('', X_train)
        else:
            self._cache = X_train.groupby_grain().apply(
                lambda Xgr: get_tail_by_grain(Xgr.name, Xgr))

    def _apply_rolling_agg_to_single_series(self, X_single):
        """
        Apply Pandas rolling window aggregation to a single time
        series.

        X_single: 
            pandas.DataFrame with *one index level* (the time index).
            Data frame columns are the columns that will be transformed. 

        Returns a pandas.DataFrame with the transformed columns.
        """
        # Sort by ascending time
        X_single.sort_index(inplace=True, ascending=True)

        # Create some shortcuts
        window_opts = self.window_opts
        feature_name_map = self._feature_name_map
        agg_func_map = self._agg_func_map
        func_name_to_func = self._func_name_to_func_map
        
        X_rolling = X_single.rolling(self.window_size,
                                     **window_opts)

        result_all = []
        if not self.transform_opts:
            # Most aggregation functions don't take arguments and we can
            # simply apply multiple functions to each column in one line of
            # code.     
            result_tmp = X_rolling.agg(agg_func_map)

            # If the result after transformation is a Series, convert it to
            # DataFrame to rename columns.
            if isinstance(result_tmp, Series):
                result_tmp = result_tmp.to_frame()

            if result_tmp.columns.nlevels > 1:
                # When multiple column and function combinations are applied,
                # the result column index has multiple levels.
                # The 'values' property should retrieve a list of 2-tuple
                #  objects. Each tuple is arranged as (column name, function).
                result_tmp.columns = \
                    [feature_name_map[(col, func_name_to_func[func_name])] 
                    for col, func_name in 
                    result_tmp.columns.values]
            else:
                # For single level column index, we expect that only
                #  one function was applied to each column
                # Check to make sure this is the case
                nonunique_by_col = {col: agg_func_map[col] 
                                    for col in result_tmp.columns
                                    if len(agg_func_map[col]) > 1}
                if len(nonunique_by_col) > 0:
                    raise TransformException(
                        ('RollingWindow: Expected a single function for each '\
                            + 'column. Instead got: {0}')
                            .format(nonunique_by_col))

                result_tmp.columns = \
                    [feature_name_map[(col, agg_func_map[col][0])]
                     for col in result_tmp.columns]

            result_all.append(result_tmp)
        else:
            # When transform_opts is not empty, we need to pass some function
            # arguments.
            for col, funcs in agg_func_map.items():
                # Check if any function in the current (column, functions)
                # pair is a key in transform_opts. If yes, go through the
                # functions in col_func one by one. When a function is a key
                # in transform_opts, parse the value of the key to extract
                # args and kwargs and pass them to pd.rolling.agg().
                if any(func in self.transform_opts for func in funcs):
                    for func in funcs:
                        if func in self.transform_opts:
                            func_opts = self.transform_opts[func]
                            if 'args' in func_opts:
                                args = func_opts['args']
                            else:
                                args = {}
                            if 'kwargs' in func_opts:
                                kwargs = func_opts['kwargs']
                            else:
                                kwargs = {}
                        else:
                            args = {}
                            kwargs = {}
                        
                        result_tmp = X_rolling[col].agg(func, *args, **kwargs)
                        if isinstance(result_tmp, Series):
                            result_tmp = result_tmp.to_frame()

                        result_tmp.columns = [feature_name_map[(col, func)]]
                        result_all.append(result_tmp)

                else:
                    # If none of the functions in the current
                    # (column, functions) pair is a key in transform_opts,
                    # simply apply all the functions to the current column at
                    # one time.
                    result_tmp = X_rolling.agg({col: funcs})
                    if isinstance(result_tmp, Series):
                        result_tmp = result_tmp.to_frame()

                    if result_tmp.columns.nlevels > 1:
                        result_tmp.columns = \
                            [feature_name_map[(col, 
                                               func_name_to_func[func_name])] 
                             for col, func_name in result_tmp.columns.values]
                    else:                 
                        # Check that there is one function applied to col
                        if len(funcs) > 1:
                            raise TransformException(
                                ('RollingWindow: Expected a single function '\
                                    + 'for column {0}. Instead got: {1}')
                                    .format(col, funcs))

                        result_tmp.columns = \
                            [feature_name_map[(col, funcs[0])]
                             for col in result_tmp.columns]

                    result_all.append(result_tmp)
        
        # Concat along columns ('cbind' in R)   
        return pd.concat(result_all, axis=1)

    def _transform_single_grain(self, gr, X_gr):
        """
        This function applies all the transformations in col_func_dict to
        the data of a single grain.

        :param X_gr:
            A TimeSeriesDataFrame containing the data of a single
            grain.
        :type X_single: TimeSeriesDataFrame

        :return: 
            A TimeSeriesDataFrame with the transformation result
            columns added to X_single. 

        """
        # Get the list of columns on which to apply rolling window
        xform_cols = list(self._agg_func_map.keys())

        # Get unique time series for requested columns 
        #  as a plain data frame
        X_sub = X_gr._extract_time_series(xform_cols) 
                           
        all_but_time = [lv for lv in X_sub.index.names 
                        if lv != X_gr.time_colname]
        if len(all_but_time) > 0:
            X_sub.reset_index(level=all_but_time,
                              drop=True, inplace=True)
        
        # Perform pandas rolling window op
        rolled_df = \
            self._apply_rolling_agg_to_single_series(X_sub)

        def _shift_window_features_for_horizon(horizon):
            """
            Shift window features to the correct dates and set
            origin times according to the horizon argument.

            This shifting is necessary because pandas rolling windows
            calculate features with a closed right interval by default. 
            That is, the features are set at the right-most slot 
            *within* the window.
            In forecasting applications, this can result in target leakage.

            This function uses the right-most date in the window as the
            *origin time* and shifts the time index ahead by `horizon`
            periods.
            """

            # Set origin dates to the window dates (right-most slot)
            origin_dates = rolled_df.index
            
            # Shift time index ahead by `horizon` and set origin date
            rolled_h = rolled_df.shift(periods=horizon, freq=self._ts_freq)
            
            return rolled_h.assign(**{self.origin_time_colname: origin_dates})

        # Get window features for all horizons
        h_max = self.max_horizon_from_key_safe(gr, self.max_horizon)
        rolled_all_horizons = pd.concat([
             _shift_window_features_for_horizon(h)
             for h in range(1, h_max + 1)])

        # Move origin times to the index
        rolled_all_horizons.set_index(self.origin_time_colname, append=True, 
                                      inplace=True)

        rolling_features = rolled_all_horizons.columns

        # Add window features to the input via left join on the indices
        return X_gr.merge(rolled_all_horizons, how='left',
                          left_index=True, right_index=True)
    
    @loggable
    def fit(self, X, y=None):
        """
        Fit the rolling window. 
        Cache the last window of training data.

        :param X: Data frame of training data
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`

        :param y: Ignored. Included for pipeline compatibility

        :return: self
        :rtype: RollingWindow
        """

        # Make maps for translating data frame column names and
        #  aggregation functions to feature names in the transformed
        #  data frame
        self._func_name_to_func_map = self._make_func_name_to_func_map()
        self._feature_name_map = self._make_feature_name_map(X)
        self._agg_func_map = self._make_agg_func_map(self._feature_name_map)

        # Get time series frequency. 
        # Needed for creating origin dates and window shifting.
        # Assume the freq is the same for train/test sets .
        self._ts_freq = X.infer_freq(return_freq_string=False)

        if X.origin_time_colname is not None:
            # If origin times are set in the input,
            #  detect the maximum horizons to use for
            #  rolling window features
            self.max_horizon = \
                self.detect_max_horizons_by_grain(X, freq=self._ts_freq)

            # Assume that if origins are set in train set, they'll
            #  be set in test set too. 
            self.origin_time_colname = X.origin_time_colname
        
        self._cache_training_data(X)
        self._is_fit = True

        return self

    @loggable
    def transform(self, X):
        """
        This function applies rolling window transformations to the input
        TimeSeriesDataFrame.

        :param X: Data frame to transform
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`

        :return: 
            A new TimeSeriesDataFrame with the transformation result
            columns added to X.
        :rtype: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`

        :raises: :class:`ftk.exception.TransformException`, :class:`ftk.exception.NotTimeSeriesDataFrameException`
        """
        if not self._is_fit:
            raise TransformException(
                'RollingWindow.transform: fit must be called before transform')

        if not isinstance(X, TimeSeriesDataFrame):
            raise NotTimeSeriesDataFrameException(
                Messages.INVALID_TIMESERIESDATAFRAME +
                " Type of the input data frame is {0}".format(type(X)))
       
        # Force center and closed window options
        self._window_opts['center'] = False

        if isinstance(self.window_size, int):
            self._window_opts['closed'] = 'both'
        else:
            self._window_opts['closed'] = 'right'

        # pre-pend cached training data
        try:
            tsdf_full = pd.concat([self._cache, X])
        except DataFrameIncorrectFormatException:
            tsdf_full = X

        # Add origin times up to the max horizon
        #  if the input doesn't already have any origin times
        if tsdf_full.origin_time_colname is None:
            tsdf_full = self.create_origin_times(
                tsdf_full, self.max_horizon,
                freq=self._ts_freq,
                origin_time_colname=self.origin_time_colname)
        
        if tsdf_full.grain_colnames is None:
            warnings.warn('The TimeSeriesDataFrame does not have any '
                          'grain_colnames or origin_time_colnames set, '
                          'Assuming a single time series.')
            tsdf_trans = self._transform_single_grain('', tsdf_full)

        else:
            tsdf_trans = (tsdf_full.groupby_grain()
                          .apply(lambda Xgr: 
                                 self._transform_single_grain(Xgr.name, Xgr)))
        
        # tsdf_trans may have rows from the cache - remove any rows that
        #  aren't in the original input by selecting on the time index
        tsdf_trans = tsdf_trans[tsdf_trans.time_index.isin(X.time_index)]

        if self.dropna:
            # Need to do a little more work if dropna is True.
            # Don't want to drop rows where NaNs are not caused 
            #   by the RollingWindow
            feature_cols = list(self._feature_name_map.values())

            # Get a binary mask indicating which rows to drop.
            # Cast to data frame to avoid TSDF finalize checks.
            df_feats = pd.DataFrame(tsdf_trans[feature_cols], copy=False) 
            notnull_by_column = df_feats.notnull().values
            not_null_all_cols = np.apply_along_axis(all, 1, notnull_by_column)
            tsdf_trans = tsdf_trans[not_null_all_cols]

        return tsdf_trans
