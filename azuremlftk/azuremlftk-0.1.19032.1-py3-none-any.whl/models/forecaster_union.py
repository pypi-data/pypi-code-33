import numpy as np
import pandas as pd
import json
from sklearn.utils.metaestimators import _BaseComposition
from sklearn.externals.joblib import Parallel, delayed
from warnings import warn
from ftk.factor_types import ComputeJobType
from ftk.compute import ComputeStrategyMixin, ComputeBase
from ftk.exception import (EstimatorTypeException, EstimatorValueException, 
                           DatetimeConversionException, DataFrameTypeException,
                           DataFrameValueException, ComputeTypeException,
                           DataFrameProcessingException)
from ftk.base_estimator import AzureMLForecastRegressorBase, loggable
from ftk.multi_forecast_data_frame import MultiForecastDataFrame
from ftk.models import RecursiveForecaster, RegressionForecaster
from ftk.pipeline import AzureMLForecastPipeline
from ftk.constants import (UNIFORM_PRED_POINT_COLNAME, 
                           UNIFORM_PRED_DIST_COLNAME,
                           ORIGIN_TIME_COLNAME_DEFAULT,
                           UNIFORM_MODEL_NAME_COLNAME,
                           UNIFORM_MODEL_PARAMS_COLNAME,
                           UNIFORM_METADATA_DICT)

UNIFORM_ORIGIN_TIME_COLNAME = ORIGIN_TIME_COLNAME_DEFAULT
# UNIFORM_PRED_POINT_COLNAME = 'PointForecast'
# UNIFORM_PRED_DIST_COLNAME = 'DistributionForecast'
# UNIFORM_MODEL_NAME_COLNAME = 'ModelName'
# UNIFORM_MODEL_PARAMS_COLNAME = 'ModelParams'
# UNIFORM_METADATA_DICT = {'pred_point': UNIFORM_PRED_POINT_COLNAME,
#                          'pred_dist': UNIFORM_PRED_DIST_COLNAME,
#                          'origin_time_colname': UNIFORM_ORIGIN_TIME_COLNAME,
#                          'model_colnames': {'model_class': UNIFORM_MODEL_NAME_COLNAME,
#                                             'param_values': UNIFORM_MODEL_PARAMS_COLNAME}}


def is_json_serializable(obj):
    """
    Determine if an object is JSON serializable

    :param obj: Input object
    :type obj: object

    :return: 
        True if the object can be serialized into a JSON string
    :rtype: boolean
    """
    try:
        json.dumps(obj)
        return True
    except TypeError:
        return False


class ForecasterUnion(ComputeStrategyMixin, AzureMLForecastRegressorBase, _BaseComposition):
    """
    This class is inspired by class sklearn.pipeline.FeatureUnion_

    .. _sklearn.pipeline.FeatureUnion: http://scikit-learn.org/stable/modules/generated/sklearn.pipeline.FeatureUnion.html

    This class enables fit/predict on a collection of forecasting models.
    A common use case is to compare the performance of several
    models on the same data set.

    Fitting parameters of an individual forecaster may be set using its name 
    and the parameter name separated by a '__'. 

    To enable parallel model fitting of ForecasterUnion estimators, enable any supported
    compute backend

    :param forecaster_list: 
        List of models to be applied to the data.
        Each list element is a tuple with two entries.
        The first half of each tuple is a name to associate with
        the resulting forecast and the second half is an object meeting
        the following qualfications:
        1. Instances of RecursiveForecaster subclasses
        2. Instance of RegressionForecaster 
        3. Instance of AzureMLForecastPipeline with last step satisfying
           either (1) or (2) above.
    :type forecaster_list: list of (string, predictor) tuples  

    :param n_jobs:
        Number of jobs to run in parallel (default 1).
    :type n_jobs: int

    """
    def __init__(self, forecaster_list, n_jobs=1):
        self.forecaster_list = forecaster_list
        self.n_jobs = n_jobs
        self._is_fit = False

    @property
    def forecaster_list(self):
        """
        List of name, forecast pairs.
        See `forecaster_list` parameter.
        """
        return self._forecaster_list

    @forecaster_list.setter
    def forecaster_list(self, val):
        # check whether the val is list of tuples
        if not (isinstance(val, list) and
                all([isinstance(v, tuple) for v in val])):
            raise EstimatorTypeException('The input for forecaster_list is '
                                         'not a list of tuples.')

        self._forecaster_list = val
        # validate the forecasters
        self._validate_forecasters()

    def _get_check_pickle_flag(self):
        # this is a temporary check added to tackle the statsmodel.ARIMA pickle
        # issue described here: https://github.com/statsmodels/statsmodels/issues/3733
        # should be fine once the statsmodel 0.9 is coming out, in which
        # version the corresponding fix has been gone to.
        # The pickle problems is happening whenever the joblib delayed
        # function is used, since it, by default with check_pickle=True,
        # will try to pickle the input function.
        # if the check_pickle returned is False, which is using statsmodel
        # version less than 0.9.X and one of the forecaster is Arima,
        # this function will return False. And as a result, the check_pickle
        # option in the following in the joblib.delayed() function will be set
        # to False to skip the pickle.dumps() step.
        check_pickle = True
        from statsmodels import __version__ as statsmodels_version
        if int(statsmodels_version[2]) <= 8:
            from ftk.models.arima import Arima
            for _, forecaster in self.forecaster_list:
                if isinstance(forecaster, Arima):
                    check_pickle = False
                    break
        return check_pickle

    def get_params(self, deep=True):
        """
        Get parameters for this estimator.

        :param deep:
            If True, will return the parameters for this estimator and
            contained subobjects that are estimators.
        :type deep: boolean

        :return: Dictionary of parameter name => values
        :rtype: dict     
        """

        return self._get_params('forecaster_list', deep=deep)

    def set_params(self, **kwargs):
        """
        Set the parameters of this estimator.
        Valid parameter keys can be listed with `get_params()`.

        Fitting parameters of an individual forecaster may be set using its name 
        and the parameter name separated by a '__'. 

        :param **kwargs: 
            Keyword arguments of the form:
            ```<Forecaster name>__<Parameter name>=<Parameter value>```
        :type **kwargs: dict

        :return: self
        :rtype: ForecasterUnion

        """
        self._set_params('forecaster_list', **kwargs)
        return self

    def _validate_forecasters(self):
        names, forecasters = zip(*self.forecaster_list)

        # validate names
        self._validate_names(names)

        # validate forecasters
        for t in forecasters:
            if not (isinstance(t, RecursiveForecaster) or
                    isinstance(t, RegressionForecaster) or
                    isinstance(t, AzureMLForecastPipeline)):
                bad_estimator = True
                if hasattr(t, 'estimator'):
                    estimator_type = type(t.estimator)
                    if (isinstance(t.estimator, RecursiveForecaster) or
                        isinstance(t.estimator, RegressionForecaster) or
                        isinstance(t.estimator, AzureMLForecastPipeline)):
                        bad_estimator = False
                else:
                    estimator_type = type(t)
                if bad_estimator:
                    raise EstimatorTypeException(
                        'Currently, the forecaster needs to be an instance '
                        'of either RecursiveForecaster/RegressionForecaster/AzureMLForecastPipeline'
                        'or their subclass.  Instead found instance of type {}'.format(type(estimator_type)))
            
            if isinstance(t, AzureMLForecastPipeline):
                # if the forecaster is a pipeline
                # it must be a pipeline with last step of
                # RecursiveForecaster/RegressionForecaster
                last_step = t._steps[len(t._steps)-1][1]
                if not (isinstance(last_step, RecursiveForecaster) or
                        isinstance(last_step, RegressionForecaster)):
                    raise EstimatorTypeException(
                        'Currently, if the forecaster is an '
                        'AzureMLForecastPipeline, its last step needs to be '
                        'an instance of either '
                        'RecursiveForecaster/RegressionForecaster or their '
                        'subclass.')

    def _get_forecaster_params(self, forecaster):
        """
        Get the dictionary of parameters for a particular forecaster.

        If the value of a specific parameter is not serializable,
        the parameter will be dropped.
        """
        json_serializable_param_dict = {key: value for key, value in
                                        forecaster.get_params().items() if
                                        is_json_serializable(value)}
        return json_serializable_param_dict

    @staticmethod
    def _fit_one_forecaster_compute(task, **func_kwargs):
        '''
        A function that is used to fit a model. This function can be passed
        as a callable to any of the compute backends that support `ComputeJobType.ForecasterUnion`
        job types.

        param task: Tuple of forecaster_name and its corresponding estimator.                    
        type task: tuple.
        param func_args: Keyword fit parameters passed on to the forecaster fit methods.
                        These arguments should have the form,
                        ```<Forecaster name>[<Parameter name>]=<Parameter value>```
        type func_args: dict.

        :return: Tuple containing the estimator name and its fitted Model
        :rtype: tuple
        '''
        if task is None:
            raise Exception('task argument is invalid or not a tuple')

        if func_kwargs is None:
            raise Exception('func_args argument is invalid')
        
        # Fetch required args for model fit.
        _X = func_kwargs.pop('X')        
        _y = func_kwargs.pop('y')        
        _fit_param_dict = func_kwargs.pop('forecaster_fit_params') 
        _forecaster_name = task[0]        
        _forecaster = task[1]

        # Return (name, fitted model) tuple
        return (_forecaster_name, _forecaster.fit(_X, _y, **_fit_param_dict[_forecaster_name]))

    def _fit_one_forecaster(self, forecaster, X, y=None, **fit_params):
        return forecaster.fit(X, y, **fit_params)

    @loggable
    def fit(self, X, y=None, **fit_params):
        """
        Fit all the forecasters

        :param X: Input data used to fit forecasters
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`

        :param y: 
            Target quantity for supervised learning.
            Ignored by many forecasters since X already contains
            the target quantity.

        :param **fit_params:
            Keyword fit parameters passed on to the forecaster fit methods.
            These arguments should have the form,
            ```<Forecaster name>__<Parameter name>=<Parameter value>```
        :type **fit_params: dict

        """

        fit_param_dict = dict([(forecaster_name, {})
                               for forecaster_name, _ in self.forecaster_list])
        for pname, pval in fit_params.items():
            forecaster_name, forecaster_fit_param = pname.split('__', 1)
            fit_param_dict[forecaster_name][forecaster_fit_param] = pval

        # If compute strategy is enabled, then trigger task job for fitting
        # ForecasterUnion models.
        if not self._compute_strategy is None:

            # The set of keyword arguments to be passsed to the function.
            func_kwargs = {
                'X': X,
                'y': y,                
                'forecaster_fit_params': fit_param_dict
            }

            # Execute the task job passing the callback function ```ForecasterUnion._fit_one_forecaster_compute```
            # that fits single model.
            job_executor = self.execute_task_job(func=ForecasterUnion._fit_one_forecaster_compute,
                                                job_type=ComputeJobType.ForecasterUnion,
                                                tasks=self.forecaster_list,                                                
                                                **func_kwargs)

            # Gather results and raise exception if errors were found                                                
            if job_executor is None or (job_executor.errors is not None and len(job_executor.errors) > 0):
                raise Exception(job_executor.errors)            
            else:
                # ForecasterUnion fit function returns a tuple (name, fitted model).
                # This is same as expected by self.forecatser_list. We simply set the results to the var.
                self.forecaster_list = job_executor.job_results

        # Iterate over grain levels - train a model for each series
        else:
            
            # fit the forecaster in parallel according to the n_jobs specified
            check_pickle = self._get_check_pickle_flag()
            if not check_pickle:
                forecasters = Parallel(n_jobs=self.n_jobs)(
                    delayed(self._fit_one_forecaster, check_pickle=False)
                    (forecaster, X, y, **fit_param_dict[forecaster_name])
                    for forecaster_name, forecaster in self.forecaster_list)
            else:
                forecasters = Parallel(n_jobs=self.n_jobs)(
                    delayed(self._fit_one_forecaster)
                    (forecaster, X, y, **fit_param_dict[forecaster_name])
                    for forecaster_name, forecaster in self.forecaster_list)

            # update the forecasters with the fitted forecasters
            self.forecaster_list = [(forecaster_name, forecasters[i])
                                    for i, (forecaster_name, forecaster) in
                                    enumerate(self.forecaster_list)]

        

        # update the _is_fit internal attribute
        self._is_fit = True

        return self

    def _predict_one_forecaster(self, forecaster_list_item, X,
                                include_forecaster_params=False,
                                retain_feature_column=False):
        forecaster_name, forecaster = forecaster_list_item
        X_predict = forecaster.predict(X)

        # we will uniform the value of following metadata and the
        # name of the corresponding column/index for ease of results
        # concatenation from different forecasters:
        # (1). pred_point
        # (2). pred_dist
        # (3). origin_time_colname
        # (4). model_colnames

        # (1). pred_point
        # (2). pred_dist
        # (3). origin_time_colname
        for attr_name in ['pred_point', 'pred_dist', 'origin_time_colname']:
            attr_value = getattr(X_predict, attr_name)
            expected_attr_value = UNIFORM_METADATA_DICT[attr_name]

            if attr_value is not None:
                if attr_value in X_predict.columns:
                    # the attr_value is in the column
                    if attr_value != expected_attr_value:
                        # rename the column to be expected name
                        X_predict.rename(
                            columns={attr_value: expected_attr_value},
                            inplace=True)
                else:
                    # the attr_value is in the index, rename the index
                    X_predict.index.names = [i if i != attr_value else
                                             expected_attr_value for i in
                                             X_predict.index.names]
            else:
                if attr_name not in type(X_predict)._slice_key_metadata:
                    # if the metadata supposed to be in the column:
                    # if the metadata is missing in the output
                    # ForecastDataFrame, make a column named the expected name,
                    # and fill the column with NA values.
                    warn('The column {0} already exist in the data frame and it '
                         'is not set as the {1} property in the '
                         'ForecastDataFrame. It will be overwritten with NA '
                         'values for joining the forecast results with those '
                         'from other models.'.format(expected_attr_value,
                                                     attr_name))
                    X_predict[expected_attr_value] = np.nan
                else:
                    # the metadata is supposed to be in the index
                    # currently, the only metadata falling here is the
                    # origin_time_colname.
                    # Nothing will be done here because we cannot just fill NA in
                    #  the index, it might leading to the exception thrown at
                    # duplicate-index-checker.
                    continue

            # reset the meta data field
            setattr(X_predict, attr_name, expected_attr_value)

        # (4). model_colnames
        # add the field indicating the forecaster name
        if UNIFORM_MODEL_NAME_COLNAME in X_predict.columns:
            warn('The column {0} already exists in the data frame and '
                 'it will be overwritten by the name of the forecaster {1}'.
                 format(UNIFORM_MODEL_NAME_COLNAME, forecaster_name))

        X_predict[UNIFORM_MODEL_NAME_COLNAME] = forecaster_name

        if include_forecaster_params:
            if UNIFORM_MODEL_PARAMS_COLNAME in X_predict.columns:
                warn('The column {0} already exists in the data frame and '
                     'it will be overwritten by the parameter information of '
                     'the forecaster {1}'.
                     format(UNIFORM_MODEL_PARAMS_COLNAME, forecaster_name))

            X_predict[UNIFORM_MODEL_PARAMS_COLNAME] = \
                np.repeat(self._get_forecaster_params(forecaster),
                          X_predict.shape[0])

        # Turn X_predict from ForecastDataFrame into MultiForecastDataFrame
        if include_forecaster_params:
            model_colnames = UNIFORM_METADATA_DICT['model_colnames']
        else:
            model_colnames = {key: value for (key, value) in
                              UNIFORM_METADATA_DICT['model_colnames'].items()
                              if value != UNIFORM_MODEL_PARAMS_COLNAME}

        X_predict = MultiForecastDataFrame(X_predict,
                                           model_colnames=model_colnames)

        if retain_feature_column:
            return X_predict
        else:
            # These are the prediction related columns
            return_cols = [X_predict.pred_point, X_predict.pred_dist]

            # add actual column if it exists
            if X_predict.actual is not None:
                return_cols = return_cols + [X_predict.actual]

            return X_predict[return_cols]

    def _predict_long_format(self, X, include_forecaster_params=False,
                             retain_feature_column=False):
        check_pickle = self._get_check_pickle_flag()
        if not check_pickle:
            predict_results = Parallel(n_jobs=self.n_jobs)(
                delayed(self._predict_one_forecaster, check_pickle=False)(
                    forecaster_list_item, X,
                    include_forecaster_params=include_forecaster_params,
                    retain_feature_column=retain_feature_column)
                for forecaster_list_item in self.forecaster_list)
        else:
            predict_results = Parallel(n_jobs=self.n_jobs)(
                delayed(self._predict_one_forecaster)(
                    forecaster_list_item, X,
                    include_forecaster_params=include_forecaster_params,
                    retain_feature_column=retain_feature_column)
                for forecaster_list_item in self.forecaster_list)

        if len(predict_results) == 0:
            return None

        # concatenate the predictions row-wise
        # This concatenation makes sense when: all the predictions share the
        # same index names and same index sequence.
        index_names_list = [predict_result.index.names for predict_result in
                            predict_results]

        # set the index names from first forecaster as the benchmark index names
        # all index names from following forecasters need to align with this.
        first_forecaster_index_names = index_names_list[0]

        for i, index_names in enumerate(index_names_list):
            if i > 0:
                if not (len(index_names) == len(first_forecaster_index_names)
                        and set(index_names) == set(first_forecaster_index_names)):
                    raise EstimatorValueException(
                        'The prediction result from forecaster {0} has '
                        'different unique index names with that from '
                        'forecaster {1}. The results cannot be '
                        'concatenated.'.format(
                            predict_results[0].index.get_level_values(
                                UNIFORM_MODEL_NAME_COLNAME).unique()[0],
                            predict_results[i].index.get_level_values(
                                UNIFORM_MODEL_NAME_COLNAME).unique()[0]
                        ))

                if index_names != first_forecaster_index_names:
                    # this means they share the same index unique names
                    # but the sequence of the index is different.
                    # then reorder the index to make sure the sequence is as
                    # same as the first one.
                    predict_results[i] = predict_results[i].reorder_levels(
                        first_forecaster_index_names)

        X_predicts = pd.concat(predict_results).sort_index()

        return X_predicts

    @loggable
    def predict(self, X, include_forecaster_params=False,
                retain_feature_column=False, wide_format=False):
        """
        Predict the target quantity with each forecaster
        and concatenate the results.

        :param X: Data to use for predict
        :type X:
            :class:`ftk.forecast_data_frame.ForecastDataFrame`,
            :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`

        :param include_forecaster_params:
            Whether to include a column which contains the
            dictionary of parameters name and value pair in the forecaster.
        :type include_forecaster_params: boolean

        :param retain_feature_column:
            Whether retain the feature columns in the output forecast data
            frame.
        :type retain_feature_column: boolean

        :param wide_format:
            Whether show the results in wide format.
        :type wide_format: boolean

        :return: Data with predictions from all forecasters
        :rtype: :class:`ftk.multi_forecast_data_frame.MultiForecastDataFrame`

        """

        # check whether the ForecasterUnion has been fitted.
        if not self._is_fit:
            raise EstimatorValueException('The ForecasterUnion has not been '
                                          'fitted yet. Please call fit() '
                                          'method '
                                          'to fit the ForecasterUnion before '
                                          'calling the predict() method.')

        if not wide_format:
            return self._predict_long_format(
                X, include_forecaster_params=include_forecaster_params,
                retain_feature_column=retain_feature_column)

        # predict without retaining feature column
        # it does not make sense to unstack the feature columns in the pivot
        # the feature values should always be the same across different
        # forecasters.
        X_predicts = self._predict_long_format(
            X, include_forecaster_params=include_forecaster_params,
            retain_feature_column=False)

        model_related_index_names = [value for key, value in
                                     X_predicts.model_colnames.items()]

        # actual columns needs to be reserved if actual metadata exists
        actual_reserve_flag = X_predicts.actual is not None

        if actual_reserve_flag:
            # drop the actual column at first so it will not be duplicated
            # across different models when operating the unstack()
            X_predicts = X_predicts.drop([X_predicts.actual], axis=1)

        # unstack returns a pandas.DataFrame, because in _unstack_frame
        # method of pandas.core.reshape.reshape.py DataFrame is explicly
        # called to reconstruct the object.
        # Metadata needs to be added back after the unstack().

        # get the metadata of X_predicts
        X_predicts_metadata_dict = X_predicts._get_metadata_dict()

        # remove the 'model_colnames', since they will be unstacked in the
        # wide format
        X_predicts_metadata_dict.pop('model_colnames', None)

        # remove the 'pred_point' and 'pred_dist'
        # currently, we don't have a ForecastDataFrame could hold multiple
        # forecasts in wide format
        X_predicts_metadata_dict.pop('pred_dist', None)
        X_predicts_metadata_dict.pop('pred_point', None)

        # get the type of X_predicts
        X_predicts_type = type(X_predicts)

        # unstack on the model related index names, this step returns a
        # pandas.DataFrame
        X_predicts = X_predicts.unstack(level=model_related_index_names)

        # bring the columns to one flat level
        # the column names are following the convention:
        # If there is no ModelParam:
        #   'ModelName_DistributionForecast' or 'ModelName_PointForecast'
        # If there is ModelParam:
        #   'ModelName_ModelParam_DistributionForecast' or 'ModelName_ModelParam_PointForecast'
        if include_forecaster_params:
            col_name_sequence = [
                X_predicts.columns.names.index(UNIFORM_MODEL_NAME_COLNAME),
                X_predicts.columns.names.index(UNIFORM_MODEL_PARAMS_COLNAME),
                X_predicts.columns.names.index(None)
            ]
        else:
            col_name_sequence = [
                X_predicts.columns.names.index(UNIFORM_MODEL_NAME_COLNAME),
                X_predicts.columns.names.index(None)
            ]

        prediction_related_columns = ['_'.join(
            [name[s] for s in col_name_sequence])
            for name in X_predicts.columns]

        X_predicts.columns = prediction_related_columns

        # reconstruct result by calling the constructor with the metadata
        X_predicts = X_predicts_type(X_predicts, **X_predicts_metadata_dict)

        # merge the X_predicts with the original X
        X_predicts = X_predicts.merge(X, how='left')

        if actual_reserve_flag:
            # set the X_predicts.actual and X_predicts.ts_value_colname
            # equal to X.ts_value_colname
            X_predicts.ts_value_colname = X.ts_value_colname
            X_predicts.actual = X.ts_value_colname

        if retain_feature_column:
            return X_predicts
        else:
            # These are the prediction related columns
            return_cols = prediction_related_columns

            # add actual column if it exists
            if X_predicts.actual is not None:
                return_cols = return_cols + [X_predicts.actual]

            return X_predicts[return_cols]

    @loggable
    def fit_predict(self, X, **fit_params):
        # This not implemented because: UnionForecast have key arguments for
        # both fit() and predict() method.
        # Future work could be done to extract the predict parameters and
        # leave all other params as they are all fit parameters, since the
        # predict method's key arguments are pretty manageable in this class.
        raise NotImplementedError('The method fit_predict() has not been'
                                  'implemented for UnionForecaster.')


