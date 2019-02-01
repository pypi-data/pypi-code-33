import os
import sys
import inspect
import numpy as np
import pandas as pd
from warnings import warn
import dateutil.relativedelta as dt_util
from statsmodels.tsa.arima_model import ARIMA
import scipy.stats

from ftk.exception import (EstimatorTypeException, EstimatorValueException)
from ftk.models.recursive_forecaster import RecursiveForecaster


class Arima(RecursiveForecaster):
    """
    Auto Regressive Integrated Moving Average univariate time series model.

    This class is an adaptation of 'arima_model' in the 'statsmodels' python package
    for an sklearn-style fit/predict interface.

    This class defines an `order` parameter; other parameters are 
    inherited from :class:`ftk.models.recursive_forecaster.RecursiveForecaster`.

    :param order: 
        Order of the ARIMA model to fit. The order is defined by a triple
        of integers, `[p, d, q]`, which specifies the auto-regressive order,
        the degree of differencing, and the moving-average order, respectively.
    :type order: list of length 3

    .. todo:: In future add parameters for seasonal forecasting and also for error metric.

    """

    def __init__(self, freq=None, order=[1, 0, 0],
                 seasonality=None,
                 pred_point_colname=None,
                 pred_dist_colname=None,
                 origin_time_colname=None):

        super().__init__(freq=freq, seasonality=seasonality,
                         pred_point_colname=pred_point_colname,
                         pred_dist_colname=pred_dist_colname,
                         origin_time_colname=origin_time_colname)
        self.order = order

    @property
    def order(self):
        """
        Order of the ARIMA model,  `[p, d, q]`.
        """
        return self._order

    @order.setter
    def order(self, val):
        if isinstance(val, str) and len(val) == 0:
            self._order = None
        elif isinstance(val, list) and all(isinstance(item, int)
                                           for item in val):
            self._order = val
        else:
            raise EstimatorTypeException('Arima: '
                                         + 'order must be represented as a list of integers.')

    """
        This method ensures that the data frame passed in satifies the criteria needed by the fit and predict method.
        Commenting this method out since it will handled separately as part of the auto.arima implementation.    
    def _check_dataframe(self, X, method) :
        super()._check_dataframe(X, method) 

        groupby_columns = X.grain_colnames
        series_column = X.ts_value_colname
        date_column = X.time_colname

        X_grouped = X.groupby(groupby_columns)
        grain_levels_list = list(X_grouped.groups.keys())
        num_grain_levels = len(grain_levels_list)
        
        if (num_grain_levels > 1 or num_grain_levels < 1) :
            raise Exception('ARIMA: Input should have exactly one grain level.')

    """

    def _single_series_train(self, series_values, grain_level, **fit_params):

        # Always convert the series value to 'float64' the reason is that the
        # fit method of arima_model in statsmodels could encounter TypeError
        # for time series contains integer values. See
        # https://github.com/statsmodels/statsmodels/issues/2984 for more details.
        series_values = series_values.astype(float)

        # In statsmodels 0.9 version for ARIMA model, if freq parameter is
        # specified then dates are also needed to be specified. This needs a
        # change in signature of the _single_series_train method. Also, in
        # future we may need to ensure that frequency the input data is also
        # supported by ARIMA model if we pass freq as parameter.So, for
        # simplicity purpose ignoring both freq and dates.
        # Note: (1) This needs to be revisited at the time when we want to
        # include support for seasonality while building ARIMA model.
        # (2) It assumes that recusiveforecaster passes in the input series
        # (series_values) that is regular and in order (missing values are
        # taken care of).
        warn('Arima._single_series_train: '
             'invoking statsmodels.tsa.arima_model.ARIMA without '
             'dates and freq parameter.')
        arima_model = ARIMA(series_values, order=self._order)
        """
            Fits ARIMA(p,d,q) model by exact maximum likelihood via Kalman
            filter. disp is an optional int parameter. If True, convergence
            information is printed. 
            disp < 0 means no output in this case.
        """
        try:
            arima_model_fit = arima_model.fit(disp=-1, **fit_params)
        except (ValueError, np.linalg.LinAlgError):
            arima_model_fit = None

        return arima_model_fit

    def _multi_series_train(self, data_by_grain, *args, **fit_params):
        """
            This fits ARIMA(p,d,q) model using the _single_series_train. To do so, this
            invokes schedule jobs on the grouped data_frame passing in args required. The actual
            model fitting is not dependent on the specific "compute" chosen but it directly dependent on
            the current model context.           

        """
        # TODO..TODO..The unit test is skipped for now. Need to test further.
        super()._multi_series_train(data_by_grain, *args, **fit_params)

    def fit(self, X, y=None, **fit_params):
        super().fit(X, y, **fit_params)
        unfit_grains = [k for k, v in self._models.items() if v is None]
        if len(unfit_grains) == len(self._models):
            warn("Unable to fit specified model to any of the data",
                 UserWarning)
        if len(unfit_grains) > 0:
            warn("{} grains could not be fit".format(len(unfit_grains)),
                 UserWarning)
        for k in unfit_grains:
            self._models.pop(k)
            self._last_observation_dates.pop(k)
            self._first_observation_dates.pop(k)
            self._grain_levels.remove(k)
        return self

    def _single_series_point_forecast(self, model, max_horizon, grain_level):
        arima_fcast = model.forecast(max_horizon)
        arima_fcast_values = arima_fcast[0]

        return arima_fcast_values

    """
        Comment from Amita: In order to gain the distribution of errors, currently needs to invoke Forecast function again. 
        This could be avoided but may also need to  make changes in recursiveforecaster as it currently needs implementation of two abstract methods.       
        For now only return an array of standard errors as it is expected to return a single dimensional array. revisit this to return confidence intervals.
    """

    def _single_series_distribution_forecast(self, model, max_horizon, grain_level):
        """
            forecast method returns a tuple consisting:
            -  array of out of sample forecasts.
            -  array of the standard error of the forecasts.
            -  2d array of the confidence interval for the forecast.
        """
        arima_fcast = model._results.forecast(max_horizon)

        arima_fcast_values = arima_fcast[0]
        arima_fcast_std_err = arima_fcast[1]
        arima_fcast_conf_int = arima_fcast[2]

        """
        Commenting the code for now that returns arrya of <standard_error, lower_bound_forecast, upper_bound_forecast>.
        arima_fcast_std_err_1 = arima_fcast_std_err.reshape(max_horizon, 1)
        arima_fcast_dist = np.concatenate((arima_fcast_std_err_1, arima_fcast_conf_int), axis = 1)
        return arima_fcast_dist
        """

        distributions = [scipy.stats.norm(loc=arima_fcast_values[h-1],
                                          scale=arima_fcast_std_err[h-1])
                         for h in range(1, max_horizon + 1)]
        return np.array(distributions)

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
        nan_values = np.empty(self.order[1])
        nan_values.fill(np.nan)
        return np.concatenate((nan_values, model.predict(typ='levels')))

    def get_model_info(self):
        """
        Get summary information for all fitted models.

        :return: 
            A dictionary with keys given by grain levels and 
            values given by model summaries of type `ARIMAResults`
            (see statsmodels)
        :rtype: dict 

        """
        if not self._is_fit:
            raise EstimatorValueException(
                'Arima.model_info: fit must be called before retrieving the summary.')

        model_summary = {lvl: None for lvl in self._grain_levels}
        for grain_level in self._grain_levels:
            model_info = self._models[grain_level].summary()
            model_summary[grain_level] = model_info

        return model_summary

    def get_fitted_models(self, grain_levels_list=None):
        """
        Get a dictionary of fitted models.

        :param grain_levels_list: 
            List of grains for which to get fitted models.
            The grains are specified as strings or tuples of
            strings, depending on whether there is a single
            or multiple columns defining the grain.
            If `None`, fitted models for all grains are returned.
        :type grain_levels_list: list of str, list of tuples  

        :return: 
            A dictionary with keys given by grain levels
            and values by fitted models of type `Arima`.
        :rtype: dict
        """
        if not self._is_fit:
            raise EstimatorValueException(
                'Arima.get_fitted_models: fit must be called before retrieving the results.')
        if (grain_levels_list == None):
            model_results = self._models
        else:
            model_results = {lvl: None for lvl in grain_levels_list}
            for grain_level in grain_levels_list:
                if (grain_level in self._grain_levels):
                    model_results[grain_level] = self._models[grain_level]
                else:
                    warn('Arima.get_fitted_models: no fitted model exists for grain_level {0}.'.format(
                        grain_level))

        return model_results
