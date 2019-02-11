# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Includes classes for storing timeseries preprocessing related functions."""
import warnings
import pandas as pd
import sklearn
import numpy as np

import automl.client.core.common.preprocess as preprocess
import automl.client.core.common.abstract_timeseries_transformer as atransformer

# Prevent warnings when using Jupyter
warnings.simplefilter("ignore")
pd.options.mode.chained_assignment = None


class MissingDummiesTransformer(sklearn.base.BaseEstimator,
                                sklearn.base.TransformerMixin,
                                preprocess.TransformerLogger):
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

    @preprocess.function_debug_log_wrapped
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


class NumericalizeTransformer(sklearn.base.BaseEstimator,
                              sklearn.base.TransformerMixin,
                              preprocess.TransformerLogger):
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

    @preprocess.function_debug_log_wrapped
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


class TimeSeriesTransformer(atransformer.AbstractTimeSeriesTransformer):
    """Class for timeseries preprocess."""

    def __init__(self, logger=None, **kwargs):
        """
        Construct for the class.

        :param logger: The logger to be used in the pipeline.
        :type logger: logging.Logger
        :param kwargs: dictionary contains metadata for TimeSeries.
                       time_column_name: The column containing dates.
                       grain_column_names: The set of columns defining the
                       multiple time series.
                       origin_column_name: latest date from which actual values
                       of all features are assumed to be known with certainty.
                       drop_column_names: The columns which will needs
                       to be removed from the data set.
                       group: the group column name.
        :type kwargs: dict

        """
        super(TimeSeriesTransformer, self).__init__(logger, **kwargs)

    def _construct_pre_processing_pipeline(self, tsdf, drop_column_names):
        """Return the featurization pipeline."""
        from .forecasting_pipeline import AzureMLForecastPipeline
        from .grain_index_featurizer import GrainIndexFeaturizer
        from .time_series_imputer import TimeSeriesImputer
        from .time_index_featurizer import TimeIndexFeaturizer

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
        if self.group_column in categorical_columns:
            categorical_columns.remove(self.group_column)

        # pipeline:
        default_pipeline = AzureMLForecastPipeline([
            ('make_numeric_na_dummies', MissingDummiesTransformer(numerical_columns)),
            ('impute_na_numeric_columns', impute_missing_numerical_values),
            ('make_time_index_featuers', time_index_featurizer)
        ])

        # Don't apply grain featurizer when there is single timeseries
        if self.dummy_grain_column not in self.grain_column_names:
            grain_index_featurizer = GrainIndexFeaturizer(overwrite_columns=True)
            default_pipeline.add_pipeline_step('make_grain_features', grain_index_featurizer)

        default_pipeline.add_pipeline_step('make_categoricals_numeric', NumericalizeTransformer())
        return default_pipeline
