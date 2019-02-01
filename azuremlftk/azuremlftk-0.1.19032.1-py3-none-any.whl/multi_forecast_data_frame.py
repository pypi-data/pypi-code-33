"""
A module that defines MultiForecastDataFrame class which in turn serves as a data structure to handle forecasts from multiple models.
"""

from ftk import TimeSeriesDataFrame, ForecastDataFrame
import pandas as pd
import numpy as np
import json

from sklearn.metrics import r2_score

from ftk import verify
from ftk.exception import (DataFrameValueException,
                           DataFrameTypeException,
                           NotSupportedException,
                           DataFrameMissingColumnException,
                           NotTimeSeriesDataFrameException)
from ftk.verify import Messages
from ftk.model_selection import RollingOriginValidator
from ftk.constants import (UNIFORM_PRED_POINT_COLNAME, 
                           UNIFORM_PRED_DIST_COLNAME)

from warnings import warn, simplefilter, catch_warnings


class MultiForecastDataFrame(ForecastDataFrame):
    """
    .. py:class:: MultiForecastDataFrame
    A subclass of ForecastDataFrame with the ability to handle forecasts 
    from multiple models.

    .. _scipy.stats: https://docs.scipy.org/doc/scipy/reference/tutorial/
        stats.html

    :param:
        data, index, columns, dtype, copy, grain_colnames, time_colname,
        ts_value_colname, group_colnames, fcast_origin_date_colname,
        grain_colname: see :class: 'timeseries_dataframe.TimeSeriesDataFrame'

    :param:
        actual, pred_point, pred_forecast, fcast_origin_date_colname: see 
        :class: 'dataframeforecast.ForecastDataFrame'

    :param model_colnames: dict
        Names of the field identifying which model each forecast came from.
        Functions in this package will create a dict with two fields `model_class`
        and `param_values`.

    :examples:
    # construct from dictionary

    >>> data1 = {'date': pd.to_datetime(['2017-01-01', '2017-01-02',
    ...                                  '2017-01-03', '2017-01-04']*4),
    ...          'grain': ['a']*8 + ['b']*8,
    ...          'origin_time': pd.to_datetime(['2016-12-31']*16),
    ...          'pred_point': [0.779, 2.039, 3.747, 4.106, -0.378,
    ...                         2.826, 1.504, 4.851, 5.775, 6.399,
    ...                         6.014, 7.998, 4.308, 5.801, 7.920,
    ...                         8.015],
    ...          'actual': [1., 2., 3., 4.]*2 + [5., 6., 7., 8.]*2,
    ...          'class': ['gaussian']*16,
    ...          'param': [0.5]*4 + [1.]*4 + [0.5]*4 + [1.]*4
    ...          }
    >>> df1 = MultiForecastDataFrame(data1, grain_colnames='grain',
    ...                              time_colname='date', actual='actual',
    ...                              pred_point='pred_point',
    ...                              origin_time_colname='origin_time',
    ...                              model_colnames={'model_class': 'class',
    ...                                              'param_values': 'param'})
    >>> df1
                                                 actual  pred_point
    date       grain origin_time class    param                    
    2017-01-01 a     2016-12-31  gaussian 0.50     1.00        0.78
    2017-01-02 a     2016-12-31  gaussian 0.50     2.00        2.04
    2017-01-03 a     2016-12-31  gaussian 0.50     3.00        3.75
    2017-01-04 a     2016-12-31  gaussian 0.50     4.00        4.11
    2017-01-01 a     2016-12-31  gaussian 1.00     1.00       -0.38
    2017-01-02 a     2016-12-31  gaussian 1.00     2.00        2.83
    2017-01-03 a     2016-12-31  gaussian 1.00     3.00        1.50
    2017-01-04 a     2016-12-31  gaussian 1.00     4.00        4.85
    2017-01-01 b     2016-12-31  gaussian 0.50     5.00        5.78
    2017-01-02 b     2016-12-31  gaussian 0.50     6.00        6.40
    2017-01-03 b     2016-12-31  gaussian 0.50     7.00        6.01
    2017-01-04 b     2016-12-31  gaussian 0.50     8.00        8.00
    2017-01-01 b     2016-12-31  gaussian 1.00     5.00        4.31
    2017-01-02 b     2016-12-31  gaussian 1.00     6.00        5.80
    2017-01-03 b     2016-12-31  gaussian 1.00     7.00        7.92
    2017-01-04 b     2016-12-31  gaussian 1.00     8.00        8.02

    # construct from pandas.DataFrame_

    >>> pd_df1 = pd.DataFrame(data1)
    >>> df2 = MultiForecastDataFrame(pd_df1, grain_colnames='grain',
    ...                              time_colname='date', actual='actual',
    ...                              pred_point='pred_point',
    ...                              origin_time_colname='origin_time',
    ...                              model_colnames={'model_class': 'class',
    ...                                              'param_values': 'param'})
    >>> df2
                                                 actual  pred_point
    date       grain origin_time class    param                    
    2017-01-01 a     2016-12-31  gaussian 0.50     1.00        0.78
    2017-01-02 a     2016-12-31  gaussian 0.50     2.00        2.04
    2017-01-03 a     2016-12-31  gaussian 0.50     3.00        3.75
    2017-01-04 a     2016-12-31  gaussian 0.50     4.00        4.11
    2017-01-01 a     2016-12-31  gaussian 1.00     1.00       -0.38
    2017-01-02 a     2016-12-31  gaussian 1.00     2.00        2.83
    2017-01-03 a     2016-12-31  gaussian 1.00     3.00        1.50
    2017-01-04 a     2016-12-31  gaussian 1.00     4.00        4.85
    2017-01-01 b     2016-12-31  gaussian 0.50     5.00        5.78
    2017-01-02 b     2016-12-31  gaussian 0.50     6.00        6.40
    2017-01-03 b     2016-12-31  gaussian 0.50     7.00        6.01
    2017-01-04 b     2016-12-31  gaussian 0.50     8.00        8.00
    2017-01-01 b     2016-12-31  gaussian 1.00     5.00        4.31
    2017-01-02 b     2016-12-31  gaussian 1.00     6.00        5.80
    2017-01-03 b     2016-12-31  gaussian 1.00     7.00        7.92
    2017-01-04 b     2016-12-31  gaussian 1.00     8.00        8.02

    """

    @property
    def _constructor(self):
        return MultiForecastDataFrame

    _metadata = ForecastDataFrame._metadata + ['model_colnames']
    # this is the metadata fields that is used to generate the property 
    # slice_key_colnames
    _slice_key_metadata = TimeSeriesDataFrame._slice_key_metadata + \
        ['model_colnames']

    def __init__(self, data=None, index=None, columns=None, dtype=None,
                 copy=False, grain_colnames=None, time_colname=None, 
                 group_colnames=None, actual=None, pred_point=None, 
                 pred_dist=None, origin_time_colname=None, model_colnames=None):

        if isinstance(data, TimeSeriesDataFrame):
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
        if isinstance(data, ForecastDataFrame):
            if data.pred_point is not None:
                pred_point = data.pred_point
            if data.pred_dist is not None:
                pred_dist = data.pred_dist
            if data.actual is not None:
                actual = data.actual

        super(MultiForecastDataFrame, self).__init__(
            data=data, index=index, columns=columns, dtype=dtype, 
            copy=copy, time_colname=None)

        self.time_colname = time_colname
        self.actual = actual
        self.group_colnames = group_colnames
        self.origin_time_colname = origin_time_colname
        self.grain_colnames = grain_colnames
        self.pred_point = pred_point
        self.pred_dist = pred_dist

        self.model_colnames = model_colnames
        self._model_class_ = 'MULTI'
        self._param_values_ = 'MULTI'

        if self.time_colname is not None:
            self._reset_tsindex()
            self._check_column_equal_across_origin()

    @property
    def model_colnames(self):
        return self.__model_colnames

    @model_colnames.setter
    def model_colnames(self, val):
        if val is None:
             with catch_warnings():
                simplefilter('ignore')
                self.__model_colnames = val
        else:
            my_cols = None
            # prefered input, check for proper formatting of dictionary
            if isinstance(val, dict):
                for key, col in val.items():
                    if key not in {'model_class', 'param_values'}:
                        raise NotSupportedException(
                            'model_colnames keys must be {`model_class`, `param_values`},' +
                            'instead found {0}'.format(set(val.keys())))
                    if not isinstance(col, str):
                        raise NotSupportedException(
                            'model_colnames values must all be str.')
                    if col not in self.columns and col not in self.index.names:
                        raise DataFrameMissingColumnException(
                            'model column %s is not found in dataframe.' % col)
                my_cols = val
            # Allowed input for user convienence.  Encode as dict
            elif isinstance(val, str):
                if val not in self.columns and val not in self.index.names:
                    raise DataFrameMissingColumnException(
                        'model column %s is not found in dataframe.' % val)
                my_cols = {'model_class': val}
            else:
                raise NotSupportedException(
                    'model columns must be specified by a dict or str value')

            with catch_warnings():
                simplefilter('ignore')
                self.__model_colnames = my_cols

            # `param_values` columns are often encoded as dicts, which are not
            # a hashable data type.  We need to convert it to a string 
            # representation.
            if 'param_values' in self.model_colnames.keys():
                moved_index = False
                if self.model_colnames['param_values'] in self.index.names:
                    self.reset_index(
                        level=self.model_colnames['param_values'], drop=False, 
                        inplace=True)
                    moved_index = True
                # encode the param values as strings
                self[self.model_colnames['param_values']] = [
                    json.dumps(v, sort_keys=True, cls=NumpyEncoder) if isinstance(
                    v, dict) else v for v in self[self.model_colnames['param_values']]]
                if moved_index:
                    self = self._reset_tsindex()

        

    def backtest(self, metric_fun=lambda y_true, y_pred: -r2_score(y_true, y_pred)):
        """
        backtest returns a MultiForecastDataFrame containing the forecast values 
        from predicted with the minimum historical error.

        :param metric_fun:
           A function used to evaluate the model error.  Should inputs `y_true`,
           the actual value and `y_pred` the predicted value.  Default value is 
           negative R^2 for compatability with the default with sklearn 
           regression estimators.
        :type metric_fun: function
        """

        if self.model_colnames is None:
            raise DataFrameMissingColumnException(
                "model_colnames must be set to perform backtesting")
        if self.pred_point is None:
            raise DataFrameMissingColumnException(
                "pred_point must be set to perform backtesting")
        if self.actual is None:
            raise DataFrameMissingColumnException(
                "actual must be set to perform backtesting")
        model_colname = list(self.model_colnames.values())
        pred_colname = self.pred_point
        actual_colname = self.actual

        # Compute the number of folds for CV
        if self.origin_time_colname is not None:
            min_time_index = min(self.time_index)
            origin_greater = self.origin_time_index[
                self.origin_time_index > min_time_index]
            num_cv_folds = len(origin_greater.unique())
        else:
            num_cv_folds = len(self.time_index.unique()) - 1

        rollcv = RollingOriginValidator(n_splits=num_cv_folds, n_step=None)
        splits = rollcv.split(self)

        ctor_params = {k: getattr(self, k, None) for k in self._metadata}
        return_df = pd.DataFrame()
        for train_cv, test_cv in splits:
            self_group = self.iloc[train_cv, :].groupby(level=model_colname)
            model_error = self_group.apply(
                lambda g: metric_fun(g[actual_colname], g[pred_colname]))
            test_values = self.iloc[test_cv, :]
            test_values = test_values.xs(
                model_error.idxmin(), drop_level=False, 
                level=model_colname if len(model_colname) > 1 else model_colname[0])
            return_df = pd.concat([return_df, test_values])
        # Construct a return object of the same type as the calling object
        return_df = type(self)(return_df, **ctor_params)

        return return_df

    @property
    def model_index(self):
        """
        Helper method to retrieve the `model_colnames` index columns
        """
        cols_to_return = [self.model_colnames['model_class']]
        if 'param_values' in self.model_colnames:
            cols_to_return.append(self.model_colnames['param_values'])
        return self._get_index_by_names(cols_to_return)


    def subset_by_model(self, model_names, model_params=None, 
                        simplify=False, rename_preds=True):
        """
        Return a subset of `MultiForecastDataFrame` with results from some of 
        the models.

        :param model_names: 
            Name(s) of models that should be returned. 
        :type model_names: str or iterable of strings.

        :param model_params: 
            Parameter values that should be returned. For many models, 
            parameter values are stored as dicts, such as
            `{'estimator__alpha': 0.0}` - in this case, provide a dict, and
            it will get encoded into a string automatically. If you seek 
            several models, you may have to pass a list of dicts.
        :type model_params: str, dict, or iterable of the above two

        :param simplify:
            If `True`, the returned output is simplified from a 
            `MultiForecastDataFrame` to a `ForecastDataFrame`. This will only
            work when results for a single model are requested, i.e. 
            `model_names` and `model_params` must both be a single string
        :type simplify: bool

        :param rename_preds:
            If `True`, the model name is appended to the `pred_point` and 
            `pred_dist` column names, and the column with the model name is 
            removed from the output. This argument is ignored if `simplify` is
            `False`. 
        :type rename_preds: bool

        :return: 
            `MultiForecastDataFrame` or `ForecastDataFrame`, depending on the
            inputs.            
        :rtype: `MultiForecastDataFrame`, `ForecastDataFrame` 
        """

        # checking simplify 
        verify.istype(simplify, bool)
        if simplify:
            if not (isinstance(model_names, str) and
                    (isinstance(model_params, str) or (model_params is None) \
                     or isinstance(model_params, dict))):
                error_msg = ("When `simplify` is `True`, both `model_names` "
                            + "and `model_params` must be singletons.")
                raise ValueError(error_msg)
        # check rename_preds
        verify.istype(rename_preds, bool)
        # check model_names
        if isinstance(model_names, str):
            model_names = [model_names]
        elif verify.is_collection(model_names):
            if simplify:
                error_msg = ("When `simplify` is `True`, input `model_names` "
                             "should be a singleton!")
                raise ValueError(error_msg)
            if not all(isinstance(x, str) for x in model_names):
                error_msg = ("When `model_names` is iterable, each element " 
                             + "must be a string!")
                raise ValueError(error_msg)
        else:
            error_msg = ('Input `model_names` can be either a string or a '
                         + 'collection of strings. Instead got: {}').format(
                             type(model_names))
            raise ValueError(error_msg)
        # now check model_params
        if model_params is not None:
            if isinstance(model_params, dict):
                model_params_clean = [json.dumps(model_params, sort_keys=True, 
                                                 cls=NumpyEncoder)]
            elif isinstance(model_params, str):
                model_params_clean = [model_params]
            elif verify.is_collection(model_params):
                if simplify:
                    error_msg = ("When `simplify` is `True`, input "
                                 "`model_params` should be a singleton!")
                    raise ValueError(error_msg)
                model_params_clean = []
                for x in model_params:
                    if isinstance(x, dict):
                        model_params_clean.append(
                            json.dumps(x, sort_keys=True, cls=NumpyEncoder))
                    elif isinstance(x, str):
                        model_params_clean.append(x)
                    else:
                        error_msg = ("When `model_params` is iterable, each " 
                                     + "element must be a string or a dict! "
                                     + "Instead got {}").format(type(x))
                        raise ValueError(error_msg)
            else:
                error_msg = ('Input `model_params` can be either `None` a '
                            + 'string, a dict, or a collection of the above. '
                            + 'Instead got: {}').format(type(model_params))
                raise ValueError(error_msg)

        subset_to_pick = model_names
        if model_params is not None:
            subset_to_pick = [(name, param) for name in subset_to_pick
                                            for param in model_params_clean]
        # edge case - returning all params for more than 1 model
        if (model_params is None) and ('param_values' in self.model_colnames):
            all_params = set(self.index.get_level_values(
                self.model_colnames['param_values']))
            subset_to_pick = [(name, param) for name in subset_to_pick
                                            for param in all_params]
        idx_to_return = [i in subset_to_pick for i in self.model_index]
        subset = self.loc[idx_to_return]
        
        if simplify:
            temp_df = super(TimeSeriesDataFrame, subset).reset_index()
            metadata = subset._get_metadata() 
            del metadata['model_colnames']
            if rename_preds:
                new_colnames = (UNIFORM_PRED_POINT_COLNAME + model_names[0], 
                                UNIFORM_PRED_DIST_COLNAME + model_names[0])
                metadata['pred_point'] = new_colnames[0]
                metadata['pred_dist'] = new_colnames[1]
                temp_df = temp_df.rename(columns={
                    UNIFORM_PRED_POINT_COLNAME: new_colnames[0], 
                    UNIFORM_PRED_DIST_COLNAME: new_colnames[1]})
                del temp_df[subset.model_colnames['model_class']]
            subset = ForecastDataFrame(temp_df, **metadata)
        return subset


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.generic):
            return np.asscalar(obj)
        else:
            return super(NumpyEncoder, self).default(obj)
