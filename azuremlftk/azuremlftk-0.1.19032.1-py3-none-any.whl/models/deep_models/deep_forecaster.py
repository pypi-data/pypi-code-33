"""
This file contains internal functions used by deep learning models to 
convert TSDFs into a format consumable by deep learning archetectures.
"""
import numpy as np
import pandas as pd
from abc import ABCMeta, abstractmethod, abstractproperty

from ftk import TimeSeriesDataFrame, ForecastDataFrame, last_n_periods_split
from ftk.base_estimator import AzureMLForecastRegressorBase
from ftk.transforms import TimeSeriesImputer, CategoryBinarizer
from ftk.exception import (DataFrameTypeException, NotSupportedException,
                           NotTimeSeriesDataFrameException)
from ftk.constants import *

import keras.backend as K
from keras.layers import Lambda, Subtract, ZeroPadding1D, Multiply, Add, Input
from keras.models import Model


class DeepForecaster(AzureMLForecastRegressorBase,
                     metaclass=ABCMeta):
    """
    Abstract base class for a Keras deep learning forecaster.
    This class implements scikit-learn style fit/predict methods on
    TimeSeriesDataFrame objects. Specific modeling code is in derived classes
    that define the specific model archetecture.

    Derived classes must implement private method `_create_estimator_`, 
    which populates the `estimator` property.

    :param lag_window_size: 
        The number of lags of the time series to use to create windows 
        of the training data.
    :type lag_window_size: int

    :param horizon: 
        The number of future values to predict using the model.
    :type horizon: int
    """

    def __init__(self, lag_window_size, horizon,
                 preprocess=None, post_process=None):

        self.lag_window_size = lag_window_size
        self.horizon = horizon
        self.preprocess = preprocess
        self.post_process = post_process

    @property
    def lag_window_size(self):
        return self._lag_window_size

    @lag_window_size.setter
    def lag_window_size(self, val):
        if not isinstance(val, int):
            raise TypeError("lag_window_size must be of type int.")
        if not val > 0:
            raise ValueError("lag_window_size must be a positive value")
        self._lag_window_size = val

    @property
    def horizon(self):
        return self._horizon

    @horizon.setter
    def horizon(self, val):
        if not isinstance(val, int):
            raise TypeError("horizon must be of type int.")
        if not val > 0:
            raise ValueError("horizon must be a positive value")
        self._horizon = val

    @property
    def preprocess(self):
        return self._preprocess

    @preprocess.setter
    def preprocess(self, val):
        if val is None or val in ['difference', 'subtract', 'divide']:
            self._preprocess = val
        else:
            raise ValueError(
                "preprocess must be None or in ['difference', 'subtract', 'divide']")

    @property
    def post_process(self):
        return self._post_process

    @post_process.setter
    def post_process(self, val):
        if val is None or val in ['add', 'multiply']:
            self._post_process = val
        else:
            raise ValueError(
                "post_process must be None or in ['add', 'multiply']")

    @property
    def estimator(self):
        """
        This property defines the Keras model to be fitted to the TSDF data.
        """
        return self._estimator

    @abstractmethod
    def _create_estimator_(self, n_features=1):
        """
        This method will create the Keras model to be be stored in the "estimator"
        property.
        """
        pass

    def finalize_model(self, n_features=1):
        """
        This creates the models made by _create_estimator_ and adds pre 
        and post processing steps.
        """
        self._create_estimator_(n_features)
        base_model = self._estimator

        input_layer = Input(name='lag_input_layer', shape=(
            self.lag_window_size, n_features, ))

        if self.post_process == 'subtract':
            last_value = self.extract_last_value(input_layer)
        if self.post_process == 'multiply' or self.preprocess == 'divide' or \
                self.post_process == 'add' or self.preprocess == 'subtract':
            mean_value, mean_target = self.extract_mean_value(input_layer)

        x_l = input_layer
        if self.preprocess == 'difference':
            x_l = self.difference_series(x_l)
        elif self.preprocess == 'subtract':
            x_l = Subtract(name='preprocess_subtract')([x_l, mean_value])
        elif self.preprocess == 'divide':
            x_l = Lambda(lambda x: x/mean_value, name='preprocess_divide')(x_l)

        base_model.layers.pop(0)
        x = base_model(x_l)

        if self.post_process == 'add':
            x = Add(name='post_process_add')([x, mean_target])
        elif self.post_process == 'multiply':
            x = Multiply(name='post_process_multiply')([x, mean_target])
        output_layer = x

        model = Model(input_layer, output_layer)
        self._estimator = model

    def extract_mean_value(self, x):
        # Normalize by the highest activation
        mean_value = Lambda(lambda x: K.mean(
            K.abs(x), 1, keepdims=True) + 1e-5, name='mean_value')(x)
        mean_target = Lambda(
            lambda tt: tt[:, :, 0], name='select_value')(mean_value)
        mean_target = Lambda(lambda x: K.repeat_elements(
            x, self.horizon, 1), name='repeat_horizon')(mean_target)
        mean_value = Lambda(lambda x: K.repeat_elements(
            x, self.lag_window_size, 1), name='repeat_lag_size')(mean_value)
        return mean_value, mean_target

    def extract_last_value(self, x):
        last_value = Lambda(lambda tt: tt[:, -1, 0], name='select_value')(x)
        last_value = Lambda(K.expand_dims, name='add_dim')(last_value)
        last_value = Lambda(lambda x: K.repeat_elements(
            x, self.horizon, -1), name='repeat')(last_value)
        return last_value

    def difference_series(self, x):
        difference = ZeroPadding1D((1, 0), name="shift_layer")(
            Lambda(lambda x: x[:, :-1, :])(x))
        x = Subtract(name='preprocess_difference')([x, difference])
        return x

    def fit(self, x, freq=None, skip=1,
            compile_params={'loss': 'mean_squared_error', 'optimizer': 'adam'},
            **kwargs):
        """
        Fit model to training data X

        :param x: Training data
        :type x: TimeSeriesDataFrame

        :param freq: the input frequency
        :type freq: pandas.DateOffset

        :param compile_params:
            A dict of parameters to be sent to the model `compile` command.
        :type compile_params: dict

        :param kwargs:
            Other arguments to be sent to the `fit` function.
        """
        if 'y' in kwargs.keys():
            raise NotSupportedException(
                "target values are generated from `ts_value_colname`, `y` inputs" +
                "are not accepted.")
        if not isinstance(x, TimeSeriesDataFrame):
            raise NotTimeSeriesDataFrameException(
                "`x` should be a `TimeSeriesDataFrame`."
            )

        if freq is None:
            freq = x.infer_freq()

        if 'validation_data' in kwargs.keys():
            if not isinstance(kwargs['validation_data'], TimeSeriesDataFrame):
                raise NotTimeSeriesDataFrameException(
                    "`validation_data should be a `TimeSeriesDataFrame`."
                )
            kwargs['validation_data'] = self._prepare_dataset(
                kwargs['validation_data'], freq=freq, skip=skip)
        else:
            _, val_data = last_n_periods_split(
                x, self.lag_window_size + self.horizon)
            x, _ = last_n_periods_split(x, self.horizon)
            kwargs['validation_data'] = self._prepare_dataset(
                val_data, freq=freq)

        X_train, y_train = self._prepare_dataset(x, freq=freq, skip=skip)
        self.finalize_model(X_train.shape[2])
        self.estimator.compile(**compile_params)
        self.estimator.fit(x=X_train, y=y_train,
                           **kwargs)

    def predict(self, x, *args, **kwargs):
        """
        Fit model to training data X

        :param x: Training data
        :type x: TimeSeriesDataFrame
        """
        # Get the feature matrix and the identifier data
        X_array, idx, origin_time = self._get_feature_windows(x)
        # Create predictions using the  model predict function
        pred = self.estimator.predict(X_array, *args, **kwargs)
        # Create a data frame to store the outputs with the identifier data
        pred_df = pd.DataFrame(pred, index=idx)
        pred_df[ORIGIN_TIME_COLNAME_DEFAULT] = origin_time
        pred_df = pred_df.set_index(ORIGIN_TIME_COLNAME_DEFAULT, append=True)
        # Pivot the dataframe to make the forecasts long form
        pred_df = pred_df.stack()
        pred_df = pred_df.reset_index(pred_df.index.nlevels - 1)
        pred_df.columns = ['horizon', UNIFORM_PRED_POINT_COLNAME]
        # Calculate the time_index value for each row
        freq = x.infer_freq()
        origin_values = pred_df.index.get_level_values(
            ORIGIN_TIME_COLNAME_DEFAULT)
        horizon_values = 1 + pred_df['horizon'].values
        pred_df[x.time_colname] = [t + n*freq for t,
                                   n in zip(origin_values, horizon_values)]
        # Format the data to merge in actuals and drop the horizon
        pred_df = pred_df.set_index(x.time_colname, append=True)
        pred_df = pred_df.reset_index(ORIGIN_TIME_COLNAME_DEFAULT)
        pred_df = pred_df.reorder_levels(x.index.names)
        # Re-factored to merge due to this issue:
        # https://pandas.pydata.org/pandas-docs/stable/indexing.html#indexing-deprecate-loc-reindex-listlike
        x_value_df = pd.DataFrame(x[[x.ts_value_colname]], copy=False)
        pred_df = pred_df.merge(x_value_df, how='left', 
                                left_index=True, right_index=True) 
        
        pred_df = pred_df.drop('horizon', axis=1)
        # Get the metadata for the ForecastDataFrame
        metadata = x._get_metadata_dict()
        metadata['origin_time_colname'] = ORIGIN_TIME_COLNAME_DEFAULT
        metadata['pred_point'] = UNIFORM_PRED_POINT_COLNAME
        metadata['actual'] = metadata.pop('ts_value_colname')
        # Create the FDF output
        pred_fdf = ForecastDataFrame(pred_df, **metadata)
        return pred_fdf

    def _make_tsdf_lags_single_grain(self, tsdf, freq=None, skip=1):
        """
        Internal function which takes single grain TSDF and outputs a training and
        testing matrix for consumption by a neural network archetecture.

        :param X: The TSDF to convert to a matrix.
        :type X: TimeSeriesDataFrame

        :param freq: the input frequency
        :type freq: pandas.DateOffset
        """
        # begin by preprocessing the data
        tsdf = tsdf.fill_datetime_gap(freq=freq)
        tsdf = tsdf.sort_index()
        # Create rolling windows of data for X and y targets
        win_len = self.lag_window_size + self.horizon
        model_values = [(tsdf.values[i:i+self.lag_window_size, :],
                         tsdf[tsdf.ts_value_colname].values[i+self.lag_window_size:i+win_len])
                        for i in reversed(range(tsdf.shape[0] - win_len, -1, -skip))]
        # Concatenate windows into arrays
        X = np.array([m[0] for m in model_values])
        y = np.array([m[1] for m in model_values])
        # The data isn't even long enough for training, return arrays
        # of length zero.
        if X.shape[0] == 0:
            X = np.zeros((0, self.lag_window_size, tsdf.shape[1]))
            y = np.zeros((0, self.horizon))

        return X, y  # X_train, y_train, X_test, y_test

    def _prepare_dataset(self, X, freq=None, skip=1):
        """
        Internal function which takes an input a TSDF and outputs a training and
        testing matrix for consumption by a neural network archetecture.

        :param X: The TSDF to convert to a matrix.
        :type X: TimeSeriesDataFrame

        :param freq: the input frequency
        :type freq: pandas.DateOffset
        """
        # Apply preprocessing to standardize input
        X = self._pre_process_data(X)
        # Compute frequency once to save compute in the groupby
        if freq is None:
            freq = X.infer_freq()
        # Create the training and testing data for each grain
        X_grain = X.groupby_grain()
        values = X_grain.apply(
            lambda x: self._make_tsdf_lags_single_grain(x, freq=freq, skip=skip))
        # Concatenate the data for each grain into a single matrix
        X_train = np.concatenate([v[0] for v in values], axis=0)
        y_train = np.concatenate([v[1] for v in values], axis=0)

        has_nan = np.isnan(
            X_train.reshape(X_train.shape[0], -1)).any(axis=1) | np.isnan(y_train).any(axis=1)
        X_train = X_train[~has_nan]
        y_train = y_train[~has_nan]

        return X_train, y_train

    def _pre_process_data(self, X):
        """
        Standard preprocessing steps to prepare data for learning including
        category binarization and moving the `ts_value` column to the first
        column.
        """
        if X.origin_time_colname is not None:
            raise DataFrameTypeException(
                "Deep learning models cannot handle data with origin_times.")
        # Begin by ensuring all data are numeric types
        cat_col = X.select_dtypes(include=['object', 'category'])
        binarizer = CategoryBinarizer(
            columns=cat_col,
            drop_first=True)
        X = binarizer.fit_transform(X)
        # Make sure that the ts_value_colname is the first value in the series
        X = X[[X.ts_value_colname] +
              [c for c in X.columns if c != X.ts_value_colname]]
        return X

    def _make_features_single_grain(self, tsdf, freq=None):
        """
        Internal function which takes single grain TSDF and outputs a feature matrix 
        for predictions from a neural network archetecture.

        :param X: The TSDF to convert to a matrix.
        :type X: TimeSeriesDataFrame

        :param freq: the input frequency
        :type freq: pandas.DateOffset
        """
        # begin by preprocessing the data
        tsdf = tsdf.fill_datetime_gap(freq=freq)
        tsdf = tsdf.sort_index()
        # Create rolling windows of data for X and y targets
        model_values = [tsdf.values[i:i+self.lag_window_size, :]
                        for i in range(tsdf.shape[0] - self.lag_window_size + 1)]
        # Get time values
        last_time = [tsdf.time_index[i]
                     for i in range(self.lag_window_size - 1, tsdf.shape[0])]
        last_time = np.array(last_time)
        # Concatenate windows into arrays
        X = np.array(model_values)
        # Replace missing data with zeros
        X[np.isnan(X)] = 0
        # Create the training and validation data sets
        if X.shape[0] == 0:
            # The data isn't even long enough prediction, return array
            # of length zero.
            zero_vals = np.zeros((self.lag_window_size - tsdf.shape[0],
                                  tsdf.shape[1]))
            X = np.concatenate([zero_vals, tsdf.values])
            X = X.reshape((1, X.shape[0], X.shape[1]))
            last_time = np.array(tsdf.time_index[-1], ndmin=1)
        return X, last_time

    def _get_feature_windows(self, X, freq=None):
        """
        Internal function which takes an input a TSDF and outputs a feature
        matrix for consumption by a neural network archetecture.

        :param X: The TSDF to convert to a matrix.
        :type X: TimeSeriesDataFrame

        :param freq: the input frequency
        :type freq: pandas.DateOffset
        """
        X = self._pre_process_data(X)
        # Compute frequency once to save compute in the groupby
        if freq is None:
            freq = X.infer_freq()
        # Create the features for each grain
        X_grain = X.groupby_grain()
        values = X_grain.apply(
            lambda x: self._make_features_single_grain(x, freq=freq))
        # Organize outputs
        # Make a index to match the output data
        idx = values.index.repeat([v[0].shape[0] for v in values])
        # Get the origin times for each row
        origin_time = np.array(np.concatenate([v[1] for v in values], axis=0))
        # Concatentate the feature matrices
        X = np.concatenate([v[0] for v in values], axis=0)
        return X, idx, origin_time
