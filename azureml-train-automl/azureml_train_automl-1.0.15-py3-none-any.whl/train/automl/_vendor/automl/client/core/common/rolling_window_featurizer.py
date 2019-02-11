# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""rolling_window_featurizer.py, a file for storing rolling window featurizer."""
import automl.client.core.common.constants as constants
import automl.client.core.common.abstract_timeseries_transformer as atransformer


ROLLING_WINDOW_FEATURIZER = 'rolling_window'


class RollingWindowFeaturizer(atransformer.AbstractTimeSeriesTransformer):
    """
    A transformation class for creating rolling window features from the columns of a DataFrame.

    Rolling windows are temporally defined with respect to origin times
    in the DataFrame. The origin time in a data frame row
    indicates the right date/time boundary of a window.
    If the input data frame does not contain origin times, they
    will be created based on the ```max_horizon``` parameter.

    """

    def __init__(self, window_size, transform_dict, window_opts=None,
                 transform_opts=None, max_horizon=1,
                 origin_time_colname=constants.TimeSeries.ORIGIN_TIME_COLNAME_DEFAULT,
                 dropna=False,
                 logger=None,
                 **kwargs):
        """
        Construct RollingWindowFeaturizer.

        :param window_size:
             Size of the moving window.
             Either the number of observations in each window
             or a time-span specified as a pandas.DateOffset.
             Note that when the size is given as a DateOffset,
             the window may contain a variable number of observations.
        :type window_size: int, pandas.DateOffset

        :param transform_dict:
            A dictionary specifying the rolling window transformations
            to apply on the columns. The keys are functions
            or names of pre-defined Pandas rolling window methods.
            See https://pandas.pydata.org/pandas-docs/stable/computation.html#method-summary.
            The dict values are columns on which to apply the functions.
            Each value can be a single column name or a list
            of column names.
        :type transform_dict: dict

        :param window_opts:
            A dictionary of keyword window options.
            These will be passed on to the pandas.Rolling
            constructor as **kwargs.
            See pandas.DataFrame.rolling for details.

            To avoid target leakage, the ```center``` option
            setting here is ignored and always set to False.

            The ```closed``` option is also ignored.
            For integer window size, it is set to `both`.
            For DateOffset window size, it is set to `right`.
        :type window_opts: dict

        :param transform_opts:
            A dictionary of aggregation function options. The keys are aggregation
            function names. The value is again a dictionary with two keys: args
            and kwargs, the value of the 'args' key is the positional arguments
            passed to the aggregation function and the value of the 'kwargs' key
            is the keyword arguments passed to the aggregation function.
        :type transform_opts: dict

        :param max_horizon:
            Integer horizons defining the origin times to create.
            Parameter can be a single integer - which indicates a maximum
            horizon to create for all grains - or a dictionary where the keys
            are grain levels and each value is an integer maximum horizon.
        :type max_horizon: int, dict

        :param origin_time_colname:
            Name of origin time column to create in case origin times
            are not already contained in the input data frame.
            The `origin_time_colname` property of the transform output
            will be set to this parameter value in that case.
            This parameter is ignored if the input data frame contains
            origin times.
        :type origin_time_colname: str

        :param dropna:
            Should missing values from rolling window feature creation be dropped?
            Defaults to False.
            Note that the missing values from the test data are not dropped but
            are instead 'filled in' with values from training data.
        :type dropna: bool

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
        self.window_size = window_size
        self.transform_dict = transform_dict
        self.window_opts = window_opts
        if self.window_opts is None:
            self.window_opts = {}
        self.transform_opts = transform_opts
        if self.transform_opts is None:
            self.transform_opts = {}
        self.max_horizon = max_horizon
        self.origin_time_colname = origin_time_colname
        self.dropna = dropna
        super(RollingWindowFeaturizer, self).__init__(logger, **kwargs)

    def _construct_pre_processing_pipeline(self, tsdf, drop_column_names=None):
        """
        Construct the pre processing pipeline.

        :param tsdf: The time series data frame.
        :type tsdf: TimeSeriesDataFrame
        :param drop_column_names: The columns to be dropped.
        :type drop_column_names: list

        """
        from .forecasting_pipeline import AzureMLForecastPipeline
        from .rolling_window import RollingWindow
        rolling_window = RollingWindow(window_size=self.window_size,
                                       transform_dict=self.transform_dict,
                                       window_opts=self.window_opts,
                                       transform_opts=self.transform_opts,
                                       max_horizon=self.max_horizon,
                                       origin_time_colname=self.origin_time_colname,
                                       dropna=self.dropna)
        rolling_window_pipeline = AzureMLForecastPipeline([(ROLLING_WINDOW_FEATURIZER, rolling_window)])
        return rolling_window_pipeline
