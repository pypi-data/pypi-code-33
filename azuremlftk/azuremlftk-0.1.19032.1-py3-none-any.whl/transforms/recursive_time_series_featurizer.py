"""
Use forecasts from univariate models as features. Can be used to populate values indexed in the future.
"""

import pandas as pd
import numpy as np
import os
import sys
from itertools import product
from sklearn.base import clone

from ftk.constants import *
from ftk.compute import ComputeStrategyMixin
from ftk.factor_types import ComputeJobType
from ftk.time_series_data_frame import TimeSeriesDataFrame
from ftk.models import RecursiveForecaster
from ftk.base_estimator import AzureMLForecastTransformerBase, loggable
from ftk.verify import (istype, Messages, is_iterable_but_not_string,
                        check_type_collection_or_dict, is_int_like, 
                        is_large_enough)
from ftk.exception import (NotTimeSeriesDataFrameException,
                           NotSupportedException,
                           TransformException,
                           TransformValueException,
                           TransformTypeException,
                           DataFrameIncorrectFormatException)
from ftk.utils import (flatten_list, make_repeated_list_strings_unique,
                       get_period_offsets_from_dates, invert_dict_of_lists)
from ftk.transform_utils import OriginTimeMixin
from warnings import warn

class RecursiveTimeSeriesFeaturizer(ComputeStrategyMixin, OriginTimeMixin, 
									AzureMLForecastTransformerBase):
    """
    .. py:class:: RecursiveTimeSeriesFeaturizer
    Transformer that constructs multi-step features from a time series by
    applying RecursiveForecaster models to them repeatedly.

     This transform returns a TimeSeriesDataFrame with properly set index 
     that has at least 2 columns, `time_colname` and `origin_time_colname`, 
     plus `grain_colnames`, if any. There will be as many new columns as there 
     were models in the `model` input argument, with names like 
     `x_y` where `x` is the name of the input column to generate features from 
     and `y` is model name.

    :param forecaster_list:
        Forecasters which  will be used to 'featurize' the time series. 
        Any recursive-style model works, e.g. Arima, Ets, Naive, or 
        Seasonal Naive. 

        This input can be a single RecursiveForecaster instance, a list
        of RecursiveForecaster instances, or a list of 
        (name, RecursiveForecaster instance) tuples.
        When a tuple is provided with forecaster names, these names will be
        used to construct new features column names.
        The pattern for new feature names is: 
        `<column name>_<forecaster name>`, where `<column>` is the column
        that forecast feature will be made from. 
        When a forecaster name is not supplied, a name will be constructed
        from the forecaster subclass type.

    :type forecaster_list:
        :class:`~ftk.models.recursive_forecaster.RecursiveForecaster`,
        list,
        list of tuples

    :param max_horizon:
        How many steps ahead should the series be featurized.
        This must be either a dict of integers with keys being grains of a 
        TimeSeriesDataFrame that will be transformed, or a single integer value
        >= 1 applied to all grains.
        If the input to `fit` already has origin times set, the maximum 
        horizons will be detected from the input. In that case, the
        `max_horizon` input will be ignored.
    :type max_horizon: dict of integers or single integer

    :param initial_window:
        How many data points at the beginning of the series should be used for
        initial featurization. Notice that these many data points will be lost.
        This must be either a dict of integers with keys being grains of a 
        TimeSeriesDataFrame that will be transformed, or a single integer 
        value applied to all grains.
        If no value(s) are provided for `initial_window`, the transform will
        attempt to infer sensible values based on the detected seasonalities
        of the time series in an input data frame. The default is currently:
        2 * seasonality + 1.
    :type initial_window: dict of integers or single integer

    :param expanding:
        Should subsequent forecasts be constructed over a rolling (if False)
        or an expanding (if True) window. Example: 
        * Consider a 5-point time series `[1, 2, 3, 4, 5]`, 
            a `Naive` forecaster and an `initial_window` of `3`. 
        * Then with `expanding=True`, first naive forecast will be 
            calculated over the window `[1, 2, 3]`, second - over the window
            `[1, 2, 3, 4]`, and last - over the window `[1, 2, 3, 4, 5]`.
        * Whereas with `expaninding=False`, first naive forecast will be 
            calculated over the window `[1, 2, 3]`, second - over the window
            `[2, 3, 4]`, and last - over the window `[3, 4, 5]`.
        Defaults to `True`. Switching to `False` can speed up computations.
    :type expanding: bool
    
    :param overwrite_columns: 
        Flag that permits the transform to overwrite existing columns in the 
        input TimeSeriesDataFrame for features that are already present in it. 
        If True, prints a warning and overwrites columns.
        If False, throws a RuntimeError. 
        Defaults to False to protect user data.
    :type overwrite_columns: bool

    :param column: 
        Name of column in an input data frame to generate features from.
        If this parameter is not provided, the transform will default to
        the `ts_value_colname` of an input data frame.
    :type column: str

    :param dropna: 
        This transform introduces NA values to a transformed data frame
        due to its initial window and also the possibility that the input
        frame contains dates that are past the forecast feature horizon.
        If the `dropna` parameter is True, those rows where NA values
        are in the forecast feature column(s) will be removed. 
        If this transform is part of a pipeline, the recommended action
        is to set this parameter to False and drop NA values after all
        transform steps have been run, prior to an estimation step.
    :type dropna: bool
    """
    ###########################################################################
    ### Checking sanity of inputs
    ###########################################################################

    MINIMUM_WINDOW_SIZE = 5

    @property
    def forecaster_list(self):
        """
        List of name, forecast pairs.
        See `forecaster_list` parameter.
        """
        return self._forecaster_list

    @forecaster_list.setter
    def forecaster_list(self, val):

        if is_iterable_but_not_string(val):
            types = [type(m) for m in val]

            if all(issubclass(t, RecursiveForecaster) for t in types):
                names = [type(m).__name__ for  m in val]
                fcasters = val

            elif all(issubclass(t, tuple) for t in types):
                names, fcasters = zip(*val)
                names = list(names)
                improper_types = [type(m) for m in fcasters
                                  if not isinstance(m, RecursiveForecaster)]
                if len(improper_types) > 0:
                    raise TransformTypeException(
                        (type(self).__name__ + ': ' +
                        'All forecasters must be of type ' +
                        'RecursiveForecaster. The following unsupported ' +
                        'input types were given: {0}').format(improper_types))

            else:
                raise TransformTypeException(
                    (type(self).__name__ + ': ' +
                     'List input can be a list of RecursiveForecasters ' +
                     'or a list of (name, RecursiveForecaster) tuples. ' +
                     'The following input types were given: {0}').format(types))

            clean_names = make_repeated_list_strings_unique(names)
            self._forecaster_list = \
                [(nm, clone(mod)) 
                 for nm, mod in zip(clean_names, fcasters)]
            
        else:
            if isinstance(val, RecursiveForecaster):
                self._forecaster_list = [(type(val).__name__, clone(val))]
            else:
                raise TransformTypeException(
                    (type(self).__name__ + ': ' +
                     '`forecaster_list` input can be a RecursiveForecaster, ' +
                     'a list of RecursiveForecasters, or a list of ' +
                     '(name, RecursiveForecaster) tuples.' +
                     'The following type was given: {0}')
                    .format(type(val)))

    @property
    def column(self):
        """
        Name of column to create forecast features from.
        """
        return self._column

    @column.setter
    def column(self, value):
        if isinstance(value, str) or (value is None):
            self._column = value
        else:
            raise TransformTypeException(
                '`column` parameter must a string or None.')

    @property
    def overwrite_columns(self):
        """
        See `overwrite_columns` parameter
        """
        return self._overwrite_columns

    @overwrite_columns.setter
    def overwrite_columns(self, value):
        if not isinstance(value, bool):
            error_message = \
                ("Input 'overwrite_column' must be True or " +
                 "False, instead received {}".format(value))
            raise TransformTypeException(error_message)
        self._overwrite_columns = value

    def _check_inputs(self, X, column, 
                      max_horizon, initial_window, expanding,
                      overwrite_columns):
        """Sanity checks for major input parameters:
            1) X must be a TimeSeriesDataFrame
            2) column must be a valid column name in X
            3) max_horizon must be a dict of ints >= 1 or an int >= 1
            4) initial_window must be a dict of ints >= 3 or an int >= 3
            5) expanding must be a bool, i.e. True or False
            6) overwrite_columns must be a bool, i.e. True or False
        """
        if not isinstance(X, TimeSeriesDataFrame):
            raise NotTimeSeriesDataFrameException(
                Messages.INPUT_IS_NOT_TIMESERIESDATAFRAME)

        if column not in X.columns:
            raise TransformException(
                (type(self).__name__ + ': Input for `column` parameter ' +
                'is not a valid data frame column. `column` value: {0}.')
                .format(column))
        
        self.verify_max_horizon_input(max_horizon)
        grains_of_X = set(X.grain_index)
        if isinstance(max_horizon, dict):
            missing_grains = [gr for gr in max_horizon
                              if gr not in grains_of_X]
            if len(missing_grains) > 0:
                raise TransformValueException(
                    ('max_horizon grains {0} ' +
                     'are not present in the input data frame')
                    .format(missing_grains))
  
        check_type_collection_or_dict(initial_window, is_int_like, grains_of_X,
                                      is_large_enough, min_value=3)

        # check if initial_window is longer than series:
        if isinstance(initial_window, dict):
            nrows_p_grain = X.groupby_grain().size().to_dict()
            for grain, init_window in initial_window.items():
                if init_window > nrows_p_grain[grain]:
                    error_message = \
                        (type(self).__name__ + ': '
                         "When `initial_window` is a `dict`, " +
                         "none of its values should exceed the number of " +
                         "rows in the TimeSeriesDataFrame available per " +
                         "grain. Not true for grain {0}, ".format(grain) +
                         "initial_window is {}, ".format(init_window) +
                         "number of rows is {}.".format(nrows_p_grain[grain]))
                    raise TransformValueException(error_message)
        else:
            min_series_len = X.groupby_grain().size().min()
            if initial_window > min_series_len:
                raise TransformValueException(
                    (type(self).__name__ + ': ' +
                     'Initial window is longer than the shortest series ' +
                     'in the input. Initial window: {0}. Shortest series ' +
                     'length: {1}').format(initial_window, min_series_len))

        istype(expanding, bool)
        istype(overwrite_columns, bool)

    ###########################################################################
    ### Internal methods with implementation details
    ###########################################################################

    def preview_feature_names(self, X):
        """
        Preview the forecast feature column names
        that would be made in a data frame.

        :param X: Input data frame
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`

        :return: List of forecast feature names
        :rtype: list of str
        """
        # if users have the same model more than once, want to avoid 
        # ambiguous feature names, use a utility funciton to clean this up
        names, _ = zip(*self.forecaster_list)

        fcast_colname = self.column if self.column is not None \
            else X.ts_value_colname

        return [fcast_colname + '_' + modname
                for modname in names]

    def preview_origin_time_colname(self, X):
        """
        Preview the origin time column name
        that would be made in a data frame.

        :param X: Input data frame
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`

        :return: Origin time column name
        :rtype: str
        """
        if X.origin_time_colname is None:
            origin_time_colname = self.origin_time_colname
        else:
            origin_time_colname = X.origin_time_colname

        return origin_time_colname

    def _infer_initial_window(self, X, minimum_size=MINIMUM_WINDOW_SIZE):
        """
        Infer a reasonable initial window size, e.g. when one is not provided
        as input. 

        This method attempts to detect seasonalities for all time series 
        (grains) in X and then sets the initial window (by grain) to:
        2*seasonality + 1. If this value is less than the minimum_size,
        the minimum size is used instead.
        If there is no seasonality inferred for a given grain in X,
        the minimum_size is used.
        """
        seasonality_list_by_grain = \
            invert_dict_of_lists(X.get_seasonality_dict())

        self.initial_window = {}
        X_grouped = X.groupby_grain()
        for gr in X_grouped.groups:
            if gr not in seasonality_list_by_grain:
                window_sz = minimum_size
                warn((type(self).__name__ + ': No seasonality inferred ' +
                     'for grain {0}. Defaulting to initial window of {1} ' +
                     'periods.')
                     .format(gr, default_size), UserWarning)
            else:
                seasonality = seasonality_list_by_grain[gr][0]
                window_sz = 2 * seasonality + 1

            # Set the initial window; threshold on the minimum window size  
            self.initial_window[gr] = window_sz if window_sz > minimum_size \
                else minimum_size

    def _check_transform_horizons(self, X):
        """
        Check if X has rows past the forecasting range
        determined in fit. If so, NA entries will
        be created in the transformed data frame.
        
        The user will be warned if missing values
        are created due to the above condition.
        """

        if X.grain_colnames is not None:
            # First get latest origin dates by grain for the features
            #  made by the fit method
            fcast_features_grouped = \
                self._forecast_features_df.groupby(
                    level=X.grain_colnames,
                    group_keys=True)
            latest_feature_origins_df = \
                (fcast_features_grouped.apply(
                    lambda Xgr: 
                    Xgr.index
                    .get_level_values(X.origin_time_colname).max())
                 .to_frame(name='origin'))

            # Second, get the latest dates by grain in the transform data
            X_grouped = X.groupby_grain(group_keys=True)
            latest_transform_dates_df = \
                (X_grouped.apply(
                    lambda Xgr: Xgr.time_index.max())
                 .to_frame(name='transform_date'))
       
            # Join the frames so we can line up the origin dates
            #  and the transform dates by grain
            horizon_summary_df = latest_transform_dates_df.merge(
                latest_feature_origins_df, how='inner',
                left_index=True, right_index=True)

        else:
            # No grain set, make a one row data frame
            horizon_summary_df = pd.DataFrame({
                'origin': (self._forecast_features_df
                           .index.get_level_values(X.origin_time_colname)
                           .max()),
                'transform_date': X.time_index.max()},
                 index=[0])
        
        # Compute the transform horizons with respect to the
        #  latest origin dates from the forecast features
        transform_horizons = \
            get_period_offsets_from_dates(
                pd.DatetimeIndex(horizon_summary_df.origin),
                pd.DatetimeIndex(horizon_summary_df.transform_date),
                self._ts_freq)
        horizon_summary_df['transform_horizon'] = transform_horizons

        # Add the fit horizons to the summary data frame
        horizon_summary_df['fit_horizon'] = \
            [self.max_horizon_from_key_safe(gr, self.max_horizon)
             for gr in horizon_summary_df.index]
        
        # Select rows in the summary data frame where the
        #  fit horizon is less than the transform horizon
        # These rows correspond to grains which will have
        #  missing values in the transformed data.
        short_grain_sel = horizon_summary_df.fit_horizon < \
            horizon_summary_df.transform_horizon
        short_grain_df = horizon_summary_df[short_grain_sel]
        
        # If there are any grains meeting the criteria, warn the user
        #  and suggest a bigger max_horizon 
        if len(short_grain_df) > 0:
            warn((type(self).__name__ + '.transform: ' +
                 'Input data contains dates that are past the maximum ' +
                 'horizon of the forecast produced by `fit`. ' +
                 'Affected rows will have missing values in the forecast ' +
                 'feature column(s). Re-fit with max_horizon set to ' +
                 'at least {0} to get forecast features at these dates. ' +
                 'Affected grains: {1}')
                 .format(horizon_summary_df.transform_horizon.max(),
                         short_grain_df.index.values))
        
    def __init__(self, forecaster_list, column=None, max_horizon=None, 
                 initial_window=None,
                 expanding=True, overwrite_columns=False, dropna=False,
                 origin_time_colname=ORIGIN_TIME_COLNAME_DEFAULT, 
                 **kwargs):
       
        super().__init__(**kwargs)

        self.column = column
        self.forecaster_list = forecaster_list
        self.max_horizon = 1 if max_horizon is None else max_horizon
        self.initial_window = initial_window
        self.expanding = expanding
        self.overwrite_columns = overwrite_columns
        self.dropna = dropna
        self.origin_time_colname = origin_time_colname

        # init cache and fit statuses
        self._is_fit = False
        self._ts_freq = None
        self._X_cache = None

    # Private helper methods for 'fit'
    # ------------------------------------------------------------------------- 
    def _get_training_window_from_cache(self, window):
        """
        Get the training data for the window defined by
        the position 'window'. 
        """
   
        # Internal function for extracting the current window
        #  rows for a single grain
        def get_current_window_single_grain(gr, Xgr, t):

            window_start = 0 if self.expanding else t
            window_end = t + self._init_window_dict[gr]
            
            return Xgr.iloc[window_start:window_end, :]
        # ----------------------------------------------

        active_grains = [gr for gr, stop_pos in 
                         self._last_window_pos.items()
                         if window < stop_pos]

        # Extract active grain rows within the window
        train_window_tsdf = pd.concat([
            get_current_window_single_grain(gr, Xgr, window)
            for gr, Xgr in self._X_cache.groupby_grain()
            if gr in active_grains])

        return train_window_tsdf

    def _make_forecasts_one_window(self, window, X_dummy, **fit_params):
        """
        Make forecasts for a single window of data. 
        
        The X_dummy argument is needed to conform to the "worker method" 
        signature required by ComputeStrategyMixin, but its contents
        are ignored in favor of the cached version of the training data.
        """
        # Get the current window from the cached training data
        Xw = self._get_training_window_from_cache(window)

        # Internal function for fitting/forecasting from a single model
        def fit_forecast_one_model(model):
            fit_model = model.fit(Xw, **fit_params)

            # Use RecursiveForecaster's internal forecasting method
            #   to generate max_horizon forecasts. 
            # Calling `predict` is overkill/clumsy here since we don't need a
            #   ForecastDataFrame output or distribution forecasts.
            fcast_df = fit_model._make_forecast(Xw, self.max_horizon,
                                                make_dist_fcast=False)

            # If origin times aren't in the index, add them;
            # Otherwise origins will be duplicated on join/concat 
            origin_name = model.preview_origin_time_colname(Xw)
            if origin_name not in fcast_df.index.names:
                fcast_df.set_index(origin_name,
                                   append=True, inplace=True)

            return fcast_df
        # -------------------------------------------------------------
        
        forecasts_for_window = \
            pd.concat([fit_forecast_one_model(clone(mod))
                       for _, mod in self.forecaster_list], 
                      axis=1)

        return forecasts_for_window
    # -------------------------------------------------------------------------
    @loggable
    def fit(self, X, y=None, **fit_params):
        """
        Fit RecursiveForecast models for each position of the expanding/rolling
        window and store generated forecasts. 

        :param X: Input data
        :type X: :class:`ftk.dateframets.TimeSeriesDataFrame`

        :param y: Ignored. Included for pipeline compatibility

        :return: Fitted transform
        :rtype: RecursiveTimeSeriesFeaturizer
        """
      
       # Setup models
        feature_names = self.preview_feature_names(X)
        for (_, m), feature_name in zip(self.forecaster_list, feature_names):
            m.pred_point_colname = feature_name
            m.origin_time_colname = self.preview_origin_time_colname(X)
        
        self._ts_freq = X.infer_freq()

        # If X has origin times already, detect the max_horizons 
        #  implied by them
        if X.origin_time_colname is not None:     
            max_horizon = \
                self.detect_max_horizons_by_grain(X, freq=self._ts_freq)

            if isinstance(max_horizon, dict):
                h_max = max(max_horizon.values())
            else:
                h_max = max_horizon

            warn((type(self).__name__ + '.fit: ' +
                 'Origin times were previously set in the input data frame, ' +
                 'so the maximum horizons will be inferred from ' +
                 'the existing origin times and the `max_horizon` input ' +
                 'to this transform will be ignored. ' +
                 'Inferred maximum horizon: {0}').format(h_max),
                 UserWarning)

            self.max_horizon = max_horizon

        if self.column is None:
            self.column = X.ts_value_colname

        # Get a data dependent guess for the initial window if it isn't set
        if self.initial_window is None:
            self._infer_initial_window(X)

        self._check_inputs(X, self.column, 
                           self.max_horizon,
                           self.initial_window, self.expanding, 
                           self.overwrite_columns)

        # Extract the series formed by self.column and
        #  sort it by time
        X_series_df = X._extract_time_series(self.column)
        X_series_df.sort_index(level=X.time_colname, inplace=True)

        # Re-constitute a TSDF from the series
        #  with no origin times and ts_value set to self.column
        ctr_args = {k: getattr(X, k) for k in X._metadata}
        ctr_args['origin_time_colname'] = None
        ctr_args['ts_value_colname'] = self.column
        X_series_tsdf = TimeSeriesDataFrame(X_series_df, 
                                            copy=False, **ctr_args)

        X_series_grouped = X_series_tsdf.groupby_grain()
        
        # To simplify downstream logic, make sure initial_window is a dict
        if isinstance(self.initial_window, dict):
            self._init_window_dict = self.initial_window
        else:
            self._init_window_dict = {gr: self.initial_window 
                                      for gr in X_series_grouped.groups}
        
        # Figure out where the windows should stop for each grain
        self._last_window_pos = {gr: len(Xgr) - self._init_window_dict[gr] + 1 
                                 for gr, Xgr in X_series_grouped}
        max_window_pos = max(self._last_window_pos.values())

        # Make an interator for looping over window positions.
        # The compute strategy expects an iterator over a tuple
        #  of (position/level, data frame) - since we cache
        #  the whole data frame in the object state, just return a
        #  dummy for the data frame in the iterator 
        window_iter = product(range(max_window_pos), [None])

        if self.compute_strategy is None:
            # Serial fit. Iterate over windows
            self._X_cache = X_series_tsdf
            forecasts_all_windows = \
                [self._make_forecasts_one_window(w, Xw, **fit_params)
                 for w, Xw in window_iter]
        else:
            # Do a parallel fit over window positions
            # Cache needs to be a copy (as opposed to a reference)
            #  in this case since it will be distributed to all workers
            self._X_cache = X_series_tsdf.copy()
            self.execute_job(self._make_forecasts_one_window, 
                             window_iter, 
                             lambda x: None, 
                             ComputeJobType.Fit, 
                             **fit_params)
            # Check for errors 
            if len(self.compute_strategy.errors) > 0:
                raise self.compute_strategy.errors[0]

            # Retrieve results from the compute object
            forecasts_all_windows = self.compute_strategy.job_results

        # Concat all window forecasts together
        # The resulting object is a pandas DataFrame
        self._forecast_features_df = \
           pd.concat(forecasts_all_windows)

        self._is_fit = True

        return self

    @loggable
    def transform(self, X):
        """
        Use stored forecasts from `fit()` to generate forecast features
        for the input data frame.

        Rows in X that don't have a corresponding forecast from the `fit`
        procedure will have NA values in the forecast feature columns.
        This includes the initial window period and any other rows
        with datetimes that don't match those for generated forecasts.

        If the transform frame, X, contains datetimes past the maximum
        horizon of the forecast features, this method prints a warning 
        messages and suggests a larger `max_horizon` input.

        :param X: Input data
        :type X: :class:`ftk.dateframets.TimeSeriesDataFrame`

        :return: Data frame with forecast feature column(s)
        :rtype: :class:`ftk.dateframets.TimeSeriesDataFrame`
        """
       
        if not self._is_fit:
            error_message = \
                (type(self).__name__ + 
                 ' fit must be called before transform')
            raise TransformException(error_message)

        # Check if we'll overwrite any columns
        feature_cols = self._forecast_features_df.columns
        dup_cols_set = set(feature_cols).intersection(set(X.columns))
        if len(dup_cols_set) > 0:
            if self.overwrite_columns:
                warn((type(self).__name__ + 
                     '.transform: Some existing columns in the input ' +
                     'data frame will be overwritten. Affected columns: {0}')
                    .format(dup_cols_set), UserWarning)
                X = X.drop(labels=list(dup_cols_set), axis=1)
            else:  
                raise TransformException(
                    (type(self).__name__ + 
                     '.transform: Overwrite of existing columns ' +
                     'is not allowed. Affected columns: {0}')
                    .format(dup_cols_set))
                           

       # If X doesn't have origin times, add them
        if X.origin_time_colname is None:
            X = self.create_origin_times(
                X, self.max_horizon, 
                freq=self._ts_freq,
                origin_time_colname=self.origin_time_colname)
      
        # Check for transform horizons past the forecast horizons
        #  used in the `fit` step.
        self._check_transform_horizons(X)

        # Join input with the forecast features
        X_trans = X.merge(self._forecast_features_df, how='left',
                          left_index=True, right_index=True)

        if self.dropna:
            notnull_by_column = X_trans[feature_cols].notnull().values
            not_null_all_cols = np.apply_along_axis(all, 1, notnull_by_column)
            X_trans = X_trans[not_null_all_cols]

        # Warn if X_trans is empty
        if len(X_trans) == 0:
            warn(type(self).__name__ + '.transform: ' +
                 'Transformed data frame is empty.', UserWarning)

        return X_trans
