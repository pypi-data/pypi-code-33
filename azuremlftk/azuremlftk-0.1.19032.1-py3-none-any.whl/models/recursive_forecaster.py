from __future__ import generators
from abc import ABCMeta, abstractmethod
from warnings import warn
import numpy as np
import pandas as pd


from ftk import verify
from ftk.time_series_data_frame import TimeSeriesDataFrame
from ftk.forecast_data_frame import ForecastDataFrame
from ftk.base_estimator import AzureMLForecastEstimatorBase, loggable
from ftk.exception import (EstimatorTypeException, EstimatorValueException,
                           DatetimeConversionException, DataFrameTypeException,
                           DataFrameValueException, DataFrameProcessingException,
                           ComputeTypeException)
from ftk.factor_types import ComputeJobType
from ftk.compute import ComputeStrategyMixin

from ftk.utils import (convert_to_list, grain_level_to_dict,
                       get_period_offsets_from_dates)
from ftk.ts_utils import detect_seasonality
from ftk.constants import *

class RecursiveForecaster(ComputeStrategyMixin,
                          AzureMLForecastEstimatorBase,
                          metaclass=ABCMeta):
    """
    .. _pd.DateOffset: https://pandas.pydata.org/pandas-docs/stable/
                        timeseries.html#offset-aliases

    Abstract base class for a recursive, univariate forecaster.
    This class implements scikit-learn style fit/predict methods on
    TimeSeriesDataFrame objects. Specific modeling code is in derived classes
    that implement training and forecasting methods on single time series.

    Derived classes must implement three private methods:
    `_single_series_train`, `_single_series_point_forecast`, and
    `_single_series_distribution_forecast`. See the method docstrings for
    requirements.

    :param freq: 
        Frequency of the time series to fit represented as a pandas offset 
        alias string or pd.DateOffset_ object.
        If not set, fit will try to infer the frequency from the input
        data frame.
    :type freq: str, pd.DateOffset_

    :param seasonality: 
        Seasonality of time series represented as an integer
        number of periods. 

        The user can set the seasonality, prior to fitting,
        as a dictionary where the keys are grain levels identifying individual 
        time series - or as a single integer representing a constant seasonality
        across all series in an input TimeSeriesDataFrame.

        The value of the seasonality parameter after fit has been called is
        a dictionary of integer seasonalities where the keys are the grain 
        levels associated with the time series in the training data.

        The _single_series_get_seasonality method can be used during training
        to optionally detect seasonality using the .NET time series utility
        assembly.
    :type seasonality: int, dict

    :param pred_point_colname: 
        Column name for point forecasts when the input to `predict` is a
        :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`.
        A default name will be used if this property is set to `None`.
        When `predict` input is a :class:`ftk.forecast_data_frame.ForecastDataFrame`,
        this property is ignored.
    :type pred_point_colname: str

    :param pred_dist_colname: 
        Column name for distribution forecasts when the input to `predict` is a
        :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`.
        A default name will be used if this property is set to `None`.
        When `predict` input is a :class:`ftk.forecast_data_frame.ForecastDataFrame`,
        this property is ignored.
    :type pred_point_colname: str

    :param origin_time_colname: 
        Column name for forecast origin datetimes when the input to `predict`
        doesn't have `origin_time_colname` set. 
        A default name will be used if this property is set to `None`.
        This property is ignored if the input to `predict`
        already has `origin_time_colname` set.
    :type origin_time_colname: str

    """

    @classmethod
    def identity_grain_level(cls):
        """
        Identifier for grain when an input data frame doesn't
        have grain_colnames specified
        """
        return TimeSeriesDataFrame.identity_grain_level()

    # Expose _can_use_dotnet to derived classes
    @classmethod
    def can_use_dotnet(cls):
        """
        Is the .NET library for ETS and seasonality detection available?
        In order for this library to import, the python env must include
        the pythonnet package and the .NET DLL must exist in 
        `$ROOT$\lib\ftk\dotnet\Microsoft.AzureML.Forecasting.dll`. 

        :return: True if .NET library can be imported
        :rtype: boolean
        """
        return _can_use_dotnet

    def __init__(self, freq=None, seasonality=None,
                 pred_point_colname=None,
                 pred_dist_colname=None,
                 origin_time_colname=None):

        self._default_pred_point_colname = \
            UNIFORM_PRED_POINT_COLNAME
        self._default_pred_dist_colname = \
            UNIFORM_PRED_DIST_COLNAME
        self._default_origin_time_colname = ORIGIN_TIME_COLNAME_DEFAULT

        self._models = dict()
        self._last_observation_dates = dict()
        self._first_observation_dates = dict()
        self._grain_levels = None
        self._is_fit = False

        self.freq = freq
        self.seasonality = seasonality
        self.pred_point_colname = pred_point_colname
        self.pred_dist_colname = pred_dist_colname
        self.origin_time_colname = origin_time_colname

    @property
    def is_fit(self):
        """
        True if the 'fit' method has been called and
        completed successfully.
        """
        return self._is_fit

    @property
    def freq(self):
        """
        Time series frequency as a pandas.DateOffset object.

        """
        return self._freq

    @freq.setter
    def freq(self, val):
        if isinstance(val, str) and len(val) == 0:
            self._freq = None
        elif isinstance(val, str):
            self._freq = pd.tseries.frequencies.to_offset(val)
        elif isinstance(val, pd.DateOffset) or val is None:
            self._freq = val
        else:
            raise EstimatorTypeException(
                'RecursiveForecaster: ' +
                'Frequency must be given by a string ' +
                'or DateOffset object.')

    @property
    def seasonality(self):
        """
        Seasonality of time series in the RecursiveForecaster models.

        This property can be set manually prior to calling fit.
        If not set, derived models can detect the seasonality.

        After the model is fit, the seasonality is read-only,
        See the `seasonality` parameter of RecursiveForecaster
        for more information.
        """
        if self._is_fit:
            return self._seasonality_output
        else:
            return self._seasonality_input

    @seasonality.setter
    def seasonality(self, val):
        if self._is_fit:
            # Seasonality is read-only after fit is called.
            raise EstimatorValueException(
                'RecursiveForecaster.seasonality: ' +
                'Cannot set seasonality on a fit model')

        if val is None:
            self._seasonality_input = None
        elif isinstance(val, int) and val > 0:
            # Use a constant seasonality across all series
            self._seasonality_input = val
        elif isinstance(val, dict):
            # Set seasonalities by individual time series
            # Make sure each entry in the dict is a valid seasonality
            if not all((isinstance(seas, int) and seas > 0)
                       for lvl, seas in val):
                raise EstimatorTypeException(
                    'RecursiveForecaster.seasonality: ' +
                    'Seasonality must be represented by an integer ' +
                    'greater than zero.')

            self._seasonality_input = val
        else:
            raise EstimatorTypeException(
                'RecursiveForecaster.seasonality: ' +
                'Seasonality must be represented by an integer ' +
                'greater than zero ' +
                'or a dictionary of integers greater than zero.')

        # Initialize the output. We'll fill this dictionary during fit
        self._seasonality_output = dict()

    @property
    def pred_point_colname(self):
        """
        Column name for point forecasts when the input to `predict` is a
        :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`.
        """
        return self._pred_point_colname

    @pred_point_colname.setter
    def pred_point_colname(self, value):
        if value is None:
            self._pred_point_colname = \
                self._default_pred_point_colname
        elif isinstance(value, str):
            self._pred_point_colname = value
        else:
            raise EstimatorTypeException(
                ('Unsupported type given for pred_point_colname: {0}. '
                 + 'It should be a string.')
                .format(type(value)))

    @property
    def pred_dist_colname(self):
        """
        Column name for distribution forecasts when the input to `predict` is a
        :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`.
        """
        return self._pred_dist_colname

    @pred_dist_colname.setter
    def pred_dist_colname(self, value):
        if value is None:
            self._pred_dist_colname = \
                self._default_pred_dist_colname
        elif isinstance(value, str):
            self._pred_dist_colname = value
        else:
            raise EstimatorTypeException(
                ('Unsupported type given for pred_dist_colname: {0}. '
                 + 'It should be a string.')
                .format(type(value)))

    @property
    def origin_time_colname(self):
        """
        Column name for forecast origin datetimes when the input to `predict`
        doesn't have `origin_time_colname` set. 
        """
        return self._origin_time_colname

    @origin_time_colname.setter
    def origin_time_colname(self, value):
        if value is None:
            self._origin_time_colname = \
                self._default_origin_time_colname
        elif isinstance(value, str):
            self._origin_time_colname = value
        else:
            raise EstimatorTypeException(
                ('Unsupported type given for origin_time_colname: {0}. '
                 + 'It should be a string.')
                .format(type(value)))

    def preview_pred_names(self, X):
        """
        Preview the prediction column names
        that would be made in the input data frame.

        :param X: Input data frame
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`, :class:`ftk.forecast_data_frame.ForecastDataFrame`

        :return: 
            Point forecast and distribution column names
        :rtype: tuple
        """
        if isinstance(X, TimeSeriesDataFrame) and \
                not isinstance(X, ForecastDataFrame):
            point_name = self._pred_point_colname
            distr_name = self._pred_dist_colname
        elif isinstance(X, ForecastDataFrame):
            point_name = X.pred_point
            distr_name = X.pred_dist
        else:
            raise DataFrameTypeException('Unrecognized data frame format')

        return point_name, distr_name

    def preview_origin_time_colname(self, X):
        """
        Preview the origin time column name
        that would be made in a data frame.

        :param X: Input data frame
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`, :class:`ftk.forecast_data_frame.ForecastDataFrame`

        :return: Origin time column name
        :rtype: str
        """
        if X.origin_time_colname is None:
            origin_time_colname = self._origin_time_colname
        else:
            origin_time_colname = X.origin_time_colname

        return origin_time_colname

    @abstractmethod
    def _single_series_train(self, series_values, grain_level, **fit_params):
        """
        Absract method for training a model on a single time series.

        :param series_values: 
            1-D array of time series values sorted by ascending time.
        :type series_values: numpy.ndarray

        :param grain_level: 
            Identifies the series by its grain group in a TimeSeriesDataFrame.
            In practice, it is an element of X.groupby_grain().groups.keys(). 
            Implementers can use the grain_level to store time series specific 
            state needed for training or forecasting. 
            See ets.py for examples.
        :type grain_level: str, tuple of str

        :Returns:
            an object representation of a model. There are no interface
            requirements on the model object; this base class simply stores the
            model returned from this function and passes it to
            _single_series_point_forecast and _single_series_distribution_forecast
            when the predict method is called. It is up to the implementer to
            define their own internally consistent interface.

        """
        pass

    @abstractmethod
    def _single_series_point_forecast(self, model, max_horizon, grain_level):
        """
        Produce point forecasts up to max_horizon from a model.

        :param model: is an object representation of a model. It is the
            object returned by the _single_series_train method.

        :param max_horizon: is an integer representing the maximum forecast
            horizon.

        :param grain_level: is an object that identifies the series by its
            grain group in a TimeSeriesDataFrame. In practice, it is an element
            of X.groupby_grain().groups.keys(). Implementers can use
            the grain_level to store time series specific state needed for
            training or forecasting. See ets.py for examples.

        :Returns: a 1-D numpy array of point forecasts up to and including max horizon.
          The k-th entry in this array is assumed to be the forecast at horizon k+1.

        """
        pass

    @abstractmethod
    def _single_series_distribution_forecast(self, model, max_horizon, grain_level):
        """
        Produce distribution forecasts up to max_horizon from a model.

        :param model:
            is an object representation of a model. It is the object
            returned by the _single_series_train method.

        :param max_horizon: is an integer representing the maximum forecast horizon.

        :param grain_level:
            is an object that identifies the series by its
            grain group in a TimeSeriesDataFrame. In practice, it is an
            element of  X.groupby_grain().groups.keys(). Implementers
            can use the grain_level to store time series specific state needed
            for training or forecasting. See ets.py for examples.

        :Returns:
            a 1-D numpy array of distribution forecasts up to and
            including max horizon. The k-th entry in this array is assumed
            to be the forecast distribution at horizon k+1.
            Distributions in this array can have any type representing a
            probability distribution, e.g. scipy.stats.distributions.rv_frozen.

        """
        pass

    @abstractmethod
    def _return_fitted_values(self, model, grain_level):
        """
        Returns the fitted values from a model.

        :param model: 
            is an object representation of a model. It is the
            object returned by the _single_series_train method.

        :param grain_level: 
            is an object that identifies the series by its
            grain group in a TimeSeriesDataFrame. In practice, it is an element
            of X.groupby_grain().groups.keys(). Implementers can use
            the grain_level to store time series specific state needed for
            training or forecasting. See ets.py for examples.

        :Returns:
            a 1-D numpy array of fitted values for the training data. The data are
            assumed to be in chronological order
        """
        pass

    def fitted(self, X):
        """
        Returns the fitted values from a the RecursiveForecaster model.

        :param X: 
            A TimeSeriesDataFrame defining the data for which fitted values 
            are desired.  Inputting the same data used to fit the model will 
            return all fitted data.
        :type X: TimeSeriesDataFrame

        :Returns:
            a ForecastDataFrame containing the fitted values in `pred_point`.
        """

        self._check_dataframe(X, 'predict')

        point_name, _ = self.preview_pred_names(X)
        origin_name = self.preview_origin_time_colname(X)
        ctr_args = {k: getattr(X, k) for k in X._metadata}
        ctr_args['origin_time_colname'] = origin_name
        ctr_args['pred_point'] = point_name
        if 'ts_value_colname' in ctr_args:
            ctr_args['actual'] = ctr_args.pop('ts_value_colname')

        fitted_df = pd.DataFrame()
        for g, X_grain in X.groupby_grain():
            origin_time = self._last_observation_dates[g]
            time_values = pd.date_range(self._first_observation_dates[g],
                                        origin_time,
                                        freq=self.freq)
            fitted = self._return_fitted_values(self._models[g], g)
            fitted = pd.Series(fitted, index=time_values)
            assign_dict = {origin_name: origin_time,
                           point_name: fitted[X_grain.time_index].values}
            X_grain = X_grain.assign(**assign_dict)

            fitted_df = pd.concat([fitted_df, X_grain])

        fitted_df = fitted_df.loc[X.index, :]

        fitted_df = ForecastDataFrame(fitted_df, **ctr_args)
        return fitted_df

    def _single_series_get_seasonality(self, series_values, grain_level):
        """
        Get the seasonality for a single series.

        If the seasonality is not set by the user, try to detect it
        automatically.

        This is an optional utility function that derived classes can call
        during the fitting procedure, e.g. from _single_series_train

        :returns: an integer seasonality.

        """

        if self._seasonality_input is None \
           or (isinstance(self._seasonality_input, dict)
               and grain_level not in self._seasonality_input):

            # User didn't specify the seasonality. Try to detect it
            seasonality_series = detect_seasonality(series_values)
           
        elif isinstance(self._seasonality_input, dict) \
                and grain_level in self._seasonality_input:

            # User specified the seasonality in a dictionary entry
            seasonality_series = self._seasonality_input[grain_level]

        elif isinstance(self._seasonality_input, int):

            # User specified the seasonality as an integer
            seasonality_series = self._seasonality_input

        else:

            # If we get here, there's nothing constructive to do
            # Just punt and revert to non-seasonal
            warn(('RecursiveForecaster: Seasonality not set or detected '
                  + 'for grain_level {0}. '
                    + 'Setting seasonality to 1.').format(grain_level))
            seasonality_series = 1

        return seasonality_series

    def _multi_series_train(self, data, *args, **fit_params):
        """
        Train model for all available time series in a data frame passed to the fit method.

        This function simply assumes all time-series in the fit method where the imput data-frame
        is passed in will be trained in parallel. If subset of series are desired for parallel training,
        then the input dataframe to the fit method must contain that set.

        **fit_params is the list of fit function params. The asusmption is all series in the dataframe
        will make use of same parameters. Per level fit_params is plain unwieldy and will involve lot of work on the
        caller. Our interface can simply be adapted with a "*maplist_fit_params" which is a map of dictionary values 
        per level.         

        """
        # The data is grouped dataframe currently; the mapper_func is not used.
        self.execute_job(self._execute_single_series_fit,
                         data,
                         self.fit_map_func,
                         ComputeJobType.Fit,
                         *args,
                         **fit_params)
        return self

    def _check_dataframe(self, X, method):
        """
        Make sure input data frames meet some minimum requirements.

        Fit needs a non-empty TimeSeriesDataFrame with a 'value' column
        set. This check also tries to infer the time series frequency if its
        not manually set.

        Predict needs a non-empty TimeSeriesDataFrame

        """

        if len(X) == 0:
            raise DataFrameValueException(
                'RecursiveForecaster.{0}: DataFrame input is empty.'.format(method))

        if method == 'fit':

            if not isinstance(X, TimeSeriesDataFrame):
                raise DataFrameTypeException((
                    'RecursiveForecaster.{0}: ' +
                    'Input should be an instance of TimeSeriesDataFrame.')
                    .format(method))

            if X.ts_value_colname is None:
                raise DataFrameValueException(
                    ('RecursiveForecaster.{0}: ' +
                     'value column not in data frame.')
                    .format(method))

            # Check time series regularity
            # If there are missing values in ts_value or
            #  date gaps, warn the user but try to keep going
            if not X.check_regularity():
                warn(('RecursiveForecaster.{0}: Input data frame has date ' +
                      'gaps or missing values in the {1} column. ' +
                      'Use TimeSeriesDataFrame.check_regularity_by_grain ' +
                      'for a diagnosis of problems. ' +
                      'Also consider using a TimeSeriesImputer transform.')
                     .format(method, X.ts_value_colname),
                     UserWarning)

                # Remove any missing values
                is_missing_target = X[X.ts_value_colname].isnull()
                if is_missing_target.any():
                    warn(('RecursiveForecaster.{0}: Input data frame has ' +
                          'missing values in the {1} column. Removing them ' +
                          'and attempting to fit.')
                         .format(method, X.ts_value_colname),
                         UserWarning)

                    X = X[~is_missing_target]

            if self._freq is None:
                # Try to infer the frequency
                self.freq = X.infer_freq()

        if method == 'predict':
            # Special checks for predictions:
            # Fit must have been called and X must be a TSDF

            if not self.is_fit:
                raise EstimatorValueException(
                    'RecursiveForecaster.predict: ' +
                    'fit must be called before predict')

            if not isinstance(X, TimeSeriesDataFrame):
                raise DataFrameTypeException(
                    ('RecursiveForecaster.{0}: ' +
                     'Input should be an instance of TimeSeriesDataFrame.')
                    .format(method))

    def _find_forecast_horizons(self, X):
        """
        Find maximum horizons to forecast in the prediction frame,
        X. Returns a dictionary, grain -> max horizon.

        Horizons are calculated relative to the latest training
        dates for each grain in X.
        If X has a grain that isn't present in the training data,
        this method returns a zero for that grain.
        """

        # Internal function for getting horizon for a single grain
        def horizon_by_grain(gr, Xgr):
            try:
                horizon = \
                    get_period_offsets_from_dates(
                        self._last_observation_dates[gr],
                        Xgr.time_index,
                        self._freq).max()
            except KeyError:
                horizon = 0

            return horizon
        #------------------------------------------

        if X.grain_colnames is not None:
            fcast_horizon = {gr: horizon_by_grain(gr, Xgr)
                             for gr, Xgr in X.groupby_grain()}
        else:
            id = self.identity_grain_level()
            fcast_horizon = {id: horizon_by_grain(id, X)}

        return fcast_horizon

    def _make_forecast_single_grain(self, grain_level, max_horizon,
                                    time_colname,
                                    grain_colnames,
                                    origin_time_colname,
                                    pred_point_colname,
                                    pred_dist_colname=None):
        """
        Generate forecasts up to max_horizon for a single grain.
        If `pred_dist_colname` is None, only a point forecast will be created.

        Returns a plain pandas Dataframe with the following columns:
        time, grain(s), origin time, point forecast, 
        distribution forecast (optional).  
        """

       # If there's no trained model for this grain
       #  or an invalid max_horizon,
       #  return a single row with NaNs.
       # Downstream processing often depends on
       #  non-empty output for *every* grain,
       #  even if we can't get predictions.
        if grain_level not in self._grain_levels \
                or max_horizon <= 0:

            fcast_dict = {time_colname: pd.NaT,
                          origin_time_colname: pd.NaT,
                          pred_point_colname: np.nan}
            if grain_colnames is not None:
                fcast_dict.update(grain_level_to_dict(grain_colnames,
                                                      grain_level))
            if pred_dist_colname is not None:
                fcast_dict.update({pred_dist_colname: np.NaN})

            if grain_level not in self._grain_levels:
                warn(('RecursiveForecaster: Cannot find a trained model ' +
                      'for grain {0}. Returning empty forecast.')
                     .format(grain_level), UserWarning)

            if max_horizon <= 0:
                warn(('RecursiveForecaster: Requested forecast horizon <=0 ' +
                      'for grain {0}. Returning empty forecast.')
                     .format(grain_level), UserWarning)

            return pd.DataFrame(fcast_dict, index=[0])
        # ---------------------------------------------------------------

        # Origin date/time is the latest training date, by definition
        origin_date = self._last_observation_dates[grain_level]

        # Retrieve the trained model and make a point forecast
        trained_model = self._models[grain_level]
        point_fcast = self._single_series_point_forecast(
            trained_model, max_horizon, grain_level)

        # Construct the time axis that aligns with the forecasts
        fcast_start = origin_date + self._freq
        fcast_dates = pd.date_range(start=fcast_start,
                                    periods=max_horizon,
                                    freq=self._freq)

        # Create the data frame from a dictionary
        fcast_dict = {time_colname: fcast_dates,
                      origin_time_colname: origin_date,
                      pred_point_colname: point_fcast}

        if grain_colnames is not None:
            fcast_dict.update(grain_level_to_dict(grain_colnames,
                                                  grain_level))

        if pred_dist_colname is not None:
            dist_fcast = self._single_series_distribution_forecast(
                trained_model, max_horizon, grain_level)
            fcast_dict.update({pred_dist_colname: dist_fcast})

        return pd.DataFrame(fcast_dict)

    def _make_forecast(self, X, max_horizon, make_dist_fcast=True):
        """
        Generate forecasts up to max_horizon for each grain in X.
        The max_horizon parameter can be a single integer or
        a dictionary mapping each grain in X to an integer.

        Note that this method generates max_horizon forecasts
        regardless of the content of X. The input, X, is used
        only to determine the grains to forecasts and the column
        names to create in the output.

        Returns a pandas DataFrame. The index of this data frame
        will have the same levels as the input, X.
        The ouput will have the following: 
        time, grain(s), origin time, point forecast, 
        distribution forecast (optional; if make_dist_fcast=True). 
        """

        # Get column names from X
        point_name, distr_name = self.preview_pred_names(X)
        origin_time_colname = self.preview_origin_time_colname(X)

        if not make_dist_fcast:
            distr_name = None

        if X.grain_colnames is not None:
            grain_iter = X.groupby_grain().groups.keys()
        else:
            grain_iter = [self.identity_grain_level()]

        # Make sure max_horizon is a dictionary
        if isinstance(max_horizon, int):
            max_horizon = {gr: max_horizon for gr in grain_iter}

        # Make max_horizon forecasts for each grain
        fcast_df = pd.concat([
            self._make_forecast_single_grain(
                gr,
                max_horizon[gr],
                X.time_colname,
                X.grain_colnames,
                origin_time_colname,
                point_name,
                distr_name)
            for gr in grain_iter])

        return fcast_df.set_index(X.index.names)

    @loggable
    def fit(self, X, y=None, **fit_params):
        """
        This method trains recursive models for the target, `ts_value` column. 
        A model is fit for each grain in the input.

        If the input frame has multi-horizon features, this method
        will extract the series corresponding to the time series value
        and use it for training.

        This method can only be called from derived classes that implement
        the time series training methods.

        :param X: 
            Input data frame which will be grouped by its 'grain_colnames'; 
            a model will then be fit for each grain group.
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`

        :param y: Ignored. Included for pipeline compatibility.

        :param **fit_params: 
            Keyword arguments passed on to model training methods
            implemented in derived classes.
        :type **fit_params: dict

        :return: self
        :rtype: RecursiveForecaster
        """

        self._check_dataframe(X, 'fit')

        # Group-by grain - use identity grain if none is set
        if X.grain_colnames is not None:
            X_bygrain = X.groupby_grain()
            self._grain_levels = list(X_bygrain.groups)
        else:
            X_bygrain = {self.identity_grain_level(): X}.items()
            self._grain_levels = [self.identity_grain_level()]

        # Initialize the models and state variables
        self._models = {lvl: None for lvl in self._grain_levels}
        self._last_observation_dates = {
            lvl: None for lvl in self._grain_levels}
        self._first_observation_dates = {
            lvl: None for lvl in self._grain_levels}

        # Train multiple series' in parallel
        if self._compute_strategy is not None:
            # If the mapper function is used, this must be updated to
            # pass the entire data frame. Right now we send the DataFrameGroupBy
            # list
            self._multi_series_train(X_bygrain, X.time_colname, **fit_params)

        # Iterate over grain levels - train a model for each series
        else:
            # Iterate over grain levels - train a model for each series
            for lvl, series_frame in X_bygrain:
                self._execute_single_series_fit(lvl, series_frame,
                                                X.time_colname, **fit_params)

        self._is_fit = True
        return self

    @loggable
    def predict(self, X):
        """
        Make a forecast of the target quantity from previously trained models. 

        To make forecasts, this method groups the input data frame 
        by `grain_colnames` and attempts to lookup a trained model
        for each grain group. If it finds a model for a group, this method 
        will use the model to generate point and distribution forecasts
        (predictions) for each row in the input group data frame.
        Prediction columns will contain missing values if a model cannot
        be found.

        Prediction column names are either set in input metadata 
        (when X is a ForecastDataFrame) or via the `pred_point_colname`
        and `pred_dist_colname` properties of RecursiveForecaster. 
        If these columns exist in X, they will be overwritten in the
        output.

        The output data frame will always have origin times set in its
        index, regardless of whether the input has origin times set. 
        The origin times generated by the forecast are always the latest
        training dates by grain. If the input already has origin times,
        they are respected and copied to the output. 
        However, rows with origin times that don't correspond to a forecast
        origin time will have NA entries in the prediction columns.
        For this reason, it is recommended that the input, X, not contain
        origin times unless the users knows well what they are doing.

        :param X: 
            Input data frame. If X is a ForecastDataFrame, point and
            distribution forecasts are assigned to the 'pred_point' 
            and 'pred_dist' columns set in the frame metadata. 
        :type X:
            :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`,
            :class:`ftk.forecast_data_frame.ForecastDataFrame`

        :return: 
            ForecastDataFrame of the same length as X and 
            with the `pred_point` and `pred_dist` columns filled.
            The output will also contain origin times in the index.

        :rtype: :class:`ftk.dataframeforecast.ForecastDataFrame`

        """
        self._check_dataframe(X, 'predict')

        # Find the maximum horizons dictated by the rows in X
        max_horizons = self._find_forecast_horizons(X)

        # Make a dataframe of forecasts
        fcast_df = self._make_forecast(X, max_horizons, make_dist_fcast=True)

        # Get rows containing in-sample data if any
        in_sample_data = pd.DataFrame()
        for g, X_group in X.groupby_grain():
            if g in self._grain_levels:
                in_sample_data = pd.concat([in_sample_data,
                                            X_group.loc[X_group.time_index <= self._last_observation_dates[g]]])
        # Get fitted results for in-sample data
        if in_sample_data.shape[0] > 0:
            in_sample_fitted = self.fitted(in_sample_data)
            super(TimeSeriesDataFrame, in_sample_fitted).\
                reset_index(
                    level=self.preview_origin_time_colname(X), inplace=True)
            in_sample_fitted = in_sample_fitted.loc[:, fcast_df.columns]
            fcast_df = pd.concat([in_sample_fitted, fcast_df])

        # We're going to join the forecasts to the input - but first:
        # Convert X to a plain data frame and drop the prediction
        #  columns if they already exist
        point_name, distr_name = self.preview_pred_names(X)
        X_df = pd.DataFrame(X, copy=False).drop(
            axis=1,
            labels=[point_name, distr_name],
            errors='ignore')

        # Left join the forecasts into the input;
        #  the join is on the index levels
        pred_df = X_df.merge(fcast_df, how='left',
                             left_index=True, right_index=True)

        # Need to convert the prediction frame into a ForecastDataFrame.
        # First, copy metadata settings from the input
        #   and make sure origin_time_colname is set.
        ctr_args = {k: getattr(X, k) for k in X._metadata}
        ctr_args['origin_time_colname'] = \
            self.preview_origin_time_colname(X)
        if not isinstance(X, ForecastDataFrame):

            # Input is a TSDF so the ctr_args correspond to TSDF metadata.
            # Make the output into a TSDF, then ForecastDataFrame.
            # Set copy=False to try to avoid unnecessary data copying.
            pred_tsdf = TimeSeriesDataFrame(pred_df, copy=False, **ctr_args)
            pred_fcdf = ForecastDataFrame(pred_tsdf, copy=False,
                                          pred_point=point_name,
                                          pred_dist=distr_name)
        else:
            pred_fcdf = ForecastDataFrame(pred_df, copy=False, **ctr_args)

        pred_fcdf._model_class_ = type(self).__name__
        pred_fcdf._param_values_ = self.get_params()

        return pred_fcdf

    def _execute_single_series_fit(self, lvl, series_frame, *args, **fit_params):
        """
        This is a function that trains a single series and will be invoked by parallel train job.
        lvl, series_frame - indicate the grain and the actual series data.
        The args positional argument contains only time_colname value, 
        The fit_params - keyword argument is the fit_params for all series in the dataframe

        """

        time_colname = None
        if args is None:
            raise ComputeTypeException("Exception in execute_single_series_fit. " +
                                       "Expected positional argument not found.")
        else:
            if not len(args) == 1:
                raise ComputeTypeException("Exception in execute_single_series_fit. " +
                                           "Positional argument expects a single argument.")
            else:
                time_colname = args[0]

        # If there's a time index, make sure the values
        # are sorted by ascending time index
        if time_colname is not None:
            series_frame = series_frame.sort_index(level=time_colname,
                                                   ascending=True)

        # Get the series values
        series_values = series_frame.ts_value.values

        # Train a model and store it in the object state
        self._models[lvl] = self._single_series_train(series_values, lvl,
                                                      **fit_params)

        # Gather the last observation date if time_colname is set
        if time_colname is not None:
            time_column_index = series_frame.time_index
            self._last_observation_dates[lvl] = time_column_index.max()
            self._first_observation_dates[lvl] = time_column_index.min()

        return True

    # Another candidate for a private method? Do we want the user
    #  to be concerned with sharding the data?
    def fit_map_func(self, data):
        """
        A mapper function to split the data that will be used by the 
        compute backend. Why? - because the caller is the one that 
        knows how his data must be split and this logic must not
        reside with the callee (the computes). 

        Issues: The mapper is ideally a generator. However, this runs
        into pickling errors when distributed backends such as 
        Dask is used. 

        >>>  while True:            
                for lvl, series_frame in data_by_grain:
                    yield (lvl, series_frame)
        """
        # Group-by grain
        data_by_grain = data.groupby_grain()
        return {lvl: series_frame for lvl, series_frame in data_by_grain}
