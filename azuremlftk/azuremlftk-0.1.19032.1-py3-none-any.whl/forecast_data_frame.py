"""
A module that contains definition of the ForecastDataFrame class 
and related utility functions.
"""

from ftk import TimeSeriesDataFrame
import pandas as pd
import numpy as np
import json
import scipy
from pydoc import locate
import math
from collections import Iterable
from statsmodels.nonparametric.kde import KDEUnivariate
import uuid


from ftk.verify import (is_iterable_but_not_string, istype,
                        validate_and_sanitize_horizon,
                        validate_and_sanitize_end_dates)
from ftk.exception import (DataFrameValueException,
                           DataFrameTypeException,
                           NotSupportedException,
                           DataFrameMissingColumnException,
                           NotTimeSeriesDataFrameException)
from ftk.verify import Messages
from ftk.metrics.metrics import calc_mape, calc_mae, calc_rmse, \
    calc_smape, calc_mase_single_grain
from ftk.constants import *

from ftk.utils import (flatten_list, standard_deviation_zero_mean,
                       tick_formatter, convert_to_list, grain_level_to_dict,
                       get_period_offsets_from_dates, make_groupby_map,
                       import_plot_and_formatter)
from warnings import warn, catch_warnings, simplefilter

def _scipy_dist_to_dict(dist_obj):
    # unit tests to be added
    """
    .. _scipy.stats.norm: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html

    Convert the scipy parametric distributions to dictionary.

    :param dist_obj: scipy distribution object, e.g `scipy.stats.norm <https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html>`_

    """
    dist_type = type(dist_obj.dist)
    dist_type_str = '.'.join([dist_type.__module__, dist_type.__name__])
    dist_kwds = dist_obj.kwds

    dist_dict = {'dist_type_str': dist_type_str, 'dist_kwds': dist_kwds}
    return dist_dict


def _scipy_dist_from_dict(dist_dict):
    # unit tests to be added.
    """
    Construct a scipy distribution object based on the input dictionary.

    :param dict_obj: dictionary.

    """
    dist_type_str = dist_dict['dist_type_str']
    dist_kwds = dist_dict['dist_kwds']
    dist_type = locate(dist_type_str)()
    dist_obj = dist_type(**dist_kwds)
    return dist_obj


def _scipy_dist_equal(left_dist_obj, right_dist_obj):
    """
    Compare whether two distribution object are equivalent.
    """
    left_dist_dict = _scipy_dist_to_dict(left_dist_obj)
    right_dist_dict = _scipy_dist_to_dict(right_dist_obj)
    if not left_dist_dict['dist_type_str'] == right_dist_dict['dist_type_str']:
        return False
    for key, value in left_dist_dict['dist_kwds'].items():
        if isinstance(value, float):
            if not math.isclose(value, right_dist_dict['dist_kwds'][key], rel_tol=1e-5):
                return False
        else:
            if not value == right_dist_dict['dist_kwds'][key]:
                return False

    return True


class ForecastDataFrame(TimeSeriesDataFrame):
    """
    A subclass of :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`
    with additional properties to identify actual and prediction values.

    ForecastDataFrame is the output type for many estimator 
    'predict' methods.

    .. _scipy.stats: https://docs.scipy.org/doc/scipy/reference/tutorial/stats.html
    .. _pandas.DataFrame: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html

    :param data: See pandas.DataFrame_
    :param index: See pandas.DataFrame_
    :param columns: See pandas.DataFrame_
    :param copy: See pandas.DataFrame_
    :param dtype: See pandas.DataFrame_
    :param time_colname: See :class:`~ftk.time_series_data_frame.TimeSeriesDataFrame`
    :param grain_colnames: See :class:`~ftk.time_series_data_frame.TimeSeriesDataFrame`
    :param group_colnames: See :class:`~ftk.time_series_data_frame.TimeSeriesDataFrame`
    :param origin_time_colname: See :class:`~ftk.time_series_data_frame.TimeSeriesDataFrame`

    :param actual: 
        Column label identifying the actual values of the forecast 
        target quantity. If 'data' is a TimeSeriesDataFrame object, 
        the actual column will be copied from the 'ts_value_colname' 
        column in 'data'.
    :type actual: str

    :param pred_point: 
        Column label identifying point prediction values.
    :type pred_point: str

    :param pred_dist: 
        Column label identifying distribution prediction. This column
        contains objects representing probability distributions, for example
        the rv_frozen object from scipy.stats.
        See distributionobjectexample.py for more examples.
    :type pred_dist: str

    Examples:

    Construct from dictionary

    >>> data1 = {'a': [1,1,0,0], 'b': [0,0,1,1], 'c': pd.to_datetime(
    ...               ['2017-01-01','2017-01-02','2017-01-03','2017-01-04']),
    ...              'd': [0,2,np.nan,14], 'e': [2,1,13,13]}
    >>> df1 = ForecastDataFrame(data1, grain_colnames = ['a','b'],
    ...                         time_colname = 'c', actual = 'd',
    ...                         pred_point='e')
    >>> df1
                        d   e
    c          a b
    2017-01-01 1 0  0.00   2
    2017-01-02 1 0  2.00   1
    2017-01-03 0 1   nan  13
    2017-01-04 0 1 14.00  13

    Construct from pandas.DataFrame_

    >>> data1 = {'a': [1,1,0,0], 'b': [0,0,1,1],
    ...                  'c': pd.to_datetime(['2017-01-01','2017-01-02',
    ...                     '2017-01-03','2017-01-04']),
    ...                  'd': [0,2,np.nan,14], 'e': [2,1,13,13]}
    >>> df1 = pd.DataFrame(data1)
    >>> df2 = ForecastDataFrame(df1, grain_colnames = ['a','b'],
    ...                         time_colname = 'c', actual = 'd',
    ...                         pred_point='e')
    >>> df2
                        d   e
    c          a b
    2017-01-01 1 0  0.00   2
    2017-01-02 1 0  2.00   1
    2017-01-03 0 1   nan  13
    2017-01-04 0 1 14.00  13

    Construct from :class:`~ftk.time_series_data_frame.TimeSeriesDataFrame`

    >>> data1 = {'a': [1,1,0,0], 'b': [0,0,1,1],
    ...                  'c': pd.to_datetime(['2017-01-01','2017-01-02',
    ...                                       '2017-01-03','2017-01-04']),
    ...                  'd': [0,2,np.nan,14], 'e': [2,1,13,13]}
    >>> df1 = TimeSeriesDataFrame(data1, grain_colnames = ['a','b'],
    ...                           time_colname = 'c', ts_value_colname = 'd',
    ...                           group_colnames='a')
    >>> df2 = ForecastDataFrame(df1, pred_point='e')
    >>> df2
                        d   e
    c          a b
    2017-01-01 1 0  0.00   2
    2017-01-02 1 0  2.00   1
    2017-01-03 0 1   nan  13
    2017-01-04 0 1 14.00  13

    """

    @property
    def _constructor(self):
        return ForecastDataFrame

    # the differece between the metadata fields of TimeSeriesDataFrame and
    # ForecastDataFrame is that:
    # (1) ForecastDataFrame does not have 'ts_value_colname'
    # (2) ForecastDataFrame has ['actual', 'pred_point', 'pred_dist']
    _additional_metadata_vs_tsdf = ['actual', 'pred_point', 'pred_dist']
    _metadata = [metadata_field for metadata_field in
                 TimeSeriesDataFrame._metadata if metadata_field !=
                 'ts_value_colname'] + _additional_metadata_vs_tsdf

    def __init__(self, data=None, time_colname=None, index=None, columns=None,
                 dtype=None,
                 copy=False, grain_colnames=None, origin_time_colname=None,
                 group_colnames=None, actual=None, pred_point=None,
                 pred_dist=None):

        if(isinstance(data, TimeSeriesDataFrame)):
            if data.grain_colnames is not None:
                grain_colnames = data.grain_colnames
            if data.group_colnames is not None:
                group_colnames = data.group_colnames
            if data.time_colname is not None:
                time_colname = data.time_colname
            if data.ts_value_colname is not None:
                actual = data.ts_value_colname
            if data.origin_time_colname is not None:
                origin_time_colname = data.origin_time_colname
        if(isinstance(data, ForecastDataFrame)):
            model_class_name = data._model_class_
            param_values_name = data._param_values_
        else:
            model_class_name = None
            param_values_name = None

        super(ForecastDataFrame, self).__init__(data=data, index=index,
                                                columns=columns, dtype=dtype,
                                                copy=copy,
                                                grain_colnames=grain_colnames,
                                                time_colname=time_colname,
                                                ts_value_colname=actual,
                                                group_colnames=group_colnames,
                                                origin_time_colname=origin_time_colname)

        self.actual = self.ts_value_colname
        self.pred_point = pred_point
        self.pred_dist = pred_dist
        with catch_warnings():
            simplefilter('ignore')
            self._model_class_ = model_class_name
            self._param_values_ = param_values_name

        # if data is ForecastDataFrame or instance of subclass of
        # ForecastDataFrame, propagate the additional metadata of
        # ForecastDataFrame properly.
        if isinstance(data, ForecastDataFrame) or \
                issubclass(type(data), ForecastDataFrame):
            for attr_name in self._additional_metadata_vs_tsdf:
                if getattr(self, attr_name) is None:
                    setattr(self, attr_name, getattr(data, attr_name))

    @property
    def actual(self):
        """
        Name of column containing actual values of the forecasting 
        target quantity
        """
        return self.__actual

    @actual.setter
    def actual(self, val):
        my_actual = None
        
        if val is not None:
            if isinstance(val, str):
                if val not in self.columns:
                    raise DataFrameMissingColumnException(
                        '\'actual\' column {0} is not in the data frame'.format(val))

                my_actual = val

            elif isinstance(val, int):
                try:
                    actual_col = self.columns[val]
                except KeyError:
                    raise DataFrameMissingColumnException(
                        'integer column index {0} is invalid'.format(val))

                my_actual = actual_col

            else:
                raise DataFrameTypeException(
                    'Unsupported type {0} given for actual column'.format(type(val)))

        with catch_warnings():
           simplefilter('ignore')
           self.__actual = my_actual

    @property
    def pred_point(self):
        """
        Name of column containing point predictions/forecasts
        """
        return self.__pred_point

    @pred_point.setter
    def pred_point(self, val):
        my_pred = None
        
        if val is not None:
            if isinstance(val, str):
                if val not in self.columns:
                    raise DataFrameMissingColumnException(
                        'pred_point column {0} is not in the data frame'.format(val))

                my_pred = val

            elif isinstance(val, int):
                try:
                    pred_col = self.columns[val]
                except KeyError:
                    raise DataFrameMissingColumnException(
                        'integer column index {0} is invalid'.format(val))

                my_pred = pred_col

            else:
                raise DataFrameTypeException(
                    'Unsupported type {0} given for pred_point column'.format(type(val)))

        with catch_warnings():
           simplefilter('ignore')
           self.__pred_point = my_pred
    
    @property
    def pred_dist(self):
        """
        Name of column containing distribution predictions/forecasts.
        """
        return self.__pred_dist

    @pred_dist.setter
    def pred_dist(self, val):
        my_pred = None

        if val is not None:
            if isinstance(val, str):
                if val not in self.columns:
                    raise DataFrameMissingColumnException(
                        'pred_dist column {0} is not in the data frame'.format(val))

                my_pred = val

            elif isinstance(val, int):
                try:
                    pred_col = self.columns[val]
                except KeyError:
                    raise DataFrameMissingColumnException(
                        'integer column index {0} is invalid'.format(val))

                my_pred = pred_col

            else:
                raise DataFrameTypeException(
                    'Unsupported type {0} given for pred_point column'.format(type(val)))

        with catch_warnings():
           simplefilter('ignore')
           self.__pred_dist = my_pred

    @property
    def _model_class_(self):
        """
        Type of estimator used to generate the forecasts
        """
        return self.___model_class_

    @_model_class_.setter
    def _model_class_(self, val):
        if val is None or isinstance(val, str):
            with catch_warnings():
                simplefilter('ignore')
                self.___model_class_ = val
        else:
            raise DataFrameTypeException(
                    'Unsupported type {0} given for model_class'.format(type(val)))

    @property
    def _param_values_(self):
        """
        Parameters used to make the forecasts
        """
        return self.___param_values_

    @_param_values_.setter
    def _param_values_(self, val):
        if val is None or isinstance(val, (str, dict)):
            with catch_warnings():
                simplefilter('ignore')
                self.___param_values_ = val
        else:
            raise DataFrameTypeException(
                    'Unsupported type {0} given for model_class'.format(type(val)))

    def check_point_forecast_dataframe(self):
        """
        Check whether the :class:`ForecastDataFrame` object 
        has appropriate actual and pred_point attributes.

        Failed checks will raise exceptions.

        :return: None
        :rtype: NoneType
        """
        if self.actual is None:
            raise DataFrameMissingColumnException(
                'the \'actual\' attribute is None in dataframe.')
        if self.pred_point is None:
            raise DataFrameMissingColumnException(
                'the pred_point attribute is None in dataframe.')
        if self.actual not in self.columns:
            raise DataFrameMissingColumnException(
                '\'actual\' column %s not found in dataframe.' % self.actual)
        if self.pred_point not in self.columns:
            raise DataFrameMissingColumnException(
                'pred_point column %s not found in dataframe.' % self.pred)

    def calc_error(self, err_name='MAPE', err_fun=None, by=None, *args, **kargs):
        """
        Calculate error metrics for the ForecastDataFrame using the 'actual'
        and 'pred_point' columns.

        :param err_name: str
            The name of the error metric to calculate.

            The following errors are supported by default:
            * 'MAPE': Mean absolute percentage error.
            * 'MAE': Mean absolute error.
            * 'RMSE': Root-mean-square deviation.
            * 'SMAPE': Symmetric mean absolute percentage error.
            * 'MASE': Mean absolute scaled error
              For MASE calculation, you can specify the keyword argument
              seasonal_freq to specify the number of observations per unit
              of time. By default, seasona_freq=None, which
              calculates the MASE for non-seasonal time series.
        :type err_name: str

        :param err_fun:
            A custom function for calculating an error metric. 

            This function must accept two arguments:
            the first argument is a vector of actual values while the 
            second argument is a vector of prediction values. 
            The function should return a single number representing the error 
            in the prediction.

            See :class: `ftk.metrics.metrics.calc_mape` for an example.
            The function should handle possible exceptions by itself.
            For the errors that are supported by default, there is no need to
            provide err_fun. Please provide your custom err_fun here if you
            want to calculate your custom error metric.
        :type err_fun: function, func(y_true, y_pred)

        :param by:
            This parameter determines groups in the ForecastDataFrame 
            where the error metric will be applied to each group separately.
            Valid inputs for 'by' are the same as those for 
            `pandas.DataFrame.groupby <https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.groupby.html>`_.

            If 'by'=None, a single error across all data frame entries 
            will be returned.

            .. note:: The 'by' argument will not have a impact if 
                      err_name='MASE'. The reason is that the MASE only makes 
                      sense when calculated on a single grain time series.
                      For 'MASE', the 'by' parameter is implicitly set
                      to the 'grain_colnames' property of the ForecastDataFrame.

        :type by: mapping, function, str, or iterable

        :return: Error metrics

        :rtype: float, `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html>`_ 
            if 'by' argument is used

        Example:

        >>> data1 = {'a': [1,1,0,0], 'b': [0,0,1,1],
        ...          'c': pd.to_datetime(['2017-01-01','2017-01-02',
        ...                             '2017-01-03','2017-01-04']),
        ...          'd': [0,2,np.nan,14], 'e': [2,1,13,13]}
        >>> df1 = pd.DataFrame(data1)
        >>> df2 = ForecastDataFrame(df1, grain_colnames=['a', 'b'],
        ...             time_colname='c', actual='d', pred_point='e')
        >>> df2
                            d   e
        c          a b
        2017-01-01 1 0  0.00   2
        2017-01-02 1 0  2.00   1
        2017-01-03 0 1   nan  13
        2017-01-04 0 1 14.00  13
        >>> df2.calc_error(err_name='MAPE', by='a')
            a  MAPE
        0  0  7.14
        1  1 50.00

        """
        self.check_point_forecast_dataframe()

        by_is_none = False
        level = None

        if by is None:
            def by(
                axis_label): return '__identity_grain_level'  # pylint: disable=function-redefined
            by_is_none = True

        if err_fun is None:

            if err_name == 'MAPE':
                err_fun = calc_mape
            elif err_name == 'MAE':
                err_fun = calc_mae
            elif err_name == 'RMSE':
                err_fun = calc_rmse
            elif err_name == 'SMAPE':
                err_fun = calc_smape
            elif err_name == 'MASE':
                err_fun = calc_mase_single_grain
                # for MASE, it only make sense to calculate the MASE by grain,
                # that is to say, for each time series in each grain, exactly
                # one MASE is calculated. What would be the scenario when
                # addtional dimension - horizon is added?
                # should the MASE calculated by grain+cutoff then?
                by = self.grain_colnames
                by_is_none = self.grain_colnames is None

        return_metric = self.groupby(by=by).apply(
            lambda df: err_fun(df[df.actual], df[df.pred_point], *args, **kargs))

        if by_is_none:
            return_metric = return_metric.iloc[0]
        else:
            return_metric.name = err_name
            return_metric = return_metric.reset_index()

        return(return_metric)

    def show_error(self, err_fun=None, err_name=None, by_col=None,
                   col_mapping=None, performance_percent=None, sorted=None,
                   plot_type=None, xlabel=None, ylabel=None, title=None,
                   figure_size=(10, 10), **kwargs):
        """
        Plot error by column specified in 'by_col' or
        'col_mapping' transformation of 'by_col'.

        .. _pandas.DataFrame.plot.kind: https://pandas.pydata.org/pandas-docs/
                                        stable/generated/pandas.DataFrame.
                                        plot.html

        :param err_fun:
            See :meth:`~ForecastDataFrame.calc_error`.
            Default: :meth:`ftk.metrics.metrics.calc_mape`
        :type err_fun: function

        :param err_name:
            See :meth:`~ForecastDataFrame.calc_error`. Default: MAPE
        :type err_name: str

        :param by_col:
            The column name used to group the errors, if col_mapping is
            not provided. Default: TimeSeriesDataFrame.grain_colnames
        :type by_col: str

        :param col_mapping:
            A function to be applied on by_col and create a new column
            used to group the errors. Default: None
        :type col_mapping: function

        :param performance_percent:
            A tuple that specifies a performance percentage interval for
            selecting a subset of 'by_col's to plot. For example, if you
            want to plot grains with bottom 5% errors, set this parameter
            to (0, 0.05). If you want to plot grains with top 5% errors,
            set this parameter to (0.95, 1).
        :type performance_percent: tuple

        :param sorted:
            A flag indicating if the errors are sorted in the output plot.
            By default, errors are not sorted. Accepted values are
            'ascending' and 'descending'.
        :type sorted:
            str

        :param plot_type:
            Type of plot. See pandas.DataFrame.plot.kind_ Default: 'bar'
        :type plot_type: str

        :param xlabel:
            Label of the x axis. If not set by the user, 'by_col' or the
            'col_mapping' transformation of 'by_col' is used.
        :type xlabel: str

        :param ylabel:
            Label of the y axis. If not set by the user, 'err_name' is used.
        :type ylabel: str

        :param title:
            title of the plot. If not set by the user, a title is created
            from 'err_name' and 'by_col'
        :type title: str

        :param figure_size:
            Size of the figure given by a tuple.
        :type figure_size: tuple

        :return:
            A tuple containg a figure object and an axis objects.
            The figure object can be further customized and saved.
            The axis object can be used to customize the plot.
        :rtype: Tuple (figure, axis)


        .. note:: This function adds a new err_name column to the input data
            frame. If col_mapping is given, a new
            by_col_<column_mapping function name> is added to the input data
            frame.

        :Examples:

        Create a ForecastDataFrame:

        >>> forecast_df = ForecastDataFrame(data, grain_colnames='Store',
        ...    time_colname='Date', actual='Sales',pred_point='Sales_pred',
        ...    pred_dist='Sales_dist')

        Show error using default options

        >>> fig, ax = forecast_df.show_error()

        Customize returned plot

        >>> ax.set(ylabel='Average MAPE')
        >>> ax.set(title='Average MAPE by Store')

        Pass custom absolute error function:

        >>> def calc_abs_error(y_true, y_pred):
        ...     abs_error = abs(y_true - y_pred)
        ...     return abs_error

        >>> fig, ax = forecast_df.show_error(err_fun=calc_abs_error,
        ... err_name='Absolute Error', xlabel='Store ID',
        ... ylabel='Average Absolute Error', title='Average Absolute Error by \
        ... Store')

        Pass custom mapping of group by column:

        >>> import math
        >>> def mapping(x):
        ...    if x <= 0:
        ...        return -1
        ...    return math.floor(math.log(x))

        >>> fig, ax = forecast_df.show_error(by_col='Sales',
        ...            col_mapping=mapping, xlabel='floor(log(Sales))',
        ...            ylabel='MAPE',title='MAPE by floor(log(Sales))')

        """
        plt, FuncFormatter = import_plot_and_formatter()
        # Set default argument values
        if err_fun is None:
            err_fun = calc_mape

        if err_name is None:
            err_name = 'MAPE'

        if by_col is None:
            by_col = self.grain_colnames

        if plot_type is None:
            plot_type = 'bar'

        formatter = FuncFormatter(tick_formatter)

        # Apply mapping if given
        if col_mapping:
            by_col_new = by_col + '_' + col_mapping.__name__
            self[by_col_new] = self[by_col].apply(col_mapping)
            by_col = by_col_new

        if xlabel is None:
            xlabel = by_col

        if ylabel is None:
            ylabel = err_name

        if title is None:
            title = '{0} by {1}'.format(err_name, by_col)

        # Calculate error
        err_by_col = self.calc_error(err_name=err_name,
                                     err_fun=err_fun,
                                     by=by_col)

        # Compute subset of data to plot
        if performance_percent is not None:
            if performance_percent[0] < 0 or performance_percent[1] > 1 or \
                    performance_percent[1] <= performance_percent[0]:
                raise ValueError('The performance_percent interval is not '
                                 'valid. Values must be between 0 and 1, '
                                 'and the second element must be greater than '
                                 'the first element.')
            err_by_col.sort_values(err_name, inplace=True)
            err_count = err_by_col.shape[0]
            err_start = math.floor(err_count * performance_percent[0])
            err_end = math.ceil(err_count * performance_percent[1])
            err_by_col = err_by_col.iloc[err_start:err_end, ]

        if sorted:
            if sorted == 'ascending':
                err_by_col.sort_values(err_name, inplace=True)
            elif sorted == 'descending':
                err_by_col.sort_values(err_name, inplace=True, ascending=False)
            else:
                warn("The value of the 'sorted' argument must be 'ascending' "
                     "or 'descending'. Invalid value is passed and ignored")
        # Create the plot
        fig, ax = plt.subplots(figsize=figure_size)

        # For Pandas 0.23, plot x axis can be defined by only a single column.
        # Need to condense the 'by columns' into a single column
        # First, make the name of the combined column via str concat.
        # Then, use a groupby map to condense the columns together.
        # Merge back into the error data frame and plot.
        if is_iterable_but_not_string(by_col):
            by_cols_combined_name = '-'.join(by_col)
        else:
            by_cols_combined_name = by_col

        gby_map = make_groupby_map(err_by_col, by_col)
        gby_map.name = by_cols_combined_name
        err_by_col = (err_by_col
                      .drop(by_col, axis=1)
                      .merge(gby_map.to_frame(), left_index=True, right_index=True))

        err_by_col.plot(kind=plot_type, y=err_name, 
                        x=by_cols_combined_name, ax=ax, **kwargs)
       
        ax.yaxis.set_major_formatter(formatter)
        ax.set(xlabel=xlabel, ylabel=ylabel, title=title)

        return fig, ax

    def plot_error_density(self, err_name=None, err_fun=None, by_col=None,
                           weighted_density=False, weighted_by=None,
                           xlabel=None, ylabel=None, title=None,
                           figure_size=(10, 10), **kwargs):
        """
        .. py:method:: plot_error_density

        Plot the kernel density estimate(kde) of the errors.

        .. _statsmodels.nonparametric.kde.KDEUnivariate: http://www.statsmodels.org/dev/generated/statsmodels.nonparametric.kde.KDEUnivariate.html

        :param err_fun:
            See :meth:`ForecastDataFrame.calc_error`.
            Default: :meth:`ftk.metrics.metrics.calc_mape`
        :type err_fun: function

        :param err_name:
            See :meth:`ForecastDataFrame.calc_error`. Default: MAPE
        :type err_name: str

        :param by_col:
            The column name used to group the errors.Default:
            TimeSeriesDataFrame.grain_colnames
        :type by_col: str

        :param weighted_density:
            If True, the kernel density is will be weighted by the column
            specified by 'weighted_by'. This is useful when the scale
            of the data of different grains vary a lot.
        :type weighted_density: bool

        :param weighted_by:
            The column to weight the kernel density on.
        :type weighted_by: str

        :param xlabel:
            Label of the x axis. If not set by the user, 'err_name' is used.
        :type xlabel: str

        :param ylabel:
            Label of the y axis. If not set by the user, 'Probability
            Density' is used.
        :type ylabel: str

        :param title:
            title of the plot. If not set by the user, a title is created
            from 'err_name'.
        :type title: str

        :param figure_size:
            Size of the figure given by a tuple.
        :type figure_size: tuple

        :return:
            A tuple containg a figure object and an axis objects.
            The figure object can be further customized and saved.
            The axis object can be used to customize the plot.
        :rtype: Tuple (figure, axis)

        """
        from matplotlib import pyplot as plt
        # Set default argument values
        if err_fun is None:
            err_fun = calc_mape

        if err_name is None:
            err_name = 'MAPE'

        if by_col is None:
            by_col = self.grain_colnames

        if xlabel is None:
            xlabel = err_name

        if ylabel is None:
            ylabel = 'Probability Density'

        if weighted_by is None:
            weighted_by = self.actual

        if title is None:
            if weighted_density:
                title = '{2} Weighted Probability Density of {0} by {' \
                        '1}'.format(err_name, by_col, weighted_by)
            else:
                title = 'Probability Density of {0} by {1}'.format(
                    err_name, by_col)

        # Calculate error
        err_by_col = self.calc_error(err_name=err_name,
                                     err_fun=err_fun,
                                     by=by_col)

        density = KDEUnivariate(err_by_col[err_name])
        if weighted_density:
            mean_by_col = self[weighted_by].groupby(by=by_col).mean()
            mean_by_col = pd.DataFrame(mean_by_col)
            mean_by_col.reset_index(inplace=True)
            err_by_col = err_by_col.merge(mean_by_col, on=by_col, how='left')
            density.fit(fft=False, weights=err_by_col[weighted_by])
        else:
            density.fit()

        fig, ax = plt.subplots(figsize=figure_size)
        ax.plot(density.support, density.density, **kwargs)

        ax.set(xlabel=xlabel, ylabel=ylabel, title=title)

        return fig, ax

    def plot_error_histogram(self, err_name=None, err_fun=None, by_col=None,
                             col_mapping=None, xlabel=None, ylabel=None,
                             title=None, figure_size=(10, 10), **kwargs):
        """
        .. py:method:: plot_error_histogram

        Plot error histogram by column specified in 'by_col' or
        'col_mapping' transformation of 'by_col'.

        :param err_fun:
            See :meth:`ForecastDataFrame.calc_error`.
            Default: :meth:`ftk.metrics.metrics.calc_mape`
        :type err_fun: function

        :param err_name:
            See :meth:`ForecastDataFrame.calc_error`. Default: MAPE
        :type err_name: str

        :param by_col:
            The column name used to group the errors, if col_mapping is
            not provided. Default: TimeSeriesDataFrame.grain_colnames
        :type by_col: str

        :param col_mapping:
            A function to be applied on by_col and create a new column
            used to group the errors. Default: None
        :type col_mapping: function

        :param xlabel:
            Label of the x axis. If not set by the user, 'err_name' is used.
        :type xlabel: str

        :param ylabel:
            Label of the y axis. If not set by the user, ylabel is created
            from by_col.
        :type ylabel: str

        :param title:
            title of the plot. If not set by the user, a title is created
            from 'err_name' and 'by_col'
        :type title: str

        :param figure_size:
            Size of the figure given by a tuple.
        :type figure_size: tuple

        :return:
            A tuple containg a figure object and an axis objects.
            The figure object can be further customized and saved.
            The axis object can be used to customize the plot.
        :rtype: Tuple (figure, axis)


        .. note:: This function adds a new err_name column to the input data
            frame. If col_mapping is given, a new column
            by_col_<column_mapping function name> is added to the input data
            frame.
        """
        plt, FuncFormatter = import_plot_and_formatter()
        # Set default argument values
        if err_fun is None:
            err_fun = calc_mape

        if err_name is None:
            err_name = 'MAPE'

        if by_col is None:
            by_col = self.grain_colnames

        formatter = FuncFormatter(tick_formatter)

        if col_mapping is not None:
            by_col_new = by_col + '_' + col_mapping.__name__
            self[by_col_new] = self[by_col].apply(col_mapping)
            by_col = by_col_new

        if xlabel is None:
            xlabel = err_name

        if ylabel is None:
            ylabel = '{} Count'.format(by_col)

        if title is None:
            title = '{0} Histogram by {1}'.format(err_name, by_col)

        # Calculate error
        err_by_col = self.calc_error(err_name=err_name,
                                     err_fun=err_fun,
                                     by=by_col)

        fig, ax = plt.subplots(figsize=figure_size)
        err_by_col.hist(column=err_name, ax=ax, **kwargs)

        ax.yaxis.set_major_formatter(formatter)
        ax.set(xlabel=xlabel, ylabel=ylabel, title=title)

        return fig, ax

    def plot_forecast_sum(self, by_horizon=False, horizon='All',
                          xlabel=None, ylabel=None, title=None,
                          legend=None, figure_size=(10, 10), **kwargs):
        """
        .. py:method:: plot_forecast_sum

        Plot the sum of 'pred_point' vs. sum of 'actual'.

        :param by_horizon:
            If True, plot one figure for each forecast horizon. This is only
            useful when you have multiple forecasts for the same date
            generated from different forecast origin dates, i.e. multiple
            forecast horizons for the same date. In contrast, if you only have
            multiple horizon forecasts generated from the same forecast
            origin date, it's not meaningful to create a separate figure for
            each horizon.
        :type by_horizon: bool

        :param horizon:
            If by_horizon is True, the horizons to plot. By default,
            all horizons are plotted, which will generate h figures if
            you have h horizons in total.
        :type horizon: pd.Timedelta

        :param xlabel:
            Label of the x axis. If not set by the user, the value of the
            metadata 'time_colname' is used.
        :type xlabel: str

        :param ylabel:
            Label of the y axis. If not set by the user, the value of the
            metadata 'actual' is used.
        :type ylabel: str

        :param title:
            Title of the plot. If not set by the user, a title is created
            from the value of metadata 'actual'.
        :type title: str

        :param legend:
            Legend for annotating the plot.
        :type legend: tuple, str

        :param figure_size:
            Size of the figure given by a tuple.
        :type figure_size: tuple

        :return:
            A list of (figure object, axis object) tuples.
            The figure objects can be further customized and saved.
            The axis objects can be used to customize the plots.
        :rtype: list of (figure, axis)

        """
        plt, FuncFormatter = import_plot_and_formatter()
        if xlabel is None:
            xlabel = self.time_colname

        if ylabel is None:
            if self.actual:
                ylabel = self.actual
            else:
                ylabel = 'Forecast'

        if title is None:
            if self.actual:
                title = 'Total Forecasted {0} vs. Total Actual {0}'\
                    .format(self.actual)
            else:
                title = 'Total Forecast'
        formatter = FuncFormatter(tick_formatter)

        fig_ax_list = []

        if by_horizon:
            self_grouped = self.groupby(self.horizon)
            if horizon == 'All':
                horizon = list(self_grouped.groups.keys())
            else:
                horizon = convert_to_list(horizon)
            for h in horizon:
                group_cur = self_grouped.get_group(h)
                if self.actual:
                    forecast_sum = group_cur[[self.actual, self.pred_point]] \
                        .groupby_index_names(self.time_colname).sum()
                else:
                    forecast_sum = group_cur[[self.pred_point]] \
                        .groupby_index_names(self.time_colname).sum()
                forecast_sum.reset_index(inplace=True)
                fig, ax = plt.subplots(figsize=figure_size)
                if self.actual:
                    ax.plot(forecast_sum[self.time_colname],
                            forecast_sum[self.actual], '-', **kwargs)
                ax.plot(forecast_sum[self.time_colname],
                        forecast_sum[self.pred_point], 'g-', **kwargs)
                ax.set(xlabel=xlabel, ylabel=ylabel,
                       title=title + ' - Horizon: ' + str(h))
                if legend is None:
                    ax.legend()
                else:
                    ax.legend(legend)
                ax.yaxis.set_major_formatter(formatter)
                fig_ax_list.append((fig, ax))
        else:
            if self.actual:
                forecast_sum = self[[self.actual, self.pred_point]]\
                    .groupby_index_names(self.time_colname).sum()
            else:
                forecast_sum = self[[self.pred_point]]\
                    .groupby_index_names(self.time_colname).sum()
            forecast_sum.reset_index(inplace=True)
            fig, ax = plt.subplots(figsize=figure_size)
            if self.actual:
                ax.plot(forecast_sum[self.time_colname],
                        forecast_sum[self.actual], '-', **kwargs)
            ax.plot(forecast_sum[self.time_colname],
                    forecast_sum[self.pred_point], 'g-', **kwargs)
            ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
            if legend is None:
                ax.legend()
            else:
                ax.legend(legend)
            ax.yaxis.set_major_formatter(formatter)
            fig_ax_list.append((fig, ax))

        return fig_ax_list

    def _plot_single_grain_forecast(self, df, prediction_interval,
                                    figure_size, **kwargs):
        from matplotlib import pyplot as plt
        fig, ax = plt.subplots(figsize=figure_size)
        if self.actual:
            ax.plot(df.time_index,
                    df[self.actual], '-', **kwargs)
        ax.plot(df.time_index,
                df[self.pred_point], 'g-', **kwargs)
        if prediction_interval:
            ax.plot(df.time_index,
                    df['CI Lower Bound'], 'y--', **kwargs)
            ax.plot(df.time_index,
                    df['CI Upper Bound'], 'c--', **kwargs)
        return fig, ax

    def plot_forecast_by_grain(self, grains=[], prediction_interval=False,
                               alpha=0.95, by_horizon=False, horizon='All',
                               performance_percent=None,
                               err_name=None, err_fun=None,
                               xlabel=None, ylabel=None, title=None,
                               legend=None, figure_size=(10, 10), **kwargs):
        """
        .. py:method:: plot_forecast_by_grain

        Plot 'pred_point' vs. 'actual' by grain.

        :param grains:
            Grains to plot.
            If not specified by the user, only the first
            grain is plotted. This avoids creating a large number of figures
            accidentally.
            If set to 'All', one figure is created for each grain.
        :type grains: Iterable, str, tuple

        :param prediction_interval:
            If True and 'pred_dist' column is populated with prediction
            distribution, the prediction interval is plotted.
        :type prediction_interval: bool

        :param alpha:
            Alpha value of prediction interval.
        :type alpha: numeric

        :param by_horizon:
            If True, plot one figure for each forecast horizon. This is only
            useful when you have multiple forecasts for the same date
            generated from different forecast origin dates, i.e. multiple
            forecast horizons for the same date. In contrast, if you only have
            multiple horizon forecasts generated from the same forecast
            origin date, it's not meaningful to create a separate figure for
            each horizon.
        :type by_horizon: bool

        :param performance_percent:
            A tuple that specifies a performance percentage interval for
            selecting a subset of grains to plot. For example, if you want
            to plot grains with bottom 5% errors, set this parameter
            to (0, 0.05). If you want to plot grains with top 5% errors,
            set this parameter to (0.95, 1).

        :param err_fun:
            Error function used to compute errors for selecting grains
            within the performance_percent interval.
            See :meth:`ForecastDataFrame.calc_error`.
            Default: :meth:`ftk.metrics.metrics.calc_mape`
        :type err_fun: function

        :param err_name:
            If performance_percent is set, this function adds a new
            err_name column to the input data frame.
            See :meth:`ForecastDataFrame.calc_error`. Default: MAPE
        :type err_name: str

        :param horizon:
            If by_horizon is True, the horizons to plot. By default,
            all horizons are plotted, which will generate h figures if
            you have h horizons in total.
        :type horizon: pd.Timedelta

        :param xlabel:
            Label of the x axis. If not set by the user, the value of the
            metadata 'time_colname' is used.
        :type xlabel: str

        :param ylabel:
            Label of the y axis. If not set by the user, the value of the
            metadata 'actual' is used.
        :type ylabel: str

        :param title:
            title of the plot. If not set by the user, a title is created
            from the value of metadata 'actual'.
        :type title: str

        :param legend:
            Legend for annotating the plot.
        :type legend: tuple, str

        :param figure_size:
            Size of the figure given by a tuple.
        :type figure_size: tuple

        :return:
            A list of (figure object, axis object) tuples.
            The figure objects can be further customized and saved.
            The axis objects can be used to customize the plots.
        :rtype: list of (figure, axis)

        """
        from matplotlib.ticker import FuncFormatter
        # When grain_colnames is not in index, selecting a specific grain
        # is hard. So we require the user to set grain_colnames as index to
        # use this function.
        if self.grain_colnames:
            for g in self.grain_colnames:
                if g not in self.grain_index.names:
                    raise Exception('grain colname {0} is not in the '
                                    'index. Set {0} as an index level and '
                                    'try again.'). format(g)
        else:
            warn('"grain_colnames" is not set, assuming a single grain.')

        if xlabel is None:
            xlabel = self.time_colname

        if ylabel is None:
            if self.actual:
                ylabel = self.actual
            else:
                ylabel = 'Forecast'

        if title is None:
            if self.actual:
                title = 'Forecasted {0} vs. Actual {0}'.format(self.actual)
            else:
                title = 'Forecast'

        if err_fun is None:
            err_fun = calc_mape

        if err_name is None:
            err_name = 'MAPE'

        formatter = FuncFormatter(tick_formatter)

        if performance_percent is not None:
            if self.grain_colnames:
                err_by_grain = self.calc_error(err_name=err_name,
                                               err_fun=err_fun,
                                               by=self.grain_colnames)

                # Compute subset of data to plot
                if performance_percent[0] < 0 or \
                        performance_percent[1] > 1 \
                        or performance_percent[1] \
                        <= performance_percent[0]:
                    raise ValueError('The performance_percent interval is not '
                                     'valid. Values must be between 0 and 1, '
                                     'and the second element must be greater '
                                     'than the first element.')
                err_by_grain.sort_values(err_name, inplace=True)
                err_count = err_by_grain.shape[0]
                err_start = math.floor(err_count * performance_percent[0])
                err_end = math.ceil(err_count * performance_percent[1])
                grains_to_plot = err_by_grain.iloc[err_start:err_end, ]
            else:
                warn('"grain_colnames" is not set, can not plot forecast of a '
                     'subset of grains.')
        if performance_percent is not None and self.grain_colnames:
            grains = grains_to_plot[self.grain_colnames].values.tolist()
            grains = [tuple(g) for g in grains]
        elif len(grains) == 0:
            warn('No grains are specified, plotting the first grain.')
            grains = [self.grain_index[0]]
        elif grains == 'All':
            grains = list(self.grain_index.unique())
        # When user provides a single grain with multiple grain_colnames
        elif is_iterable_but_not_string(grains) and len(self.grain_colnames) \
                > 1 and not isinstance(grains[0], Iterable):
            grains = [grains]
        else:
            grains = convert_to_list(grains)

        # Subset the data frame
        self_subset = self.subset_by_grains(grains)
        columns_to_use = [self.pred_point]
        if self.actual:
            columns_to_use.append(self.actual)

        if by_horizon:
            horizon_col = str(uuid.uuid4())
            self_subset = self_subset.assign(
                **{horizon_col: self_subset.horizon})
            columns_to_use.append(horizon_col)

        if self.pred_dist:
            columns_to_use.append(self.pred_dist)

        self_subset = self_subset[columns_to_use]

        # Extract prediction interval bounds
        if prediction_interval:
            if self.pred_dist and \
                    not any(pd.isnull(self_subset[self.pred_dist])):
                self_subset['CI Lower Bound'] = \
                    [x.interval(alpha=alpha)[0]
                     for x in self_subset[self.pred_dist].values]
                self_subset['CI Upper Bound'] = \
                    [x.interval(alpha=alpha)[1]
                     for x in self_subset[self.pred_dist].values]
            elif self.pred_dist:
                prediction_interval = False
                warn('Some or all values of the {0} column is NA. The '
                     'prediction interval can not be plotted'.format(
                         self.pred_dist))
            else:
                prediction_interval = False
                warn('The "pred_dist" metadata of the ForecastDataFrame is '
                     'not set. The prediction interval can not be plotted')
        fig_ax_list = []
        if self.grain_colnames:
            if by_horizon:
                self_grouped = self_subset.groupby(horizon_col)
                if horizon == 'All':
                    horizon = list(self_grouped.groups.keys())
                else:
                    horizon = convert_to_list(horizon)
                for h in horizon:
                    group_cur = self_grouped.get_group(h)
                    for g in grains:
                        grain_df_cur = group_cur.subset_by_grains(g)

                        fig, ax = self._plot_single_grain_forecast(
                            grain_df_cur, prediction_interval, figure_size,
                            **kwargs)

                        ax.set(xlabel=xlabel, ylabel=ylabel,
                               title=title + ' - Grain: ' + str(g)
                               + ' - Horizon: ' + str(h))
                        if legend is None:
                            ax.legend()
                        else:
                            ax.legend(legend)
                        ax.yaxis.set_major_formatter(formatter)
                        fig_ax_list.append((fig, ax))
            else:
                for g in grains:
                    grain_df_cur = self_subset.subset_by_grains(g)
                    fig, ax = self._plot_single_grain_forecast(
                        grain_df_cur, prediction_interval, figure_size, **kwargs)
                    ax.set(xlabel=xlabel, ylabel=ylabel,
                           title=title + ' - Grain: ' + str(g))
                    if legend is None:
                        ax.legend()
                    else:
                        ax.legend(legend)
                    ax.yaxis.set_major_formatter(formatter)
                    fig_ax_list.append((fig, ax))
        else:
            fig, ax = self._plot_single_grain_forecast(
                self_subset, prediction_interval, figure_size, **kwargs)
            ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
            if legend is None:
                ax.legend()
            else:
                ax.legend(legend)
            ax.yaxis.set_major_formatter(formatter)
            fig_ax_list.append((fig, ax))

        return fig_ax_list

    def to_json(self):
        """
        Serialize the ForecastDataFrame as a JSON string.

        :return: JSON representation of the ForecastDataFrame
        :rtype: str

        """
        json_dict = {}

        # add metadata attributes to json_dict
        for attribute in ForecastDataFrame._metadata:
            json_dict[attribute] = getattr(self, attribute)
        # pylint: disable=bad-super-call
        # get the names of columns that contains datetime type data
        datetime_colnames_all = list(super(TimeSeriesDataFrame, self).reset_index(
        ).select_dtypes(include=[np.datetime64]).columns.values)
        json_dict['datetime_colnames_all'] = datetime_colnames_all

        fcdf_data = super(TimeSeriesDataFrame, self).reset_index()
        if self.pred_dist is not None:
            if type(fcdf_data[self.pred_dist].iloc[0]).__module__ == \
                    'scipy.stats._distn_infrastructure':
                fcdf_data[self.pred_dist] = fcdf_data[self.pred_dist].apply(
                    _scipy_dist_to_dict)

        json_dict['data'] = super(
            TimeSeriesDataFrame, fcdf_data).to_json(orient='split')
        json_str = json.dumps(json_dict)
        return json_str

    @classmethod
    def construct_from_json(cls, json_str):
        """
        Construct ForecastDataFrame from a JSON string.

        The input string should conform with the serialization format
        used in ForecastDataFrame.to_json().

        :param json_str: Input json string.
        :type json_str: str

        :return: Constructed data frame
        :rtype: TimeSeriesDataFrame

        Construct ForecastDataFrame based on json string, which should conform
        with the output from ForecastDataFrame.to_json().

        :param json_str: String.
            input json string.

        """

        json_dict = json.loads(json_str)

        if isinstance(json_dict, str):
            # this is to handle the result string coming from
            # operationalization web service call, which needs two json.loads
            json_dict = json.loads(json_dict)
            if not isinstance(json_dict, dict):
                raise ValueError('Input of type {} can not be converted json '
                                 'dictionary'.format(type(json_str)))

        fcdf_data = pd.read_json(
            json_dict['data'], orient='split',
            convert_dates=json_dict['datetime_colnames_all'])

        if json_dict['pred_dist'] is not None:
            if isinstance(fcdf_data[json_dict['pred_dist']].iloc[0], dict):
                fcdf_data[json_dict['pred_dist']] = \
                    fcdf_data[json_dict['pred_dist']].apply(
                        _scipy_dist_from_dict)

        json_dict['data'] = fcdf_data

        # delete the datetime_colnames_all attribute, which is not needed
        # for the constructor
        json_dict.pop('datetime_colnames_all')

        fcdf = cls(**json_dict)
        return fcdf

    def equals(self, other):
        # unit tests to be added.
        """
        Check whether two ForecastDataFrame are equal. 
        This is designed to be used in unit tests.

        :param other: 
            The ForecastDataFrame to compare against.
        :type other: ForecastDataFrame

        :return: True if the frame is equal to 'other'
        :rtype: boolean
        """

        # check the equality of metadata added on top of ForecastDataFrame
        for attribute_name in list(set(ForecastDataFrame._metadata) -
                                   set(TimeSeriesDataFrame._metadata)):
            if not getattr(self, attribute_name) == getattr(other, attribute_name):
                return False

        if self.pred_dist is not None:
            self_drop_pred_dist = self.drop(self.pred_dist, axis=1)
            other_drop_pred_dist = other.drop(other.pred_dist, axis=1)
            if not super(ForecastDataFrame, self_drop_pred_dist).equals(
                    other_drop_pred_dist):
                return False

            self_pred_dist_type = type(self[self.pred_dist].iloc[0]).__module__
            other_pred_dist_type = type(
                other[other.pred_dist].iloc[0]).__module__

            if not self_pred_dist_type == other_pred_dist_type:
                return False

            if self_pred_dist_type == 'scipy.stats._distn_infrastructure':
                # check equality of the distribution column
                # If the distribution column does not store distribution
                # object, then it is really a not meaningful column,
                # we don't check that.
                # we sort the index before the comparison so that the
                # comparison is proper.
                pred_dist_df = pd.concat(
                    [self[self.pred_dist].sort_index().reset_index(drop=True),
                     other[other.pred_dist].sort_index().reset_index(drop=True)],
                    axis=1)
                pred_dist_df.columns = ['left', 'right']
                if not pred_dist_df.apply(
                        lambda x: _scipy_dist_equal(x['left'], x['right']),
                        axis=1).all():
                    return False
        else:
            if not super(ForecastDataFrame, self).equals(other):
                return False

        return True

    def calc_pred_dist(self):
        """
        Calculate distribution forecasts via backtesting
        from rolling origin cross-validation.  Prediction 
        intervals are estimated using a gaussian distribution.
        The mean of the distribution for each row is 
        `pred_point` and the standard deviation is estimated 
        using the errors frow rows of the ForecastDataFrame 
        whose `time_index` is earlier than that row's 
        `origin_time`.  Because earlier time points are used 
        to create distributions for later time points, 
        prediction intervals will not be estimated for the 
        earliest values in the ForecastDataFrame.

        The distributions are stored in the ForecastDataFrame
        'pred_dist' column.

        :return: None
        :rtype: NoneType
        """
        from ftk.model_selection import RollingOriginValidator
        from scipy.stats import norm

        # Make sure the FDF is properly formatted
        if self.pred_point is None:
            raise DataFrameMissingColumnException(
                "pred_point must be set to perform backtesting")
        if self.actual is None:
            raise DataFrameMissingColumnException(
                "actual must be set to perform backtesting")
        if self.pred_dist is not None:
            warn("calc_pred_ind called but pred_dist is already set." +
                 " Previous pred_dist will be overwritten.", UserWarning)
            pred_dist_col = self.pred_dist
        else:
            self["PredictionDistribution"] = None
            self.pred_dist = "PredictionDistribution"

        # Compute the number of folds for CV
        if self.origin_time_colname is not None:
            min_time_index = min(self.time_index)
            origin_greater = self.origin_time_index[
                self.origin_time_index >= min_time_index]
            num_cv_folds = len(origin_greater.unique())
        else:
            num_cv_folds = len(self.time_index.unique()) - 1
        if num_cv_folds < 1:
            raise DataFrameValueException(
                "Not enough backtesting data to compute prediction intervals")

        # Split data for training and testing sets
        rollcv = RollingOriginValidator(n_splits=num_cv_folds)
        splits = rollcv.split(self)

        for train_cv, test_cv in splits:
            train_df = self.iloc[train_cv, :]
            # Now we compute the standard deviation for the prediction interval
            # distribution for each grouping.
            error_stdev = train_df._stdev_by_slicekey()
            # Next we need to align these errors with the test data
            stdev_aligned = self.iloc[test_cv, :]._get_slice_vals(error_stdev)
            # Assign the distributions to the correct rows
            # NOTE: this is ugly as sin, if someone can help me figure out
            #       how to combine a .iloc and a .loc more nicely,
            #       I would love the suggestion.
            means = self.iloc[test_cv][self.pred_point]
            dist_col = [scipy.stats.norm(loc=m, scale=s) if not np.isnan(s) else None
                        for m, s in zip(means.values, stdev_aligned.values)]
            self.loc[self.index[test_cv], self.pred_dist] = dist_col

    def _stdev_by_slicekey(self):
        """
        Utility function for calc_pred_dist to get the standard deviation
        of errors for each slice key.
        """
        # We need to group by the slice key, but we need to use horizon
        # instead of origin_time.
        groupings = [self.index.get_level_values(
            col) for col in self.slice_key_colnames if col != self.origin_time_colname]
        if self.origin_time_colname is not None:
            groupings.append(self.horizon)
        self_group = self.groupby(groupings)
        # Now we compute the standard deviation for the prediction interval
        # distribution for each grouping.
        error_stdev = self_group.apply(
            lambda g: standard_deviation_zero_mean(g[self.pred_point] - g[self.actual]))
        return(error_stdev)

    def _get_slice_vals(self, new_data):
        """
        Utility function for calc_pred_dist to align data between training
        and testing data.
        """
        # First we need to get a data frame with just our indexing values
        index_df = pd.DataFrame(self, copy=True).reset_index()
        index_keys = [col for col in self.slice_key_colnames
                      if col != self.origin_time_colname]
        index_df = index_df[index_keys]
        index_df['horizon'] = self.horizon
        index_keys.append('horizon')
        merge_index = [k for k in index_keys if k in new_data.index.names]
        # This merge step aligns the new data values with the indexes in self
        ret_values = pd.merge(index_df,
                              new_data.to_frame(
                                  'slice_value_column').reset_index(),
                              on=merge_index, how='left')
        ret_values.set_index(index_keys)
        return ret_values['slice_value_column']

    def __finalize__(self, other, method=None, **kwargs):
        """propagate metadata from other to self """
        # If concatenating two ForecastDataFrames from different methods
        # create and return a MultiForecastDataFrame
        if method == 'concat':
            if all(isinstance(x, ForecastDataFrame) for x in other.objs):
                model_tuples = [(x._model_class_, x._param_values_) for x in other.objs]
                if model_tuples.count(model_tuples[0]) != len(model_tuples):
                    from ftk import MultiForecastDataFrame
                    # Get the model names and create a column
                    # The `sum` call here is used to concatenate the list of lists
                    # produced by the list comprehension
                    model_names = sum([[x._model_class_]*x.shape[0] for x in other.objs], [])
                    self[UNIFORM_MODEL_NAME_COLNAME] = model_names
                    model_dict = {'model_class': UNIFORM_MODEL_NAME_COLNAME}
                    # If model params are not all none get them and make a column
                    model_params = sum([[x._param_values_]*x.shape[0] for x in other.objs], [])
                    if not all([x is None for x in model_params]):
                        self[UNIFORM_MODEL_PARAMS_COLNAME] = model_params
                        model_dict['param_values'] = UNIFORM_MODEL_PARAMS_COLNAME
                    meta_dict = other.objs[0]._get_metadata()
                    self = MultiForecastDataFrame._internal_ctor(self, model_colnames=model_dict, **meta_dict)

        return super(ForecastDataFrame, self).__finalize__(other, method, **kwargs)

################################################################################


def construct_forecast_df_from_train_tsdf(X, horizon=None, future_date=None,
                                          include_all=True, **kwargs):
    """
    Creates a ForecastDataFrame to hold forecast from a training
    TimeSeriesDataFrame

    :param X: 
        The TimeSeriesDataFrame that would be used to train a model
    :type X: TimeSeriesDataFrame

    :param horizon: 
        The period indices past the last timepoint for each grain
        that the ForecastDataFrame should hold. Can be either a single integer, 
        an iterable of integers, or a dict whose keys are grains of `X` and 
        values are either ints or iterables of ints. Defaults to 1.
    :type horizon: int, iterable, or dict

    :param future_date:
        Dates for which forecasts are sought. Can be either a single datetime, 
        an iterable of datetimes, or a dict whose keys are grains of `X` 
        and values are either datetimes or iterables of datetimes.
    :type future_date: int, iterable, or dict

    :param include_all:
        If `True`, all horizons between min and max of `horizon` will be 
        returned, otherwise only the requested horizons will be returned.
        Works similarly for `future_date`s. Defaults to True.
    :type include_all: bool

    :param **kwargs:
        Additional parameters to be passed to ForecastDataFrame
    :type **kwargs: dict

    :return:
        ForecastDataFrame with rows to hold forecasts for either all requested
        `horizon`s or `future_date`s.
    :rtype: ForecastDataFrame

    Examples:

    # Create a TimeSeriesDataFrame

    >>> data1 = {'a': [1, 1, 0, 0], 'b': [0, 0, 1, 1],
    ...          'c': pd.to_datetime(['2017-01-01', '2017-01-02', '2017-01-03',
    ...                               '2017-01-04']),
    ...          'd': [0, 2, np.nan, 14], 'e': [2, 1, 13, 13]}
    >>> df1 = TimeSeriesDataFrame(data1, grain_colnames=['a', 'b'],
    ...                           time_colname='c', ts_value_colname='d')
    >>> # Create corresponding ForecastDataFrame using default parameters
    >>> fdf1 = construct_forecast_from_train(df1)
    >>> # Create a horizons 1-5 ForecastDataFrame
    >>> fdf2 = construct_forecast_from_train(df1, horizon=5)
    >>> # Create a horizon five only ForecastDataFrame and add a column
    >>> # to store pred.point data
    >>> fdf3 = construct_forecast_from_train(df1, horizon=5, include_all=False,
    ...                                      pred_point='prediction')
    >>> # Create a ForecastDataFrame with a specific future dates
    >>> fdf4 = construct_forecast_from_train(
    ...     df1, future_date=pd.to_datetime('2017-01-05'))

    """
    ###########################################################################
    def get_dates_for_subset_of_horizons(last_date, horizons, freq_str):
        """Thin wrapper around pd.date_range() to get a subset of horizons"""
        new_dates = pd.date_range(last_date, periods=max(horizons) + 1,
                                  freq=freq_str)
        last_date_array = pd.DatetimeIndex([last_date] * (max(horizons) + 1))
        new_horizons = get_period_offsets_from_dates(
            last_date_array, new_dates, freq_str)
        temp_df = pd.DataFrame({'date': new_dates, 'hor': new_horizons})
        result = temp_df[temp_df['hor'].isin(horizons)]

        return pd.DatetimeIndex(result['date'].values)
    ###########################################################################
    # validate inputs
    if not isinstance(X, TimeSeriesDataFrame):
        err = ("Input argument `X` must be of class TimeSeriesDataFrame, "
               + "instead got {}").format(type(X))
        raise NotTimeSeriesDataFrameException(err)
    istype(include_all, bool)
    grains_of_X = set(X.grain_index)
    # sanitize inputs
    if horizon is None and future_date is None:
        horizon = 1
    if horizon is not None:
        horizon_dict = validate_and_sanitize_horizon(horizon, grains_of_X,
                                                     include_all)
    if future_date is not None:
        future_date_dict = validate_and_sanitize_end_dates(future_date, X,
                                                           include_all)
    if horizon is not None and future_date is not None:
        warning_message = ("If both `horizon` and `future_date` are "
                           + "specified, `future_date` will be ignored.")
        warn(warning_message, UserWarning)
    ###########################################################################
    # Get the metadata from the original data frame and update it
    # with new inputs from kwargs
    # Removing constructor args with value=None, since this creates
    #   columns named 'NA' in the output of this function
    constructor_args = {name: getattr(X, name, None)
                        for name in X._metadata
                        if getattr(X, name, None) is not None}

    if 'ts_value_colname' in constructor_args.keys():
        constructor_args['actual'] = constructor_args['ts_value_colname']
    constructor_args.update(kwargs)

    # Get the column names from the original data and add any new
    # names from kwargs
    data_names = set(X.columns)
    data_names = data_names.union(set(X.index.names))
    data_names = data_names.union(set(flatten_list(constructor_args.values())))

    # Construct an empty dictionary to store the data for the constructor
    new_data = {key: [] for key in list(data_names)}

    # Add the new time and grain data to the dictionary
    X_bygrain = X.groupby_grain()
    X_freq = X.infer_freq()
    for grain, series_frame in X_bygrain:
        time_column_index = series_frame.time_index
        if horizon is not None:
            horizons_to_use = sorted(horizon_dict[grain])
            time_values = get_dates_for_subset_of_horizons(
                time_column_index.max(), horizons_to_use, X_freq)
        else:
            time_values = sorted(future_date_dict[grain])
        if (not is_iterable_but_not_string(grain)):
            grain = [grain]
        for i in range(0, len(X.grain_colnames)):
            new_data[X.grain_colnames[i]].extend(
                [grain[i]] * len(time_values))
        new_data[X.time_colname].extend(time_values)
        # handle origins in the input data
        if series_frame.origin_time_colname is not None:
            new_data[series_frame.origin_time_colname] = max(
                series_frame.time_index)

    # Create empty lists of the correct length to store the other data
    for k in set(new_data.keys()).difference(set(X.index.names)):
        new_data[k] = np.nan * len(new_data[X.time_colname])

    # Get the ForecastDataFrame parameters
    forecast_params = {'time_colname', 'grain_colnames', 'origin_time_colname',
                       'actual', 'pred_point', 'pred_dist', 'group_colnames'}
    forecast_params = forecast_params.intersection(
        set(constructor_args.keys()))
    forecast_args = {key: constructor_args[key] for key in forecast_params}

    # Construct the ForecastDataFrame
    new_fdf = ForecastDataFrame(new_data, **forecast_args)
    return new_fdf
################################################################################
