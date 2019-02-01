"""
Featurize the grain columns. 
"""

import pandas as pd
import numpy as np
from warnings import warn

from ftk.time_series_data_frame import TimeSeriesDataFrame
from ftk.base_estimator import AzureMLForecastTransformerBase, loggable
from ftk import utils
from ftk.exception import (AzureMLForecastException,
                           NotTimeSeriesDataFrameException)


class GrainIndexFeaturizer(AzureMLForecastTransformerBase):
    """
    .. py:class:: GrainIndexFeaturizer
    
    Transform that adds grain related features  
    to a TimeSeriesDataFrame.
    By default, the transforms adds a new categorical
    column for each level in the time series grain index.
    If make_horizon_feature=True, the transform
    will construct an integer horizon feature from
    the origin_time_index.

    :param grain_feature_prefix:
        Prefix to apply to names of columns created for grain features.
        Defaults to `grain`
    :type grain_feature_prefix: str

    :param horizon_feature_prefix:
        Prefix to apply to column name created for a horizon feature.
        Defaults to `horizon`
    :type horizon_feature_prefix: str

    :param prefix_sep:
        Separator to use in new grain/horizon column names between
        the prefix and the name of the relevant index level.
        Defaults to `_`.
        Ex: If the grain index has levels `store` and `brand`,
        the new grain features will be named `grain_store` and
        `grain_brand` by default.
    :type prefix_sep: str

    :param make_horizon_feature:
        Flag for making a horizon feature. 
        The name of the feature will be determined by the
        TimeSeriesDataFrame.origin_time_colname, 
        horizon_feature_prefix,and prefix_sep.
        Ex: If the origin time column is `ForecastOrigin`,
        the horizon feature will be named `horizon_ForecastOrigin`,
        by default.
        Defaults to True
    :type make_horizon_feature: boolean

    :param overwrite_columns:
        Flag that permits the transform to overwrite existing columns in the 
        input TimeSeriesDataFrame for features that are already present in it. 
        If True, prints a warning and overwrites columns.
        If False, throws a AzureMLForecastException. 
        Defaults to False to protect user data.
    :type overwrite_columns: boolean

    :param ts_frequency:
        The frequency of the time series that this transform will be applied to.
        This parameter is used to construct the horizon feature.
        If ts_frequency=None, the fit method will attempt to infer the frequency
        from the input TimeSeriesDataFrame.
    :type ts_frequency: str (pandas offset alias), pd.DateOffset

    """

    def __init__(self, grain_feature_prefix='grain',
                 horizon_feature_prefix='horizon',
                 prefix_sep='_',
                 make_horizon_feature=True,
                 overwrite_columns=False,
                 ts_frequency=None):

        self.grain_feature_prefix = grain_feature_prefix
        self.horizon_feature_prefix = horizon_feature_prefix
        self.prefix_sep = prefix_sep
        self.make_horizon_feature = make_horizon_feature
        self.overwrite_columns = overwrite_columns
        self.ts_frequency = ts_frequency

    def _check_input(self, X):
        if not isinstance(X, TimeSeriesDataFrame):
            raise NotTimeSeriesDataFrameException(
                'GrainIndexFeaturizer: X must be a TimeSeriesDataFrame')

    def preview_grain_feature_names(self, X):
        """
        Get the grain features names that would be made
        if the transform were applied to X

        :param X: Input data
        :type X: TimeSeriesDataFrame

        :return: grain feature names
        :rtype: list of strings
        """
        if X.grain_colnames is None:
            return []
        grain_cols = X.grain_index.names
        feat_names = [self.grain_feature_prefix +
                      self.prefix_sep + idx
                      for idx in grain_cols]

        return feat_names

    def preview_horizon_feature_name(self, X):
        """
        Get the horizon feature name that would 
        be made if the transform were applied to X

        :param X: Input data
        :type X: TimeSeriesDataFrame

        :return: horizon feature name
        :rtype: str, None if no origin time column is set
        """
        name = None
        if X.origin_time_colname is not None:
            name = self.horizon_feature_prefix + self.prefix_sep + \
                X.origin_time_colname

        return name
    
    @loggable
    def fit(self, X, y=None):
        """
        Fit the grain featurizer

        :param X: Input data
        :type X: :class:`ftk.dateframets.TimeSeriesDataFrame`

        :param y: 
            Ignored. Included for pipeline compatibility

        :return: self
        :rtype: GrainIndexFeaturizer
        """

        self._check_input(X)

        if self.make_horizon_feature and self.ts_frequency is None:
            self.ts_frequency = X.infer_freq()

        return self

    @loggable
    def transform(self, X):
        """
        Transform the input data

        :param X: Input data
        :type X: :class:`ftk.dateframets.TimeSeriesDataFrame`

        :return: Transformed data
        :rtype: :class:`ftk.dateframets.TimeSeriesDataFrame`
        """

        self._check_input(X)

        new_columns = {}
        if X.grain_colnames is not None:
            grain_names = self.preview_grain_feature_names(X)
            grain_cols = X.grain_index.names
            new_columns = {nm:
                           pd.Categorical(X.index.get_level_values(idx))
                           for nm, idx in zip(grain_names, grain_cols)}

        if self.make_horizon_feature is True:
            if X.origin_time_colname is not None:

                horizon_feature = \
                    utils.get_period_offsets_from_dates(X.origin_time_index,
                                                        X.time_index,
                                                        self.ts_frequency)

                horizon_name = self.preview_horizon_feature_name(X)
                new_columns.update({horizon_name: horizon_feature})

            else:
                warn('GrainIndexFeaturizer.transform: '
                     + 'X does not have an origin time column set. '
                     + 'Cannot create a horizon feature.')

        if len(new_columns) == 0:
            warn('No grain is set and horizon features were not created; ' +
                 'data will be unchanged', UserWarning)
        # Check for existing columns of the same names
        overlap = set(new_columns).intersection(set(X.columns))
        if len(overlap) > 0:
            message = ('Some of the existing columns in X will be '
                       + 'overwritten by the transform: {0}. ').format(overlap)
            # if told to overwrite - warn
            if self.overwrite_columns:
                warn(message, UserWarning)
            else:
                # if not told to overwrite - raise exception
                error_message = message + ("Set 'overwrite_columns' to True "
                                           + 'to overwrite columns in X, currently it is {0}').format(
                    self.overwrite_columns)
                raise AzureMLForecastException(error_message)

        return X.assign(**new_columns)
