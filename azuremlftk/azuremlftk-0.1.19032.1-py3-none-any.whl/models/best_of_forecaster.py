import pandas as pd
import numpy as np
from warnings import warn
from scipy.stats import norm
from sklearn.utils.metaestimators import _safe_split
from sklearn.metrics import mean_absolute_error
from ftk.models import ForecasterUnion
from ftk.model_selection import RollingOriginValidator


class BestOfForecaster(ForecasterUnion):
    """
    .. py:class:: BestOfForecaster

    This class enables fit/predict on a collection of forecasting models and
    selection of the model with the best accuracy using cross-validation. 
    While fit evaluates all models provided, predict only returns the results 
    for the best model for each grain.

    Fitting parameters of an individual forecaster may be set using its name 
    and the parameter name separated by a '__'. 

    :param forecaster_list: 
        List of models to be applied to the data.
        Each list element is a tuple with two entries.
        The first half of each tuple is a name to associate with
        the resulting forecast and the second half is an object meeting
        the following qualfications:
        1. Instances of RecursiveForecaster subclasses
        2. Instance of RegressionForecaster 
        3. Instance of AzureMLForecastPipeline with last step satisfying
           either (1) or (2) above.
    :type forecaster_list: list of (string, predictor) tuples  

    :param n_jobs:
        Number of jobs to run in parallel (default 1).
    :type n_jobs: int

    """

    def __init__(self, forecaster_list, n_jobs=1):
        super(BestOfForecaster, self).__init__(forecaster_list, n_jobs)
        self.best_by_grain = None
        self._stdevs = None

    def fit(self, X, y=None, validator=RollingOriginValidator(),
            metric_fun=mean_absolute_error, **fit_params):
        """
        Fit all the forecasters and use cross-validation to select the best
        forecaster for each grain.

        :param X: Input data used to fit forecasters
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`

        :param y: 
            Target quantity for supervised learning.
            Ignored by many forecasters since X already contains
            the target quantity.

        :param validator:
            A validator object used to select the best model for each grain.
            While any validator is compatible (e.g. :class:`sklearn.model_selection.KFold`),
            the accuracuy of prediction intervals depends on the use of an 
            instance of :class:`ftk.model_selection.RollingOriginValidator`.
            (default `RollingOriginValidator()`)
        :type validator: :class:`sklearn.model_selection.BaseValidator`

        :param metric_fun:
            A function for computing the metric to be optimized when selecting
            the best model for each grain.  The model with the minimum output from
            `metric_fun` will be returned.  Must take parameters `y_true` and 
            `y_pred`. (default `sklearn.metrics.mean_absolute_error`)
        :type metric_fun: function

        :param **fit_params:
            Keyword fit parameters passed on to the forecaster fit methods.
            These arguments should have the form,
            ```<Forecaster name>__<Parameter name>=<Parameter value>```
        :type **fit_params: dict

        """
        splits = validator.split(X)
        predictions = pd.DataFrame()
        errors = pd.DataFrame()
        # Use cross-validation to select the best model
        for train, test in splits:
            # Split the data
            X_train, y_train = _safe_split(None, X, y, train)
            X_test, y_test = _safe_split(None, X, y, test, train)
            # Get the predictions on the testing data
            fitted = super(BestOfForecaster, self).fit(
                X_train, y_train, **fit_params)
            predicted = super(BestOfForecaster, self).predict(X_test)
            predicted = predicted[~np.isnan(predicted[predicted.pred_point])]
            # at this point predictions gets converted to a MFDF
            predictions = predictions.append(predicted)
            if y_train is not None:
                predicted[X.actual] = y_train
            # group by grain and model
            pred_group = predicted.groupby(
                level=predicted.grain_colnames + list(predicted.model_colnames.values()))
            # Compute the error function
            error = pred_group.apply(
                lambda x: metric_fun(x[x.actual], x[x.pred_point]))
            errors = errors.append(error.to_frame(name='error'))
        # Get the mean error accross CV folds
        mean_errors = errors.groupby(level=errors.index.names).mean()
        mean_errors.reset_index(
            list(predicted.model_colnames.values()), inplace=True)
        # Identify the model with the smallest error
        min_errors = mean_errors.sort_values('error').groupby(
            level=X.grain_colnames).first()
        # Store the model with the lowest error for each grain
        grain_dict = {g: m for g, m in
                      zip(min_errors.index.values,
                          min_errors[list(predicted.model_colnames.values())].values)}
        self.best_by_grain = grain_dict
        # Check that all grains were analyzed, throw a warning if not
        if set(self.best_by_grain.keys()) != set(X.grain_index):
            warn(("Not all grains were evaluated during cross-validation! Missing grains " +
                  "were {0}. Consider increasing the value of `n_fold` or `n_step` in the " +
                  "`validator` object").format(set(X.grain_index).difference(set(self.best_by_grain.keys()))),
                 UserWarning)
        # Compute the standard deviation of out of sample errors for use in
        # calculating prediciton intervals
        stdevs = predictions._stdev_by_slicekey()
        stdev_dict = {k: s for k, s in
                      zip(stdevs.index.values, stdevs.values)}
        self._stdevs = stdev_dict
        # Fit the model to the full training data.
        self = super(BestOfForecaster, self).fit(
            X, y, **fit_params)
        return self

    def predict(self, X, include_forecaster_params=False,
                retain_feature_column=False, overwrite_pi=False):
        """
        Predict the target quantity with the best forecaster for each grain.

        :param X: Data to use for predict
        :type X: :class:`ftk.forecast_data_frame.ForecastDataFrame`, :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`

        :param include_forecaster_params:
            Whether to include a column which contains the
            dictionary of parameters name and value pair in the forecaster.
        :type include_forecaster_params: boolean

        :param retain_feature_column:
            Whether to retain the feature columns in the output forecast data
            frame.
        :type retain_feature_column: boolean

        :param overwrite_pi:
            Whether to over write the prediction intervals generated by the models
            with the prediction intervals generated by out of sample errors from
            best model selection.
        :type overwrite_pi: boolean

        :return: Data with predictions from the best forecaster for each grain.
        :rtype: :class:`ftk.multi_forecast_data_frame.MultiForecastDataFrame`

        """
        if not self._is_fit:
            raise EstimatorValueException('The BestOfForecaster has not been '
                                          'fitted yet. Please call fit() '
                                          'method '
                                          'to fit the BestOfForecaster before '
                                          'calling the predict() method.')

        def predict_grain(X_grain):
            if X_grain.grain_index.values[0] not in self.best_by_grain:
                warn(("grain {0} was not evaluated in training data so predictions " +
                      "cannot be returned").format(X_grain.grain_index.values[0]), UserWarning)
                return
            # since this function is called once for each grain, we can get
            # we just need the first element to get the grain designation.
            forecaster_name = self.best_by_grain[X_grain.grain_index.values[0]]
            if isinstance(forecaster_name, np.ndarray):
                forecaster_name = forecaster_name[0]
            # the initializer function checks that the forecaster names are
            # unique so we can just grab the first one.
            forecaster_list_item = [
                l for l in self.forecaster_list if l[0] == forecaster_name][0]
            predicted = self._predict_one_forecaster(forecaster_list_item, X_grain,
                                                     include_forecaster_params,
                                                     retain_feature_column)
            if predicted.pred_dist == None:
                predicted["PredictionDistribution"] = None
                predicted.pred_dist = "PredictionDistribution"
            # Computes prediction intervals from the BestOfForecaster cross-validation
            # if 1) it was requested or 2) the forecaster doesn't natively have
            # prediction intervals (e.g. regression forecaster)
            if all([d is None for d in predicted[predicted.pred_dist]]) or overwrite_pi:
                # Groups by slice_key, but uses horizon instead of origin_time
                groupings = [predicted.index.get_level_values(
                    col) for col in predicted.slice_key_colnames if col != predicted.origin_time_colname]
                if predicted.origin_time_colname is not None:
                    groupings.append(predicted.horizon)
                groupings = pd.MultiIndex.from_arrays(groupings)
                # Gets the stdev that was stored earlier for the slice_keys
                stdevs = [self._stdevs[i] if i in self._stdevs.keys()
                          else None for i in groupings]
                # Computes the intervals
                dists = [norm(loc=m, scale=s) if s is not None else None
                         for m, s in zip(predicted[predicted.pred_point].values, stdevs)]
                predicted[predicted.pred_dist] = dists

            return predicted
        # Evaluate each grain independantly
        X_by_grain = X.groupby_grain()
        return X_by_grain.apply(predict_grain)
