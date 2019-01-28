# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Includes classes for storing timeseries preprocessing related functions."""
import warnings
import pandas as pd
import numpy as np

from .constants import TimeSeries
from sklearn.base import BaseEstimator, TransformerMixin
from automl.client.core.common.preprocess import TransformerLogger, function_debug_log_wrapped
warnings.simplefilter("ignore")
pd.options.mode.chained_assignment = None


class MissingDummiesTransformer(BaseEstimator, TransformerMixin, TransformerLogger):
    """Add columns indicating corresponding numeric columns have NaN."""

    def __init__(self, numerical_columns, logger=None):
        """
        Construct for MissingDummiesTransformer.

        :param numerical_columns: The columns that will be marked.
        :type numerical_columns: list
        :return:
        """
        self._init_logger(logger)
        self.numerical_columns = numerical_columns

    def fit(self, x, y=None):
        """
        Fit function for MissingDummiesTransformer.

        :param x: Input data.
        :type x: TimeSeriesDataFrame
        :param y: Target values.
        :type y: numpy.ndarray
        :return: Class object itself.
        """
        return self

    @function_debug_log_wrapped
    def transform(self, x):
        """
        Transform function for MissingDummiesTransformer.

        :param x: Input data.
        :type x: TimeSeriesDataFrame
        :return: Result of MissingDummiesTransformer.
        """
        result = x.copy()
        for col in self.numerical_columns:
            is_null = result[col].isnull()
            result[col + '_WASNULL'] = is_null.apply(lambda x: int(x))
        return result


class NumericalizeTransformer(BaseEstimator, TransformerMixin, TransformerLogger):
    """Encode categorical columns with integer codes."""

    NA_CODE = pd.Categorical(np.nan).codes[0]

    def __init__(self, logger=None):
        """
        Construct for NumericalizeTransformer.

        :param categorical_columns: The columns that will be marked.
        :type categorical_columns: list
        :return:
        """
        self._init_logger(logger)

    def fit(self, x, y=None):
        """
        Fit function for NumericalizeTransformer.

        :param x: Input data.
        :type x: TimeSeriesDataFrame
        :param y: Target values.
        :type y: numpy.ndarray
        :return: Class object itself.
        """
        # Detect all categorical type columns
        fit_cols = (x.select_dtypes(['object', 'category', 'bool'])
                    .columns)

        # Save the category levels to ensure consistent encoding
        #   between fit and transform
        self._categories_by_col = {col: pd.Categorical(x[col]).categories
                                   for col in fit_cols}

        return self

    @function_debug_log_wrapped
    def transform(self, x):
        """
        Transform function for NumericalizeTransformer transforms categorical data to numeric.

        :param x: Input data.
        :type x: TimeSeriesDataFrame
        :return: Result of NumericalizeTransformer.
        """
        # Check if X categoricals have categories not present at fit
        # If so, warn that they will be coded as NAs
        for col, fit_cats in self._categories_by_col.items():
            now_cats = pd.Categorical(x[col]).categories
            new_cats = set(now_cats) - set(fit_cats)
            if len(new_cats) > 0:
                warnings.warn((type(self).__name__ + ': Column {0} contains '
                               'categories not present at fit: {1}. '
                               'These categories will be set to NA prior to encoding.')
                              .format(col, new_cats))

        # Get integer codes according to the categories found during fit
        assign_dict = {col:
                       pd.Categorical(x[col],
                                      categories=fit_cats)
                       .codes
                       for col, fit_cats in self._categories_by_col.items()}

        return x.assign(**assign_dict)


class TimeSeriesTransformer(BaseEstimator, TransformerMixin, TransformerLogger):
    """Class for timeseries preprocess."""

    def __init__(self, param_dict, logger=None):
        """
        Construct for TimeSeriesTransformer class.

        :param param_dict: dictionary contains related parameters.
        :type param_dict: dict
        """
        if TimeSeries.TIME_COLUMN_NAME not in param_dict.keys():
            raise KeyError("{} must be set".format(TimeSeries.TIME_COLUMN_NAME))
        self.time_column_name = param_dict[TimeSeries.TIME_COLUMN_NAME]
        self.grain_column_names = param_dict.get(TimeSeries.GRAIN_COLUMN_NAMES)
        self.drop_column_names = param_dict.get(TimeSeries.DROP_COLUMN_NAMES)

        self._init_logger(logger)

        self.target_column_name = '_automl_target_col'
        # Used to make data compatible with timeseries dataframe
        self.dummy_grain_column = '_automl_dummy_grain_col'
        self.dummy_group_column = '_automl_dummy_group_col'
        self.original_order_column = '_automl_original_order_col'

        self.engineered_feature_names = None

    def _construct_pre_processing_pipeline(self, tsdf, drop_column_names):
        self._logger_wrapper('info', 'Start construct pre-processing pipeline.')
        try:
            from ftk.transforms import (TimeSeriesImputer, TimeIndexFeaturizer,
                                        DropColumns, GrainIndexFeaturizer)
        except ImportError as ie:
            raise ie
        numerical_columns = [x for x in tsdf.select_dtypes(include=[np.number]).columns
                             if x not in drop_column_names]
        if self.target_column_name in numerical_columns:
            numerical_columns.remove(self.target_column_name)
        if self.original_order_column in numerical_columns:
            numerical_columns.remove(self.original_order_column)

        imputation_dict = {col: tsdf[col].median() for col in numerical_columns}
        impute_missing_numerical_values = TimeSeriesImputer(
            input_column=numerical_columns, value=imputation_dict, freq=self.freq)

        time_index_featurizer = TimeIndexFeaturizer(overwrite_columns=True)

        categorical_columns = [x for x in tsdf.select_dtypes(['object', 'category', 'bool']).columns
                               if x not in drop_column_names]
        if self.dummy_group_column in categorical_columns:
            categorical_columns.remove(self.dummy_group_column)

        try:
            from ftk.pipeline import AzureMLForecastPipeline
        except ImportError as ie:
            raise ie
        # pipeline:
        default_pipeline = AzureMLForecastPipeline([
            ('make_numeric_na_dummies', MissingDummiesTransformer(numerical_columns)),
            ('impute_na_numeric_columns', impute_missing_numerical_values),
            ('make_time_index_featuers', time_index_featurizer)
        ])
        # Don't add dropColumn transfomer if there is nothing to drop
        if len(drop_column_names) > 0:
            default_pipeline.add_pipeline_step('drop_irrelevant_columns', DropColumns(drop_column_names),
                                               prepend=True)

        # Don't apply grain featurizer when there is single timeseries
        if self.dummy_grain_column not in self.grain_column_names:
            grain_index_featurizer = GrainIndexFeaturizer(overwrite_columns=True)
            default_pipeline.add_pipeline_step('make_grain_features', grain_index_featurizer)

        default_pipeline.add_pipeline_step('make_categoricals_numeric', NumericalizeTransformer())

        self._logger_wrapper('info', 'Finish Construct Pre-Processing Pipeline.')
        return default_pipeline

    def _impute_target_value(self, tsdf):
        """Perform the y imputation based on frequency."""
        try:
            from ftk.transforms import TimeSeriesImputer
        except ImportError as ie:
            raise ie
        target_imputer = TimeSeriesImputer(input_column=tsdf.ts_value_colname,
                                           option='fillna', method='ffill',
                                           freq=self.freq)

        return target_imputer.fit_transform(tsdf)

    def fit_transform(self, X, y=None, **fit_params):
        """
        Wrap around the fit_transform function for the Data transformer class.

        :param X: Dataframe representing text, numerical or categorical input.
        :type X: numpy.ndarray or pandas.DataFrame
        :param y: To match fit signature.
        :type y: numpy.ndarray or pandas.DataFrame
        :param fit_params: Additional parameters for fit_transform().
        :param logger: External logger handler.
        :type logger: logging.Logger
        :return: Transformed data.
        """
        self.fit(X, y, **fit_params)
        return self.transform(X, y)

    def fit(self, df, y=None):
        """
        Perform the raw data validation and identify the transformations to apply.

        :param df: Dataframe representing text, numerical or categorical input.
        :type df: pandas.DataFrame
        :param y: To match fit signature.
        :type y: numpy.ndarray
        :return: DataTransform object.
        :raises: Value Error for non-dataframe and empty dataframes.
        """
        if self.grain_column_names is None or len(self.grain_column_names) == 0:
            df[self.dummy_grain_column] = self.dummy_grain_column
            self.grain_column_names = [self.dummy_grain_column]
        df[self.target_column_name] = y

        tsdf = self._create_tsdf_from_data(df,
                                           time_column_name=self.time_column_name,
                                           target_column_name=self.target_column_name,
                                           grain_column_names=self.grain_column_names)

        all_drop_column_names = [x for x in tsdf.columns if
                                 np.sum(tsdf[x].notnull()) == 0]
        if isinstance(self.drop_column_names, str):
            all_drop_column_names.extend([self.drop_column_names])
        elif self.drop_column_names is not None:
            all_drop_column_names.extend(self.drop_column_names)

        self.freq = tsdf.infer_freq(True)
        self.pipeline = self._construct_pre_processing_pipeline(tsdf, all_drop_column_names)
        self.pipeline.fit(tsdf, y)
        return self

    def transform(self, df, y=None):
        """
        Transform the input raw data with the transformations idetified in fit stage.

        :param df: Dataframe representing text, numerical or categorical input.
        :type df: pandas.DataFrame
        :param y:
        :type y:
        :return: pandas.DataFrame
        """
        if not self.pipeline:
            raise Exception("fit not called")

        if self.dummy_grain_column in self.grain_column_names:
            df[self.dummy_grain_column] = self.dummy_grain_column

        transformed_data = None
        if y is not None:
            # transform training data
            df[self.target_column_name] = y
            tsdf = self._create_tsdf_from_data(df,
                                               time_column_name=self.time_column_name,
                                               target_column_name=self.target_column_name,
                                               grain_column_names=self.grain_column_names)
            tsdf = self._impute_target_value(tsdf)
            transformed_data = self.pipeline.transform(tsdf)
        else:
            # Dealing with X_test, save the row sequence number then use it to restore the order
            # Drop existing index if there is any
            df.reset_index(inplace=True, drop=True)

            df[self.original_order_column] = df.index
            tsdf = self._create_tsdf_from_data(df,
                                               time_column_name=self.time_column_name,
                                               target_column_name=None,
                                               grain_column_names=self.grain_column_names)
            # preserve the index because the input X_test may not be continurous
            transformed_data = self.pipeline.transform(tsdf)
            transformed_data = transformed_data[transformed_data[self.original_order_column].notnull()]
            transformed_data.sort_values(by=[self.original_order_column], inplace=True)
            transformed_data.pop(self.original_order_column)

        transformed_data.pop(self.dummy_group_column)
        if self.engineered_feature_names is None:
            self.engineered_feature_names = transformed_data.columns.values.tolist()
            if self.target_column_name in self.engineered_feature_names:
                self.engineered_feature_names.remove(self.target_column_name)
        return pd.DataFrame(transformed_data)

    def get_engineered_feature_names(self):
        """
        Get the transformed column names.

        :return: list of strings
        """
        return self.engineered_feature_names

    def _create_tsdf_from_data(self, data, time_column_name, target_column_name=None,
                               grain_column_names=None):
        """
        Given the input data, construct the time series data frame.

        :param data: data used to train the model.
        :type data: pandas.DataFrame
        :param time_column_name: Column label identifying the time axis.
        :type time_column_name: str
        :param target_column_name: Column label identifying the target column.
        :type target_column_name: str
        :param grain_column_names:  Column labels identifying the grain columns.
                                Grain columns are the "group by" columns that identify data
                                belonging to the same grain in the real-world.

                                Here are some simple examples -
                                The following sales data contains two years
                                of annual sales data for two stores. In this example,
                                grain_colnames=['store'].

                                >>>          year  store  sales
                                ... 0  2016-01-01      1     56
                                ... 1  2017-01-01      1     98
                                ... 2  2016-01-01      2    104
                                ... 3  2017-01-01      2    140

        :type grain_column_names: str, list or array-like
        :return: TimeSeriesDataFrame
        """
        data[time_column_name] = pd.to_datetime(data[time_column_name])
        # In timeseries model, group_column defines model boundary.
        # Not support multiple model yet, we use the whole data to train one model
        data[self.dummy_group_column] = self.dummy_group_column
        data = data.infer_objects()
        try:
            from ftk.time_series_data_frame import TimeSeriesDataFrame
        except ImportError as ie:
            raise ie
        tsdf = TimeSeriesDataFrame(data, time_colname=time_column_name,
                                   ts_value_colname=target_column_name,
                                   grain_colnames=grain_column_names,
                                   group_colnames=self.dummy_group_column)
        return tsdf
