"""
Decompose the target value to the Trend and Seasonality.
"""
import pandas as pd
import numpy as np
import warnings

from statsmodels.tsa.seasonal import seasonal_decompose

from ftk.forecast_data_frame import ForecastDataFrame
from ftk.base_estimator import AzureMLForecastTransformerBase, loggable
from ftk.exception import NotSupportedException
from ftk.models.exponential_smoothing import ExponentialSmoothing
from ftk.constants import STL_SEASON_SUFFIX, STL_TREND_SUFFIX
from numpy import int64
from numpy.ma.testutils import assert_array_equal


class STLFeaturizer(AzureMLForecastTransformerBase):
    """
    The class for decomposition of input data to the seasonal and trend component.

    If seasonality is not presented by int or int64 ValueError is raised.
    :param seasonality: Time series seasonality. If seasonality is set to -1, it will be inferred.
    :type seasonality: int
    :param model_type:
        str {"additive"(default), "multiplicative"}
        Type of seasonal component. Abbreviations are accepted.
    :type model_type: str
    :raises: ValueError

    """

    def __init__(self, seasonality=-1, model_type='additive'):
        """Constructor."""

        self._model_type = model_type
        if not isinstance(
                seasonality,
                int) and not isinstance(
                seasonality,
                int64):
            raise ValueError("The seasonality should be an integer.")
        self._seasonality = seasonality
        self._stls = {}
        self._origins_freqs = {}  # Contains origins and frequencies.
        self._trend_model = None

    @loggable
    def fit(self, X, y=None):
        """
        Determine trend and seasonality.
        If the number of rows is <= seasonality, the ValueError is raised.

        :param X: Input data
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`
        :param y: Not used, added for back compatibility with scikit**-**learn.
        :type y: np.array
        :return: Fitted transform
        :rtype: TimeIndexFeaturizer
        :raises: ValueError

        """
        if self.seasonality == -1:
            self._seasonality = self.infer_seasonality(X)

        if self.seasonality >= X.shape[0]:
            raise ValueError("Each grain of the training data set "
                             "should have more rows than seasonality.")

        result = (X.groupby_grain()
                  .apply(lambda df_one:
                         self._fit_one_grain(df_one)))
        # The Exponential Smoothing model is used for prediction only, but
        # for consistency its type matches the type of STLFeaturizer.
        mtype = 'AA' if self._model_type == 'additive' else 'MM'
        model = ExponentialSmoothing(model_type=mtype)
        result.ts_value_colname = result.ts_value_colname + STL_TREND_SUFFIX
        result.dropna(inplace=True)
        if result is None or result.shape[0] == 0:
            warnings.warn("The trend can not be established!")
            self._trend_model = None
        else:
            self._trend_model = model.fit(result)
        return self

    @loggable
    def transform(self, X):
        """
        Create time index features for an input data frame.
        **Note** in this method we assume that we do not know the target value.

        :param X: Input data
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`
        :return: Data frame with trand and seasonality column.
        :rtype: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`
        :raises: NotSupportedException
        """
        if not self._stls.keys() or self.seasonality == -1:
            error_message = \
                ("For the STLFeaturizer to work correctly, fit() " +
                 "must be called before transform()!")
            raise NotSupportedException(error_message)

        result = (X.groupby_grain()
                   .apply(lambda df_one:
                          self._transform_one_grain(df_one)))
        # At that point we do not have the trend column. Use the Exponential Smoothing
        # model to predict it.
        trend_colname = result.ts_value_colname + STL_TREND_SUFFIX
        if self._trend_model:
            tsdf_temp = result.copy()
            tsdf_temp = tsdf_temp.assign(
                **{trend_colname: np.repeat(np.NaN, tsdf_temp.shape[0])},
                **{'trend_dist': np.repeat(np.NaN, tsdf_temp.shape[0])})
            tsdf_temp.ts_value_colname = tsdf_temp.ts_value_colname + STL_TREND_SUFFIX
            fdf_temp = ForecastDataFrame(
                tsdf_temp,
                pred_point=trend_colname,
                pred_dist='trend_dist')
            fdf_temp = self._trend_model.predict(fdf_temp)
            result = result.merge(pd.DataFrame(
                data=fdf_temp[fdf_temp.pred_point]), left_index=True, right_index=True)
            # Merging will introduce the origin column. Drop it.
            result.drop('origin', axis=1, inplace=True)
            return result
            # return result.assign(
            #    **{trend_colname: fdf_temp[fdf_temp.pred_point].values})
        else:
            return result.assign(
                **{trend_colname: np.repeat(np.NaN, result.shape[0])})

    @loggable
    def fit_transform(self, X, y=None):
        """
        Apply `fit` and `transform` methods in sequence.
        **Note** that because in this case we know the target value
        and hence we can use the statsmodel of trend inference.

        :param X: Input data.
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`
        :param y: Not used, added for back compatibility with scikit**-**learn.
        :type y: np.array
        :return: Data frame with trand and seasonality column.
        :rtype: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`

        """
        self.fit(X)
        result = (X.groupby_grain()
                   .apply(lambda df_one:
                          self._fit_transform_one_grain(df_one)))
        return result

    def infer_seasonality(self, X):
        """
        Return the seasonality of the data.
        If different grains have different seasonality the warning is shown and
        the most frequent seasonality will be returned.

        :param X: The dataset.
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`
        :returns: The seasonality.
        :rtype: int

        """
        max_grain_num = 0
        seasonalities_dict = X.get_seasonality_dict()
        for test_seasonality in seasonalities_dict.keys():
            if isinstance(seasonalities_dict[test_seasonality], int):
                grain_num = seasonalities_dict[test_seasonality]
            else:
                grain_num = len(seasonalities_dict[test_seasonality])
            if grain_num > max_grain_num:
                max_grain_num = grain_num
                seasonality = test_seasonality
        if len(seasonalities_dict.keys()) > 1:
            warnings.warn(
                'Different grains have different seasonality, '
                'the mode seasonality of {} will be used.'.format(seasonality))
        return seasonality

    def _fit_one_grain(self, df_one):
        """
        Do the STL decomposition of a single grain and save the result object.
        returned the transformed object.
        If one of grains contains fewer then one dimensions the ValueError is raised.

        :param df_one: The TimeSeriesDataFrame with one grain.
        :type df_one: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`
        :returns: The data frame with season and trend columns.
        :rtype: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`
        :raises: ValueError

        """
        grain_id = self._get_grain_id(df_one)
        if df_one.shape[0] < 2:
            raise ValueError(
                'Grain {} is degenerate time series of exactly one datapoint.'.format(grain_id))
        series_vals = df_one[df_one.ts_value_colname].values
        stl_result = seasonal_decompose(series_vals,
                                        model=self._model_type,
                                        freq=self.seasonality,
                                        two_sided=False)

        self._origins_freqs[grain_id] = (min(
            df_one.time_index.values), df_one.time_index.values[1] - df_one.time_index.values[0])
        self._stls[grain_id] = stl_result
        return self._assign_trend_season(
            df_one, stl_result.seasonal, stl_result.trend)

    def _fit_transform_one_grain(self, df_one):
        """
        Infer the seasonality and trend for single grain.
        In this case we assume that fit data are the same as train data.
        This method is used in the fit_transform.

        """
        stl_result = self._stls[self._get_grain_id(df_one)]
        season_name = df_one.ts_value_colname + STL_SEASON_SUFFIX
        return self._assign_trend_season(
            df_one, stl_result.seasonal, stl_result.trend)

    def _transform_one_grain(self, df_one):
        """
        Infer the seasonality and trend for single grain.
        In this case we assume that fit data are the same as train data.
        This method is used in the fit_transform.

        """
        grain_id = self._get_grain_id(df_one)
        stl_result = self._stls[grain_id]
        season_name = df_one.ts_value_colname + STL_SEASON_SUFFIX
        trend_name = df_one.ts_value_colname + STL_TREND_SUFFIX
        seasonal = pd.Series(df_one.time_index.values).apply(lambda dt: stl_result.seasonal[(
            (dt - self._origins_freqs[grain_id][0]) // self._origins_freqs[grain_id][1]) % self.seasonality])
        assign_dict = {season_name: seasonal.values}
        return df_one.assign(**assign_dict)

    def _assign_trend_season(self, tsdf, ar_season, ar_trend):
        """
        Create the season and trend columns in the data frame.

        :param tsdf: Target data frame.
        :type tsdf: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`
        :param ar_season: seasonality component.
        :type ar_season: np.array
        :param ar_trend: trend component.
        :type ar_trend: np.array

        """
        season_name = tsdf.ts_value_colname + STL_SEASON_SUFFIX
        trend_name = tsdf.ts_value_colname + STL_TREND_SUFFIX

        assign_dict = {season_name: ar_season,
                       trend_name: ar_trend}
        return tsdf.assign(**assign_dict)

    def _get_grain_id(self, X):
        """
        Return the ID used to store the data about given grain.

        :param X: The TimeSeriesDataFrame with the single grain.
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`
        :returns: The string id the concatenation like grain1_grain2_..._grainN.
        :rtype: str

        """
        if isinstance(X.grain_index, pd.core.indexes.base.Index):
            return str(X.grain_index[0])
        #X is MultiIndex
        return "_".join([str(grain[0]) for grain in X.grain_index.levels])

    @property
    def seasonality(self):
        """
        Get seasonality property: the number of periods after which
        the series values tend to repeat.

        :returns: seasonality.
        :rtype: int

        """
        return self._seasonality
