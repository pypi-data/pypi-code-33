# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""lag_lead_featurizer.py, a file for storing lag lead featurizer."""
import automl.client.core.common.constants as constants
import automl.client.core.common.abstract_timeseries_transformer as atransformer


LAG_LEAD_OPERATOR = 'lag_lead_operator'


class LagLeadFeaturizer(atransformer.AbstractTimeSeriesTransformer):
    """
    A transformation class for computing lags and leads for values in DataFrame.

    This will be used as a featurization step inside
    the forecast pipeline.
    For more information on forecasting terminology refer to documentation.
    :doc: `Documentation/timeseries.md`

    """

    def __init__(self,
                 lags_to_construct,
                 max_horizon=1,
                 dropna=False,
                 origin_time_colname=constants.TimeSeries.ORIGIN_TIME_COLNAME_DEFAULT,
                 overwrite_columns=False,
                 logger=None,
                 **kwargs):
        """
        Construct for the class.

        :param lags_to_construct:
            dictionary of the form {'column_to_lag' : [lag_order1, lag_order2]}.
            Dictionary keys must be names of columns in the data frame to which
            the transform is applied. Dictionary values are either integers or
            lists of integers indicating what lags must be constructed.
            Negative values are allowed, and indicate 'leads' i.e. moving into
            the future values of time series. In this case the Lag_0 means current value.
            Lead_0 would be the next value that follows after the Lag_1.
        :type lags_to_construct: dict

        :param max_horizon:
            how many steps ahead do you intend to predict the series later. This
            is used to construct a full grid of `time` and `origin_time` to make
            sure that output is compatible with multi-step forecasting featurizers
            downstream. This argument is ignored if the input data has
            `origin_time_colname` set, because it is assumed that the job of
            setting up multi-horizon data structure had already been performed.
            Defaults to 1 to produce expected behavior for most users.
        :type max_horizon: int

        :param dropna:
            should missing values from lag creation be dropped? Defaults to False.
            Note that the missing values from the test data are not dropped but
            are instead 'filled in' with values from training data.
        :type dropna: bool

        :param origin_time_colname:
            how to name the `origin_time` column when the input does not contain
            one. Must be a single string. This argument is ignored if the input
            data has `origin_time_colname` set, because it is assumed that the job
            of setting up multi-horizon data structure had already been performed.
            Defaults to "origin".
        :type origin_time_colname: str

        :param overwrite_columns:
            Flag that permits the transform to overwrite existing lag and lead
            columns in the input TimeSeriesDataFrame for features that are already
            present in it. The existing origin column will not be affected by a transform.
            If True, prints a warning and overwrites columns.
            If False, throws a RuntimeError.
            Defaults to False to protect user data.
        :type overwrite_columns: bool

        :param logger: The logger to be used in the pipeline.
        :type logger: logging.Logger

        :param kwargs: kwargs contains metadata for TimeSeries.
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
        self.lags_to_construct = lags_to_construct
        self.max_horizon = max_horizon
        self.dropna = dropna
        self.origin_time_colname = origin_time_colname
        self.overwrite_columns = overwrite_columns
        super(LagLeadFeaturizer, self).__init__(logger, **kwargs)

    def _construct_pre_processing_pipeline(self, tsdf, drop_column_names=None):
        """
        Construct the pre processing pipeline.

        :param tsdf: The time series data frame.
        :type tsdf: TimeSeriesDataFrame
        :param drop_column_names: Not used.
        :type drop_column_names: list

        """
        from .forecasting_pipeline import AzureMLForecastPipeline
        from .lag_lead_operator import LagLeadOperator
        lag_lead = LagLeadOperator(lags_to_construct=self.lags_to_construct,
                                   max_horizon=self.max_horizon,
                                   dropna=self.dropna,
                                   origin_time_colname=self.origin_time_colname,
                                   overwrite_columns=self.overwrite_columns)

        # pipeline:
        lag_lead_pipeline = AzureMLForecastPipeline([
            (LAG_LEAD_OPERATOR, lag_lead)
        ])
        return lag_lead_pipeline
