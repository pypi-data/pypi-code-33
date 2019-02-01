import numpy as np
import pandas as pd
from warnings import warn

from sklearn.base import BaseEstimator

from ftk.base_estimator import AzureMLForecastTransformerBase, loggable
from ftk.exception import (InvalidEstimatorTypeException,
                           EstimatorValueException,
                           NotTimeSeriesDataFrameException)


class SklearnEstimatorWrapper(AzureMLForecastTransformerBase):
    """
    Wrapper for sklearn estimators so that their fit/predict
    methods are compatible with :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`.
    Wrapping is a necessary condition for including the estimator
    in an :class:`ftk.pipeline.AzureMLForecastPipeline`. 

    .. _sklearn.base.BaseEstimator: http://scikit-learn.org/stable/modules/generated/sklearn.base.BaseEstimator.html

    :param sklearn_estimator: Internal sklearn estimator
    :type sklearn_estimator: sklearn.base.BaseEstimator_

    """

    def __init__(self, sklearn_estimator):
        
        self.sklearn_estimator = sklearn_estimator

        self._features_in_fit = list()

    @property
    def sklearn_estimator(self):
        return self._sklearn_estimator

    @sklearn_estimator.setter
    def sklearn_estimator(self, est):

        if isinstance(est, BaseEstimator):
            self._sklearn_estimator = est

        else:
            raise InvalidEstimatorTypeException(
                'estimator must inherit from sklearn BaseEstimator.')

    @property
    def features_in_fit(self):
        """
        List of column names in the design matrix when
        the fit method is called. 
        
        """
        return self._features_in_fit

    def _prepare_input(self, X, y):

        # Get numpy array representations of X, y
        X_np = X
        y_np = y
        if isinstance(X, pd.DataFrame):
            X_np = X.values
        if isinstance(y, pd.Series) or isinstance(y, pd.DataFrame):
            y_np = y.values

        return X_np, y_np
       
    @loggable
    def fit(self, X, y=None, **fit_params):
        """
        Fit the sklearn estimator.

        .. _pandas.DataFrame: http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html
        .. _pandas.Series: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.html

        This method simply extracts numpy.ndarray_
        representations of X and y and
        passes them on to `sklearn_estimator.fit`.

        :param X: Input data
        :type X: pandas.DataFrame_

        :param y: Target quantity for supervised learning
        :type y: pandas.Series_, pandas.DataFrame_

        :return: Wrapped, fitted estimator
        :rtype: SklearnEstimatorWrapper
        """
        
        X_np, y_np = self._prepare_input(X, y)
        fitted = self._sklearn_estimator.fit(X_np, y=y_np, **fit_params)

        # Store the names of the features
        self._features_in_fit = list(X.columns)

        return self

    @loggable
    def predict(self, X):
        """
        Predict values using the fitted sklearn estimator.

        .. _numpy.ndarray: https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.html

        This method simply extracts an numpy.ndarray_
        representation of X and passes it to sklearn_estimator.predict.

        :param X: Input data
        :type X: pandas.DataFrame

        :returns: Predicted data
        :rtype: numpy.ndarray_

        """

        # Check for mismatch of X columns with the
        #  columns present in fit
        if list(X.columns) != self._features_in_fit:
            warn(('SklearnEstimatorWrapper.predict: '\
                + 'X has a different set of columns '\
                + 'than were present at fit. '\
                + 'X columns: {0}, columns in fit: {1}').format(
                    X.columns, 
                    self._features_in_fit))

        X_np, _ = self._prepare_input(X, None)

        return self._sklearn_estimator.predict(X_np)
