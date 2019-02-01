from warnings import warn
import numpy as np
import pandas as pd
import scipy.stats

from ftk.models.recursive_forecaster import RecursiveForecaster
from ftk.exception import EstimatorValueException


class _SeasonalNaiveModel(object):
    """
    Internal class encapsulating the training and forecasting 
    computations for the seasonal naive model.

    This is a utility class used by the main SeasonalNaive class.
    It should not be instantiated outside of this module.

    """

    def __init__(self):
        self._seasonality = None
        self._fit_mse = None
        self._last_season_observations = None
        self.fitted_values = None

    def train(self, series_values, seasonality):
        """
        Train a seasonal naive model. 

        Compute the mean squared error of the fit 
        and store the last full season cycle of observations
        from the training data.

        :param series_values : 1-d ndarray of time series values in date ascending order

        :param seasonality :
            integer representing the seasonality of the series in
            number of periods.

        :returns: No return object. This method changes object state.

        """

        self._seasonality = seasonality

        # Get the fit values via right shifting the series by the seasonality
        naive_fitted = series_values[:-seasonality]
       
        if len(series_values) > seasonality:

            # Compute the mean squared error on the overlap between fit and obs
            self._fit_mse = np.mean(
                (naive_fitted - series_values[seasonality:])**2)

        else:

            # If we have a single season or less of obs,
            #  the fit mse is undefined
            warn(('SeasonalNaive: Series length of {0} is too short to compute '
                  + 'the mean squared error of the fit. '
                  + 'Forecast variances will be undefined for this series.')
                 .format(len(series_values)))
            self._fit_mse = np.nan

        # Set the full fitted values array by padding 
        #   the naive fitted forecasts with NaNs
        num_pads = series_values.size - naive_fitted.size
        self.fitted_values = np.concatenate((np.repeat(np.nan, num_pads),
                                             naive_fitted))

        # Store the last season of obs for prediction
        self._last_season_observations = series_values[-seasonality:]

    def forecast(self, max_horizon):
        """
        Make a forecast up to the max_horizon.

        The forecast variance is calculated according to:
        v_h = sigma^2 * (1 + floor((h-1)/seasonality)),
        where sigma^2 is estimated via the mean squared error 
        of the fit.

        For justification of this formula, see: 
        Prediction intervals for exponential smoothing using two
        new classes of state space models,
        Hyndman et. al., J. Forecasting, 2015.

        In that paper, Hydnman derives the forecast variance 
        for the ETS(A, A_d, A) model - 
        seasonal naive is just a special case with
        alpha = beta = 0, gamma = 1

        :param max_horizon:
            integer giving the maximum horizon value.
            Forecasts will be generated at horizons 1, ..., max_horizon.

        :return: point forecasts and forecast variances as numpy arrays.

        """

        # How many full seasons do we need?
        full_seasons = np.ceil(max_horizon/self._seasonality).astype(int)

        # Make point forecast from stored obs
        fcast = np.tile(self._last_season_observations,
                        full_seasons)[:max_horizon]

        # Get forecast variance
        variance_multiplier = np.repeat(np.arange(1, 1+full_seasons),
                                        self._seasonality)[:max_horizon]

        return fcast, self._fit_mse*variance_multiplier


class SeasonalNaive(RecursiveForecaster):
    """
    Seasonal Naive univariate time series model.
    This model predicts future values of a time series by repeating
    the final season of observations ahead in time. 

    Uses the RecursiveForecaster base class to handle TimeSeriesDataFrame 
    book-keeping in fit and predict.

    This class primarily implements the abstract methods in RecursiveForecaster for
    training/forecasting single series.

    In the case where SeasonalNaive is trained on a series with less than a 
    full season cycle of observations, the model disregards the seasonality 
    and generates a simple naive forecast.

   For a description of the class parameters, see :class:`ftk.models.recursiveforecaster.RecursiveForecaster`
    """

    def __init__(self, freq=None, seasonality=None,
                 pred_point_colname=None,
                 pred_dist_colname=None,
                 origin_time_colname=None):
        # Must call the RecursiveForecaster constructor first!
        super().__init__(freq=freq, seasonality=seasonality,
                         pred_point_colname=pred_point_colname,
                         pred_dist_colname=pred_dist_colname,
                         origin_time_colname=origin_time_colname)

    def _single_series_train(self, series_values, grain_level):
        """
        Implementation of RecursiveForecaster abstract method for
        training a model on a single series.
        See RecursiveForecaster._single_series_train for more comments.

        """

        # Get the seasonality from the base class
        # The seasonality is either set by the user or automatically detected
        seasonality = self._single_series_get_seasonality(
            series_values, grain_level)

        # Check that the series has at least a full season of data
        # If not, revert to naive forecast and print a warning
        input_length = len(series_values)
        if input_length < seasonality:
            warn(('SeasonalNaive: series length {0} is less than a full season. '
                  + 'Reverting to naive forecast').format(input_length))
            seasonality = 1

        # "Train" the model
        # Really just storing some state in an object
        naive_model = _SeasonalNaiveModel()
        naive_model.train(series_values, seasonality)

        # Store the final seasonality in the object state
        self._seasonality_output[grain_level] = seasonality

        return naive_model

    def _single_series_point_forecast(self, model, max_horizon, grain_level):
        """
        Implementation of RecursiveForecaster abstract method for
        generating a point forecast from a single series model.
        See RecursiveForecaster._single_series_point_forecast for more comments.
        """

        fcast, _ = model.forecast(max_horizon)

        return fcast

    def _single_series_distribution_forecast(self, model, max_horizon, grain_level):
        """
        Implementation of RecursiveForecaster abstract method for
        generating a distribution forecast from a single series model.
        See RecursiveForecaster._single_series_distribution_forecast for more comments.

        """

        fcast, fcast_variance = model.forecast(max_horizon)

        # Naive forecast errors are assumed gaussian
        distributions = [scipy.stats.norm(loc=fcast[h-1],
                                          scale=np.sqrt(fcast_variance[h-1]))
                         for h in range(1, max_horizon + 1)]

        return np.array(distributions)

    def _multi_series_train(self, data_by_grain, *args, **fit_params):
        super()._multi_series_train(data_by_grain, *args, **fit_params)

    def _return_fitted_values(self, model, grain_level):
        """
        Returns the fitted values from a model.

        :param model
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
       
        return model.fitted_values


class Naive(SeasonalNaive):
    """
    Naive univariate time series model.
    This model predicts future values of a time series by repeating
    the final observation ahead in time.
    It is equivalent to a SeasonalNaive model with the seasonality set
    to a single period. 

    Uses the RecursiveForecaster base class to handle TimeSeriesDataFrame 
    book-keeping in fit and predict.

    This class primarily implements the abstract methods in RecursiveForecaster for
    training/forecasting single series.

    For a description of the class parameters, see :class:`ftk.models.recursiveforecaster.RecursiveForecaster`

    """

    def __init__(self, freq=None, seasonality=None,
                 pred_point_colname=None,
                 pred_dist_colname=None,
                 origin_time_colname=None):

        # constrain the seasonality equal to 1
        super().__init__(freq=freq, seasonality=1,
                         pred_point_colname=pred_point_colname,
                         pred_dist_colname=pred_dist_colname,
                         origin_time_colname=origin_time_colname)

    @property
    def seasonality(self):
        """
        Seasonality property.
        For the Naive forecaster, the seasonality is always 1.

        See :class:`ftk.models.recursiveforecaster.RecursiveForecaster`
        """
        if self._is_fit:
            return self._seasonality_output
        else:
            return self._seasonality_input

    @seasonality.setter
    def seasonality(self, val):
        """
        The seasonality setter will throw exception if val is other than 1, 
        since Naive always needs to have seasonality equal to one.

        """
        if self._is_fit:
            # Seasonality is read-only after fit is called.
            raise EstimatorValueException('RecursiveForecaster.seasonality: '
                                          + 'Cannot set seasonality on a fit model')

        if val == 1:
            self._seasonality_input = 1
        else:
            raise EstimatorValueException(
                'The seasonality of the Naive forecaster cannot be '
                + 'any value other than 1.')

        # Initialize the output. We'll fill this dictionary during fit
        self._seasonality_output = dict()
