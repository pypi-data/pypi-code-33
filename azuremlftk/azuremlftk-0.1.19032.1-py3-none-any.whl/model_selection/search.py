"""
The :mod:`ftk.model_selection.search` module includes utilities to fine-tune the
parameters of an estimator and return the out of sample predictions for use in
back testing models.
"""

import os
import pickle
import warnings
import numbers
import time
from collections import Mapping, defaultdict, Sequence
from functools import partial
from itertools import product
from sklearn.externals.joblib import logger
import numpy as np
import pandas as pd
from scipy.stats import rankdata

from sklearn.base import is_classifier, clone, BaseEstimator, RegressorMixin
from sklearn.model_selection._split import check_cv
from sklearn.model_selection._validation import (_aggregate_score_dicts,
                                                 _index_param_value)
from sklearn.externals.joblib import Parallel, delayed
from sklearn.externals import six
from sklearn.utils.fixes import MaskedArray
from sklearn.utils.validation import indexable, _num_samples
from sklearn.utils.deprecation import DeprecationDict
from sklearn.metrics.scorer import _check_multimetric_scoring
from sklearn.model_selection import ParameterGrid

from sklearn.model_selection._validation import _score
from sklearn.utils.metaestimators import _safe_split
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.utils import indexable
from sklearn.exceptions import FitFailedWarning
from traceback import format_exception_only

from ftk.exception import NotSupportedException
from ftk.factor_types import ComputeJobType
from ftk.compute import ComputeStrategyMixin, ComputeBase
from ftk.base_estimator import AzureMLForecastRegressorBase
from ftk import TimeSeriesDataFrame


class PassThroughEstimator(BaseEstimator, RegressorMixin):
    """
    Estimator whose predictions are the same as the input 
    values. Needed for the `metric_from_scorer` function.
    """

    def fit(self):
        return self

    def predict(self, x):
        return x


def metric_from_scorer(scorer, is_multimetric):
    """
    Function to convert a sklearn.scorer object into a 
    metric function.
    """
    estimator = PassThroughEstimator()

    def metric_fun(x, y):
        return -_score(estimator, x, y, scorer, is_multimetric)
    return metric_fun


class CVWithPredictionMixin(ComputeStrategyMixin):
    """
    Internal class, shared Time Series Cross-Validation functionality for
    :class:`ftk.model_selection.TSRandomizedSearchCV`
    and :class:`ftk.model_selection.TSGridSearchCV`.
    """

    def fit_retain_predictions(self, X, y=None, groups=None, **fit_params):
        """
        Run fit with all sets of parameters and return the out of sample
        predictions along with the over all results. Used to overwrite the
        `fit` function.

        :param X:
            Training vector, where `n_samples` is the number of samples and
            `n_features` is the number of features.
        :type X: array-like, shape = [n_samples, n_features]

        :param y:
            Target relative to `X` for classification or regression;
            None for unsupervised learning.
        :type y:  array-like, shape = `[n_samples]` or `[n_samples, n_output]`, optional

        :param groups:
            Group labels for the samples used while splitting the dataset into
            train/test set.
        :type groups: array-like, with shape `(n_samples,)`, optional

        :param **fit_params:
            Parameters passed to the ``fit`` method of the estimator
        :type **fit_params: dict of string -> object
        """

        # Added in FTK
        if y is None:
            if not isinstance(X, TimeSeriesDataFrame):
                raise ValueError('For input X which is not '
                                 'TimeSeriesDataFrame, y argument must be '
                                 'provided with value not equal to None.')
            if X.ts_value_colname is None:
                raise ValueError('Both y and X.ts_value_colname is None. '
                                 'Please either provide y or make sure the '
                                 'input TimeSeriesDataFrame X has attribute '
                                 'ts_value_colname of value not equal to None.')
            y = X[X.ts_value_colname]
        ### End added in FTK ###

        if self.fit_params is not None:
            warnings.warn('"fit_params" as a constructor argument was '
                          'deprecated in version 0.19 and will be removed '
                          'in version 0.21. Pass fit parameters to the '
                          '"fit" method instead.', DeprecationWarning)
            if fit_params:
                warnings.warn('Ignoring fit_params passed as a constructor '
                              'argument in favor of keyword arguments to '
                              'the "fit" method.', RuntimeWarning)
            else:
                fit_params = self.fit_params
        estimator = self.estimator
        cv = check_cv(self.cv, y, classifier=is_classifier(estimator))

        scorers, self.multimetric_ = _check_multimetric_scoring(
            self.estimator, scoring=self.scoring)

        if self.multimetric_:
            if self.refit is not False and (
                    not isinstance(self.refit, six.string_types) or
                    # This will work for both dict / list (tuple)
                    self.refit not in scorers):
                raise ValueError("For multi-metric scoring, the parameter "
                                 "refit must be set to a scorer key "
                                 "to refit an estimator with the best "
                                 "parameter setting on the whole data and "
                                 "make the best_* attributes "
                                 "available for that metric. If this is not "
                                 "needed, refit should be set to False "
                                 "explicitly. %r was passed." % self.refit)
            else:
                refit_metric = self.refit
        else:
            refit_metric = 'score'

        X, y, groups = indexable(X, y, groups)

        n_splits = cv.get_n_splits(X, y, groups)

        ### Added in FTK ###
        # Check if estimator is RegressionForecaster, if so make sure
        # parameters start with `estimator__`
        if isinstance(self.estimator, AzureMLForecastRegressorBase):
            if isinstance(self.param_grid, dict):
                c = {k if k.startswith('estimator__') else
                     'estimator__' + str(k): v
                     for k, v in self.param_grid.items()}
                new_params = c
            else:
                new_params = []
                for c in self.param_grid:
                    c = {k if k.startswith('estimator__') else
                            'estimator__' + str(k): v
                            for k, v in c.items()}
                    new_params.append(c)
            candidate_params = new_params
            self.param_grid = candidate_params
        ### End Added in FTK ###

        # Regenerate parameter iterable for each fit
        candidate_params = list(self._get_param_iterator())
        n_candidates = len(candidate_params)
        if self.verbose > 0:
            print("Fitting {0} folds for each of {1} candidates, totalling"
                  " {2} fits".format(n_splits, n_candidates,
                                     n_candidates * n_splits))

        # Clone estimator
        base_estimator = clone(self.estimator)
        pre_dispatch = self.pre_dispatch

        ### Added in FTK ###
        # Changes made to use a dynamically specified
        # compute backend
        if self.compute_strategy is not None:

            # Pack all arguments as dict parameters.
            cvsearch_params = {}
            cvsearch_params['estimator'] = base_estimator,
            cvsearch_params['y'] = y
            cvsearch_params['scorers'] = scorers,
            cvsearch_params['fit_params'] = fit_params,
            cvsearch_params['verbose'] = self.verbose or 0,
            cvsearch_params['return_train_score'] = self.return_train_score,
            cvsearch_params['return_n_test_samples'] = True,
            cvsearch_params['return_times'] = True,
            cvsearch_params['return_parameters'] = False,
            cvsearch_params['error_score'] = self.error_score,
            cvsearch_params['cv'] = cv,
            cvsearch_params['groups'] = groups,
            cvsearch_params['candidate_params'] = candidate_params,

            # Invoke the generic execute_job on the `ComputeStrategyMixin`
            job_executor = self.execute_job(self.cvsearch_func_fit_score_predict,
                                            X,
                                            self.cvsearch_map_func,
                                            ComputeJobType.CVSearch,
                                            None,
                                            **cvsearch_params)
            if job_executor is None or (job_executor.errors is not None and len(job_executor.errors) > 0):
                raise Exception(job_executor.errors)
            else:
                # The result also needs unwrapped.
                if (isinstance(job_executor.job_results, list) and
                        len(job_executor.job_results) == 1):
                    out = job_executor.job_results[0]
                else:
                    out = job_executor.job_results

        ### End added in FTK ###
        # Default behavior, run parallel jobs locally
        else:
            ### Modified in FTK to use CVWithPredictionMixin._fit_score_predict ###
            out = Parallel(
                n_jobs=self.n_jobs, verbose=self.verbose,
                pre_dispatch=pre_dispatch
            )(delayed(CVWithPredictionMixin._fit_score_predict)(clone(base_estimator), X, y, scorers,
                                                                train, test, self.verbose, parameters,
                                                                fit_params=fit_params,
                                                                return_train_score=self.return_train_score,
                                                                return_n_test_samples=True,
                                                                return_times=True, return_parameters=False,
                                                                error_score=self.error_score)
              for parameters, (train, test) in product(candidate_params,
                                                       cv.split(X, y, groups)))

        # if one choose to see train score, "out" will contain train score info
        if self.return_train_score:
            ### Modified in FTK to accept outputs `train_results_dicts` `test_results_dicts`###
            (train_score_dicts, test_score_dicts, train_results_dicts, test_results_dicts,
                test_sample_counts, fit_time, score_time) = zip(*out)
        else:
            ### Modified in FTK to accept outputs `train_results_dicts` `test_results_dicts`###
            (test_score_dicts, test_results_dicts, test_sample_counts, fit_time,
             score_time) = zip(*out)

        # test_score_dicts and train_score dicts are lists of dictionaries and
        # we make them into dict of lists
        test_scores = _aggregate_score_dicts(test_score_dicts)
        if self.return_train_score:
            train_scores = _aggregate_score_dicts(train_score_dicts)

        # TODO: replace by a dict in 0.21
        results = (DeprecationDict() if self.return_train_score == 'warn'
                   else {})

        def _store(key_name, array, weights=None, splits=False, rank=False):
            """A small helper to store the scores/times to the cv_results_"""
            # When iterated first by splits, then by parameters
            # We want `array` to have `n_candidates` rows and `n_splits` cols.
            array = np.array(array, dtype=np.float64).reshape(n_candidates,
                                                              n_splits)
            if splits:
                for split_i in range(n_splits):
                    # Uses closure to alter the results
                    results["split%d_%s"
                            % (split_i, key_name)] = array[:, split_i]

            array_means = np.average(array, axis=1, weights=weights)
            results['mean_%s' % key_name] = array_means
            # Weighted std is not directly available in numpy
            array_stds = np.sqrt(np.average((array -
                                             array_means[:, np.newaxis]) ** 2,
                                            axis=1, weights=weights))
            results['std_%s' % key_name] = array_stds

            if rank:
                results["rank_%s" % key_name] = np.asarray(
                    rankdata(-array_means, method='min'), dtype=np.int32)  # pylint: disable=invalid-unary-operand-type

        _store('fit_time', fit_time)
        _store('score_time', score_time)
        # Use one MaskedArray and mask all the places where the param is not
        # applicable for that candidate. Use defaultdict as each candidate may
        # not contain all the params
        param_results = defaultdict(partial(MaskedArray,
                                            np.empty(n_candidates,),
                                            mask=True,
                                            dtype=object))
        for cand_i, params in enumerate(candidate_params):
            for name, value in params.items():
                # An all masked empty array gets created for the key
                # `"param_%s" % name` at the first occurence of `name`.
                # Setting the value at an index also unmasks that index
                param_results["param_%s" % name][cand_i] = value

        results.update(param_results)
        # Store a list of param dicts at the key 'params'
        results['params'] = candidate_params

        ### Added in FTK ###
        # Store the results of the individual cross-validation folds
        def create_results_dict(param, idxs, origins, fold_results):
            if len(origins) > 0:
                exper_design = product(param, zip(idxs, origins))
            else:
                exper_design = product(param, zip(idxs, [None]*len(idxs)))
            cv_predict = defaultdict(list)
            for exper, res in zip(exper_design, fold_results):
                for name in exper[0].keys():
                    cv_predict[name].extend([exper[0][name]]*len(exper[1][0]))
                cv_predict['idx'].extend(exper[1][0])
                if len(origins) > 0:
                    cv_predict['origin'].extend([exper[1][1]]*len(exper[1][0]))
                for name in res.keys():
                    cv_predict[name].extend(res[name])
            return cv_predict

        idx_vals = {'origin': [], 'idx': []}
        for tr, ts in cv.split(X, y, groups):
            idx_vals['idx'].append(ts)
            if hasattr(X, 'origin_time_colname') and X.origin_time_colname is None:
                idx_vals['origin'].append(max(X.time_index[tr]))

        predictions = create_results_dict(candidate_params,
                                          idx_vals['idx'],
                                          idx_vals['origin'],
                                          test_results_dicts)
        ### End added in FTK ###

        # NOTE test_sample counts (weights) remain the same for all candidates
        test_sample_counts = np.array(test_sample_counts[:n_splits],
                                      dtype=np.int)
        iid = self.iid
        if self.iid == 'warn':
            if len(np.unique(test_sample_counts)) > 1:
                warnings.warn("The default of the `iid` parameter will change "
                              "from True to False in version 0.22 and will be"
                              " removed in 0.24. This will change numeric"
                              " results when test-set sizes are unequal.",
                              DeprecationWarning)
            iid = True

        for scorer_name in scorers.keys():
            # Computed the (weighted) mean and std for test scores alone
            _store('test_%s' % scorer_name, test_scores[scorer_name],
                   splits=True, rank=True,
                   weights=test_sample_counts if iid else None)
            if self.return_train_score:
                prev_keys = set(results.keys())
                _store('train_%s' % scorer_name, train_scores[scorer_name],
                       splits=True)

                if self.return_train_score == 'warn':
                    for key in set(results.keys()) - prev_keys:
                        message = (
                            'You are accessing a training score ({!r}), '
                            'which will not be available by default '
                            'any more in 0.21. If you need training scores, '
                            'please set return_train_score=True').format(key)
                        # warn on key access
                        results.add_warning(key, message, FutureWarning)

        # For multi-metric evaluation, store the best_index_, best_params_ and
        # best_score_ iff refit is one of the scorer names
        # In single metric evaluation, refit_metric is "score"
        if self.refit or not self.multimetric_:
            self.best_index_ = results["rank_test_%s" % refit_metric].argmin()
            self.best_params_ = candidate_params[self.best_index_]
            self.best_score_ = results["mean_test_%s" % refit_metric][
                self.best_index_]

        if self.refit:
            self.best_estimator_ = clone(base_estimator).set_params(
                **self.best_params_)
            if y is not None:
                self.best_estimator_.fit(X, y, **fit_params)
            else:
                self.best_estimator_.fit(X, **fit_params)

        # Store the only scorer not as a dict for single metric evaluation
        self.scorer_ = scorers if self.multimetric_ else scorers['score']

        self.cv_results_ = results
        ### Added in FTK ###
        self.cv_predictions_ = predictions
        self.cv_predictions_ = self._construct_ts_from_cv_predictions(X)
        if y is not None and y.name is not None:
            self.cv_predictions_.rename(columns={'test_actuals': y.name},
                                        inplace=True)
            self.cv_predictions_.actual = y.name
        ### End Added in FTK ###
        self.n_splits_ = n_splits

        return self

    def predict_tsdf(self, X):
        """
        Call predict on the estimator with the best found parameters.
        Only available if ``refit=True`` and the underlying estimator supports
        ``predict``.

        :param X:
            Must fulfill the input assumptions of the
            underlying estimator.
        :type X: indexable, length `n_samples`

        :return:
            If the estimator is a :class:`ftk.models.RegressionForecaster` the return
            will be a :class:`ftk.dataframeforecast.ForecastDataFrame` with the forecasts and
            prediction distribution for the testing data. Otherwise, returns
            a ndarray of predictions.
        :rtype: ndarray, ForecastDataFrame
        """
        from ftk import ForecastDataFrame
        from scipy.stats import norm

        ret = self.best_estimator_.predict(X)
        if isinstance(ret, ForecastDataFrame):
            train_df = self.backtest()
            if ret is not None:
                error_stdev = []
                for i in [t for t in ret.origin_time_index.unique() if any(train_df.time_index <= t)]:
                    train_fold = train_df.loc[train_df.time_index <=
                                              i, :]  # pylint: disable=no-member
                    error_stdev.append(train_fold._stdev_by_slicekey())
                error_stdev = pd.concat(error_stdev)
            else:
                error_stdev = train_df._stdev_by_slicekey()
            # Next we need to alight these errors with the test data
            std_devs = ret._get_slice_vals(error_stdev)
            if ret.pred_dist is not None:
                dist_name = ret.pred_dist
            else:
                dist_name = 'DistributionForecast' + \
                    type(self.best_estimator_).__name__
            ret[dist_name] = [norm(loc=m, scale=s) if not np.isnan(s) else None for m, s in zip(
                ret.loc[:, ret.pred_point], std_devs)]
        return ret

    def backtest(self):
        """
        Extracts backtesting data from the cross-validation folds.
        """
        metric = metric_from_scorer(self.scorer_, self.multimetric_)
        return self.cv_predictions_.backtest(metric_fun=metric)

    def _construct_ts_from_cv_predictions(self, X):
        """
        Internal method to transform the ``cv_predictions_`` field from a
        ``dict`` into a :class:`ftk.multi_forecast_data_frame.MultiForecastDataFrame`
        using the index and metadata from ``X``.

        :params X:
            The :class:`ftk.time_series_data_frame.TimeSeriesDataFrame` used to fit ``self``
        :type X: TimeSeriesDataFrame

        :returns:
            :class:`ftk.multi_forecast_data_frame.MultiForecastDataFrame` of
            out of sample predictions from CV folds.
        :rtype: MultiForecastDataFrame
        """
        from ftk import MultiForecastDataFrame

        cv_pred = self.cv_predictions_
        cv_index = X.index[cv_pred['idx']]
        preds = pd.DataFrame(cv_pred, index=cv_index)
        preds.drop('idx', axis=1, inplace=True)
        param_names = list(self._get_param_iterator())[0].keys()
        meta_values = {}
        for name in X._metadata:
            meta_values[name] = getattr(X, name, None)
        if 'ts_value_colname' in meta_values.keys():
            meta_values['actual'] = meta_values.pop('ts_value_colname')
        meta_values['pred_point'] = 'test_predict'
        meta_values['actual'] = 'test_actuals'
        if X.origin_time_colname is None:
            meta_values['origin_time_colname'] = 'origin'
        # Make sure parameter datatypes are serializable
        for p in param_names:
            preds_p_column = [np.asscalar(obj) if isinstance(obj, np.generic)
                              else obj for obj in preds.loc[:, p]]
            try:
                preds.loc[:, p] = preds_p_column
            except ValueError:
                # this is for situation that the parameter value is not hashable
                # such as list, e.g order in Arima
                # This preds.loc[:, p] now stores a Pandas Series with each
                # element stores the object of parameter value. e.g For order
                #  in Arima, it will be a Pandas Series with a list as each
                # element.
                preds.loc[:, p] = pd.Series(preds_p_column, index=preds.index)

        # Put the parameter values into columns of the dataframe
        if hasattr(self.estimator, 'estimator'):
            preds['model_class'] = type(self.estimator.estimator).__name__
        else:
            preds['model_class'] = type(self.estimator).__name__
        preds['param_values'] = preds[list(
            param_names)].to_dict(orient='records')
        preds.drop(list(param_names), axis=1, inplace=True)
        preds = MultiForecastDataFrame(
            preds, model_colnames={'model_class': 'model_class',
                                   'param_values': 'param_values'},
            **meta_values)
        return preds

    def cvsearch_func_fit_score_predict(self, data, parameters, train, test, **kwargs):
        """
        This function is called from the FTK compute backends to fit a
        single model for a hyperparameter combination set during cvsearch.

        :param data:
            Training vector, where `n_samples` is the number of samples and
            `n_features` is the number of features.
        :type data: array-like, shape = `[n_samples, n_features]`

        :param parameters:
            Parameters to be set on the estimator.
        :type parameters: dict or None

        :param train:
            Indices of training samples.
        :type train: array-like, shape `(n_train_samples,)`

        :param test:
            Indices of test samples.
        :type train: array-like, shape `(n_test_samples,)`

        :param **kwargs:
            Parameters passed to the ``CVWithPredictionMixin._fit_score_predict``
            method of the estimator
        :type **kwargs: dict of string -> object
        """
        # Unwrap all parameters from the compute backend caller and callback
        # into the CVWithPredictionMixin._fit_score_predict method.
        # When unwrapped the parameters all come back as `list`. We have to grab
        # the first item of the list.
        # Unwrap parameters
        estimator = kwargs.pop('estimator', None)[0]
        y = kwargs.pop('y', None)
        scorers = kwargs.pop('scorers', None)[0]
        fit_params = kwargs.pop('fit_params', {})[0]
        verbose = kwargs.pop('verbose', 10)[0]
        return_train_score = kwargs.pop('return_train_score', True)[0]
        return_n_test_samples = kwargs.pop('return_n_test_samples', True)[0]
        return_times = kwargs.pop('return_times', True)[0]
        return_parameters = kwargs.pop('return_parameters', False)[0]
        error_score = kwargs.pop('error_score', None)[0]

        # Return fit_predict_score for the specific parameter set
        return CVWithPredictionMixin._fit_score_predict(estimator,
                                                        data,
                                                        y,
                                                        scorers,
                                                        train,
                                                        test,
                                                        verbose,
                                                        parameters,
                                                        fit_params=fit_params,
                                                        return_train_score=return_train_score,
                                                        return_n_test_samples=return_n_test_samples,
                                                        return_times=return_times,
                                                        return_parameters=return_parameters,
                                                        error_score=error_score)

    @staticmethod
    def _fit_score_predict(estimator, X, y, scorer, train, test, verbose,
                           parameters, fit_params, return_train_score=False,
                           return_parameters=False, return_n_test_samples=False,
                           return_times=False, return_estimator=False,
                           error_score='raise-deprecating'):
        """
        Fit estimator and compute scores for a given dataset split.  Return
        predictions along with fit and scores. Replaces function
        `sklearn:fit_and_score`.

        :param estimator:
            The object to use to fit the data.
        :type estimator: estimator object implementing 'fit'

        :param X: The data to fit.
        :type X: array-like of shape at least 2D

        :param y:
            The target variable to try to predict in the case of
            supervised learning.
        :type y: array-like, optional, default: None

        :param scorer:
            If it is a single callable, the return value for ``train_scores`` and
            ``test_scores`` is a single float.

            For a dict, it should be one mapping the scorer name to the scorer
            callable object / function.

            The callable object / fn should have signature
            ``scorer(estimator, X, y)``.
        :type scorer: A single callable or dict mapping scorer name to the callable

        :param train: Indices of training samples.
        :type train: array-like, shape `(n_train_samples,)`

        :param test: Indices of test samples.
        :type test: array-like, shape `(n_test_samples,)`

        :param verbose: The verbosity level.
        :type verbose: integer

        :param error_score:
            Value to assign to the score if an error occurs in estimator fitting.
            If set to 'raise', the error is raised. If a numeric value is given,
            FitFailedWarning is raised. This parameter does not affect the refit
            step, which will always raise the error. Default is 'raise' but in
            later versions it will change to np.nan.
        :type error_score: 'raise' or numeric

        :param parameters: Parameters to be set on the estimator.
        :type parameters: dict or None

        :param fit_params:
            Parameters that will be passed to ``estimator.fit``.
        :type fit_params: dict or None

        :param return_train_score:
            Compute and return score on training set.
        :type return_train_score: boolean, optional, default: False

        :param return_parameters:
            Return parameters that has been used for the estimator.
        :type return_parameters: boolean, optional, default: False

        :param return_n_test_samples:
            Whether to return the ``n_test_samples``
        :type return_n_test_samples: boolean, optional, default: False

        :param return_times :  Whether to return the fit/score times.
        :type return_times : boolean, optional, default: False

        :param return_estimator :  Whether to return the fitted estimator.
        :type return_estimator : boolean, optional, default: False

        :return: an object with the following fields

            train_scores : dict of scorer name -> float, optional
                Score on training set (for all the scorers),
                returned only if `return_train_score` is `True`.

            test_scores : dict of scorer name -> float, optional
                Score on testing set (for all the scorers).

            train_results : dict of predictions and actuals for
                for all validation folds, optional
                Predictions on training set (for all the scorers),
                returned only if `return_train_score` is `True`.

            test_scores : dict of predictions and actuals for
                for all validation folds.
                Predict on testing set (for all the scorers).

            n_test_samples : int
                Number of test samples.

            fit_time : float
                Time spent for fitting in seconds.

            score_time : float
                Time spent for scoring in seconds.

            parameters : dict or None, optional
                The parameters that have been evaluated.

            estimator : estimator object
                The fitted estimator
        """
        from ftk import ForecastDataFrame
        from ftk.models import RecursiveForecaster

        if verbose > 1:
            if parameters is None:
                msg = ''
            else:
                msg = '%s' % (', '.join('%s=%s' % (k, v)
                                        for k, v in parameters.items()))
            print("[CV] %s %s" % (msg, (64 - len(msg)) * '.'))

        # Adjust length of sample weights
        fit_params = fit_params if fit_params is not None else {}
        fit_params = dict([(k, _index_param_value(X, v, train))
                           for k, v in fit_params.items()])

        ### Added for FTK ###
        test_scores = {}

        # currently if trying to set return_train_score to True for
        # RecrusiveForecaster, a NotSupportedException will be thrown.
        if isinstance(estimator, RecursiveForecaster):
            if return_train_score:
                raise NotSupportedException('Currently, RecusiveForecaster '
                                            'does not support for in-sample '
                                            'predictions.')

        ### End Added for FTK ###

        train_scores = {}
        if parameters is not None:
            estimator.set_params(**parameters)

        start_time = time.time()

        X_train, y_train = _safe_split(estimator, X, y, train)
        X_test, y_test = _safe_split(estimator, X, y, test, train)

        is_multimetric = not callable(scorer)
        n_scorers = len(scorer.keys()) if is_multimetric else 1

        try:
            if y_train is None:
                estimator.fit(X_train, **fit_params)
            else:
                estimator.fit(X_train, y_train, **fit_params)

        except Exception as e:
            # Note fit time as time until error
            fit_time = time.time() - start_time
            score_time = 0.0
            if error_score == 'raise':
                raise
            elif error_score == 'raise-deprecating':
                warnings.warn("From version 0.22, errors during fit will result "
                              "in a cross validation score of NaN by default. Use "
                              "error_score='raise' if you want an exception "
                              "raised or error_score=np.nan to adopt the "
                              "behavior from version 0.22.",
                              FutureWarning)
                raise
            elif isinstance(error_score, numbers.Number):
                if is_multimetric:
                    test_scores = dict(zip(scorer.keys(),
                                           [error_score, ] * n_scorers))
                    if return_train_score:
                        train_scores = dict(zip(scorer.keys(),
                                                [error_score, ] * n_scorers))
                else:
                    test_scores = error_score
                    if return_train_score:
                        train_scores = error_score
                warnings.warn("Estimator fit failed. The score on this train-test"
                              " partition for these parameters will be set to %f. "
                              "Details: \n%s" %
                              (error_score, format_exception_only(
                                  type(e), e)[0]),
                              FitFailedWarning)
            else:
                raise ValueError("error_score must be the string 'raise' or a"
                                 " numeric value. (Hint: if using 'raise', please"
                                 " make sure that it has been spelled correctly.)")

        else:
            fit_time = time.time() - start_time
            # _score will return dict if is_multimetric is True
            test_scores = _score(estimator, X_test, y_test,
                                 scorer, is_multimetric)
            ### Added for FTK ###
            test_predict = estimator.predict(X_test)
            if isinstance(test_predict, ForecastDataFrame):
                test_predict = test_predict[test_predict.pred_point]
            test_results = {'test_predict': np.array(test_predict),
                            'test_actuals': np.array(y_test)}
            ### End Added for FTK ###
            score_time = time.time() - start_time - fit_time
            if return_train_score:
                train_scores = _score(estimator, X_train, y_train, scorer,
                                      is_multimetric)
                ### Added for FTK ###
                train_predict = estimator.predict(X_train)
                train_results = {'train_predict': np.array(train_predict),
                                 'train_actuals': np.array(y_train)}
                ### End Added for FTK ###

        if verbose > 2:
            if is_multimetric:
                for scorer_name, score in test_scores.items():
                    msg += ", %s=%s" % (scorer_name, score)
            else:
                msg += ", score=%s" % test_scores
        if verbose > 1:
            total_time = score_time + fit_time
            end_msg = "%s, total=%s" % (
                msg, logger.short_format_time(total_time))
            print("[CV] %s %s" % ((64 - len(end_msg)) * '.', end_msg))

        ### Added for FTK ###
        ret = [train_scores, test_scores,
               train_results] if return_train_score else [test_scores]
        ret.append(test_results)
        ### End Added for FTK ###
        if return_n_test_samples:
            ret.append(_num_samples(X_test))
        if return_times:
            ret.extend([fit_time, score_time])
        if return_parameters:
            ret.append(parameters)
        if return_estimator:
            ret.append(estimator)
        return ret

    def cvsearch_map_func(self, data, **kwargs):
        estimator = kwargs.pop('estimator', None)
        y = kwargs.pop('y', None)
        cv = kwargs.pop('cv', None)[0]
        # cv = check_cv(cv, y, classifier=is_classifier(estimator))
        groups = kwargs.pop('groups', [])
        if groups[0] == None:
            groups = None
        candidate_params = np.array(kwargs.pop('candidate_params', [])[0])
        return product(candidate_params, cv.split(data, y, groups))


class TSGridSearchCV(GridSearchCV, CVWithPredictionMixin):
    """
    Exhaustive search over specified parameter values for an estimator
    returning predictions from each cross-validation fold.

    Important members are fit, predict.

    TSGridSearchCV implements a "fit" and a "score" method.
    It also implements "predict", "predict_proba", "decision_function",
    "transform" and "inverse_transform" if they are implemented in the
    estimator used.

    The parameters of the estimator used to apply these methods are optimized
    by cross-validated grid-search over a parameter grid.

    Read more in the scikit-learn :ref:`User Guide <grid_search>`.


    Attributes:

    cv_results_ : dict of numpy (masked) ndarrays
        A dict with keys as column headers and values as columns, that can be
        imported into a pandas ``DataFrame``.

        For instance the below given table
        \`\`\`
        +------------+-----------+------------+-----------------+---+---------+
        \|param_kernel\|param_gamma\|param_degree\|split0_test_score\|...\|rank_t...\|
        +============+===========+============+=================+===+=========+
        \|  'poly'    \|     --    \|      2     \|       0.80      \|...\|    2    \|
        +------------+-----------+------------+-----------------+---+---------+
        \|  'poly'    \|     --    \|      3     \|       0.70      \|...\|    4    \|
        +------------+-----------+------------+-----------------+---+---------+
        \|  'rbf'     \|     0.1   \|     --     \|       0.80      \|...\|    3    \|
        +------------+-----------+------------+-----------------+---+---------+
        \|  'rbf'     \|     0.2   \|     --     \|       0.93      \|...\|    1    \|
        +------------+-----------+------------+-----------------+---+---------+
        \`\`\`

        will be represented by a ``cv_results_`` dict of:
        \`\`\`
            {
            'param_kernel': masked_array(data = ['poly', 'poly', 'rbf', 'rbf'],
                                         mask = [False False False False]...)
            'param_gamma': masked_array(data = [-- -- 0.1 0.2],
                                        mask = [ True  True False False]...),
            'param_degree': masked_array(data = [2.0 3.0 -- --],
                                         mask = [False False  True  True]...),
            'split0_test_score'  : [0.80, 0.70, 0.80, 0.93],
            'split1_test_score'  : [0.82, 0.50, 0.70, 0.78],
            'mean_test_score'    : [0.81, 0.60, 0.75, 0.85],
            'std_test_score'     : [0.01, 0.10, 0.05, 0.08],
            'rank_test_score'    : [2, 4, 3, 1],
            'split0_train_score' : [0.80, 0.92, 0.70, 0.93],
            'split1_train_score' : [0.82, 0.55, 0.70, 0.87],
            'mean_train_score'   : [0.81, 0.74, 0.70, 0.90],
            'std_train_score'    : [0.01, 0.19, 0.00, 0.03],
            'mean_fit_time'      : [0.73, 0.63, 0.43, 0.49],
            'std_fit_time'       : [0.01, 0.02, 0.01, 0.01],
            'mean_score_time'    : [0.01, 0.06, 0.04, 0.04],
            'std_score_time'     : [0.00, 0.00, 0.00, 0.01],
            'params'             : [{'kernel': 'poly', 'degree': 2}, ...],
            }
        \`\`\`

        NOTE

        The key ``'params'`` is used to store a list of parameter
        settings dicts for all the parameter candidates.

        The ``mean_fit_time``, ``std_fit_time``, ``mean_score_time`` and
        ``std_score_time`` are all in seconds.

        For multi-metric evaluation, the scores for all the scorers are
        available in the ``cv_results_`` dict at the keys ending with that
        scorer's name (``'_<scorer_name>'``) instead of ``'_score'`` shown
        above. ('split0_test_precision', 'mean_train_precision' etc.)

    cv_predictions_ : :class:`ftk.multi_forecast_data_frame.MultiForecastDataFrame`
        A MultiForecastDataFrame containing the best out of sameple predictions
        from the folds of cross-validation.

    best_estimator_ : estimator or dict
        Estimator that was chosen by the search, i.e. estimator
        which gave highest score (or smallest loss if specified)
        on the left out data. Not available if ``refit=False``.

        See ``refit`` parameter for more information on allowed values.

    best_score_ : float
        Mean cross-validated score of the best_estimator

        For multi-metric evaluation, this is present only if ``refit`` is
        specified.

    best_params_ : dict
        Parameter setting that gave the best results on the hold out data.

        For multi-metric evaluation, this is present only if ``refit`` is
        specified.

    best_index_ : int
        The index (of the ``cv_results_`` arrays) which corresponds to the best
        candidate parameter setting.

        The dict at ``search.cv_results_['params'][search.best_index_]`` gives
        the parameter setting for the best model, that gives the highest
        mean score (``search.best_score_``).

        For multi-metric evaluation, this is present only if ``refit`` is
        specified.

    scorer_ : function or a dict
        Scorer function used on the held out data to choose the best
        parameters for the model.

        For multi-metric evaluation, this attribute holds the validated
        ``scoring`` dict which maps the scorer key to the scorer callable.

    n_splits_ : int
        The number of cross-validation splits (folds/iterations).


    Notes:

    The parameters selected are those that maximize the score of the left out
    data, unless an explicit score is passed in which case it is used instead.

    If `n_jobs` was set to a value higher than one, the data is copied for each
    point in the grid (and not `n_jobs` times). This is done for efficiency
    reasons if individual jobs take very little time, but may raise errors if
    the dataset is large and not enough memory is available.  A workaround in
    this case is to set `pre_dispatch`. Then, the memory is copied only
    `pre_dispatch` many times. A reasonable value for `pre_dispatch` is `2 *
    n_jobs`.


    See Also:

    :class:`sklearn.ParameterGrid`:
        generates all the combinations of a hyperparameter grid.

    :func:`sklearn.model_selection.train_test_split`:
        utility function to split the data into a development set usable
        for fitting a GridSearchCV instance and an evaluation set for
        its final evaluation.

    :func:`sklearn.metrics.make_scorer`:
        Make a scorer from a performance metric or loss function.


    :param estimator:
        This is assumed to implement the scikit-learn estimator interface.
        Either estimator needs to provide a ``score`` function,
        or ``scoring`` must be passed.
    :type estimator: estimator object.

    :param param_grid:
        Dictionary with parameters names (string) as keys and lists of
        parameter settings to try as values, or a list of such
        dictionaries, in which case the grids spanned by each dictionary
        in the list are explored. This enables searching over any sequence
        of parameter settings.
    :type param_grid: dict or list of dictionaries

    :param scoring:
        A single string (see :ref:`scoring_parameter`) or a callable
        (see :ref:`scoring`) to evaluate the predictions on the test set.

        For evaluating multiple metrics, either give a list of (unique) strings
        or a dict with names as keys and callables as values.

        NOTE that when using custom scorers, each scorer should return a single
        value. Metric functions returning a list/array of values can be wrapped
        into multiple scorers that return one value each.

        See :ref:`multimetric_grid_search` for an example.

        If None, the estimator's default scorer (if available) is used.
    :type scoring: string, callable, list/tuple, dict or None, default: None

    :param fit_params:
        Parameters to pass to the fit method.

        .. deprecated::
           ``fit_params`` as a constructor argument was deprecated in version
           0.19 of scikit-learn and will be removed in version 0.21. Pass fit
           parameters to the ``fit`` method instead.
    :type fit_params: dict, optional

    :param n_jobs:
        Number of jobs to run in parallel.
    :type n_jobs: int, default=1

    :param pre_dispatch:
        Controls the number of jobs that get dispatched during parallel
        execution. Reducing this number can be useful to avoid an
        explosion of memory consumption when more jobs get dispatched
        than CPUs can process. This parameter can be:

            - None, in which case all the jobs are immediately
              created and spawned. Use this for lightweight and
              fast-running jobs, to avoid delays due to on-demand
              spawning of the jobs

            - An int, giving the exact number of total jobs that are
              spawned

            - A string, giving an expression as a function of n_jobs,
              as in '2*n_jobs'
    :type pre_dispatch: int, or string, optional

    :param iid:
        If True, return the average score across folds, weighted by the number
        of samples in each test set. In this case, the data is assumed to be
        identically distributed across the folds, and the loss minimized is
        the total loss per sample, and not the mean loss across the folds. If
        False, return the average score across folds. Default is True, but
        will change to False in version 0.21, to correspond to the standard
        definition of cross-validation.

        ..versionchanged:: 0.20
            Parameter ``iid`` will change from True to False by default in
            version 0.22, and will be removed in 0.24.
    :type iid: boolean, default='warn'

    :param cv:
        Determines the cross-validation splitting strategy.
        Possible inputs for cv are:
          * None, to use the default 3-fold cross validation,
          * integer, to specify the number of folds in a `(Stratified)KFold`,
          * An object to be used as a cross-validation generator.
          * An iterable yielding train, test splits.

        For integer/None inputs, if the estimator is a classifier and ``y`` is
        either binary or multiclass, :class:`sklearn.StratifiedKFold` is used. In all
        other cases, :class:`sklearn.KFold` is used.

        Refer :ref:`User Guide <cross_validation>` for the various
        cross-validation strategies that can be used here.
    :type cv: int, cross-validation generator or an iterable, optional

    :param refit:
        Refit an estimator using the best found parameters on the whole
        dataset.

        For multiple metric evaluation, this needs to be a string denoting the
        scorer is used to find the best parameters for refitting the estimator
        at the end.

        The refitted estimator is made available at the ``best_estimator_``
        attribute and permits using ``predict`` directly on this
        ``TSGridSearchCV`` instance.

        Also for multiple metric evaluation, the attributes ``best_index_``,
        ``best_score_`` and ``best_parameters_`` will only be available if
        ``refit`` is set and all of them will be determined w.r.t this specific
        scorer.

        See ``scoring`` parameter to know more about multiple metric
        evaluation.
    :type refit: boolean, or string, default=True

    :param verbose:
        Controls the verbosity: the higher, the more messages.
    :type verbose: integer

    :param error_score:
        Value to assign to the score if an error occurs in estimator fitting.
        If set to 'raise', the error is raised. If a numeric value is given,
        FitFailedWarning is raised. This parameter does not affect the refit
        step, which will always raise the error. Default is 'raise' but from
        version 0.22 it will change to np.nan.
    :type error_score: 'raise' or numeric

    :param return_train_score:
        If ``False``, the ``cv_results_`` attribute will not include training
        scores.

        Current default is ``'warn'``, which behaves as ``True`` in addition
        to raising a warning when a training score is looked up.
        That default will be changed to ``False`` in later versions.
        Computing training scores is used to get insights on how different
        parameter settings impact the overfitting/underfitting trade-off.
        However computing the scores on the training set can be computationally
        expensive and is not strictly required to select the parameters that
        yield the best generalization performance.
    :type return_train_score: boolean, optional

    Examples:

    >>> from sklearn.linear_model import Lasso
    >>> from ftk.model_selection import TSGridSearchCV
    >>> from ftk.data import load_dominicks_oj_dataset
    >>> df, _ = load_dominicks_oj_dataset()
    >>> target = self.train_tsdf.ts_value_colname
    >>> y = self.train_tsdf[target]
    >>> X = self.train_tsdf.copy()
    >>> X.ts_value_colname = None
    >>> X.drop([target], axis=1, inplace=True)
    >>> parameters = {'alpha': np.logspace(0, 3, 3)}
    >>> lasso = Lasso()
    >>> clf = TSGridSearchCV(lasso, parameters)
    >>> clf.fit(X, y)

    """

    def fit(self, *args, **kwargs):
        return self.fit_retain_predictions(*args, **kwargs)

    def predict(self, *args, **kwargs):
        return self.predict_tsdf(*args, **kwargs)
    
    def _get_param_iterator(self):
        """
        Redefine the _get_param_iterator from :class: GridSearchCV to allow
        compatibility with new scikit**-**learn versions.
        """
        superclass = super(TSGridSearchCV, self)
        # If _get_param_iterator is present in the suprerclkass, return it.
        if hasattr(superclass, '_get_param_iterator') and callable(getattr(superclass, '_get_param_iterator')):
            return superclass._get_param_iterator()
        # If it is a version of sklearn >= 0.20rc1 implment this method.
        return ParameterGrid(self.param_grid)


class TSRandomizedSearchCV(CVWithPredictionMixin, RandomizedSearchCV):
    """
    Randomized search on hyper parameters.

    RandomizedSearchCV implements a "fit" and a "score" method.
    It also implements "predict", "predict_proba", "decision_function",
    "transform" and "inverse_transform" if they are implemented in the
    estimator used.

    The parameters of the estimator used to apply these methods are optimized
    by cross-validated search over parameter settings.

    In contrast to :class:`ftk.model_selection.search.TSGridSearchCV`, not all
    parameter values are tried out, but rather a fixed number of parameter
    settings is sampled from the specified distributions. The number of parameter
    settings that are tried is given by `n_iter`.

    If all parameters are presented as a list,
    sampling without replacement is performed. If at least one parameter
    is given as a distribution, sampling with replacement is used.
    It is highly recommended to use continuous distributions for continuous
    parameters.

    Read more in the sklearn :ref:`User Guide <randomized_parameter_search>`.

    .. _sklearn.ParameterSampler: http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.ParameterSampler.html
    .. _scipy.stats.distributions: https://docs.scipy.org/doc/scipy/reference/stats.html
    Attributes:

    cv_results_ : dict of numpy (masked) ndarrays
        A dict with keys as column headers and values as columns, that can be
        imported into a pandas ``DataFrame``.

        For instance the below given table
        \`\`\`
        +--------------+-------------+-------------------+---+---------------+
        \| param_kernel \| param_gamma \| split0_test_score \|...\|rank_test_score\|
        +==============+=============+===================+===+===============+
        \|    'rbf'     \|     0.1     \|       0.80        \|...\|       2       \|
        +--------------+-------------+-------------------+---+---------------+
        \|    'rbf'     \|     0.2     \|       0.90        \|...\|       1       \|
        +--------------+-------------+-------------------+---+---------------+
        \|    'rbf'     \|     0.3     \|       0.70        \|...\|       1       \|
        +--------------+-------------+-------------------+---+---------------+
        \`\`\`
        will be represented by a ``cv_results_`` dict of:
        \`\`\`
            {
            'param_kernel' : masked_array(data = ['rbf', 'rbf', 'rbf'],
                                          mask = False),
            'param_gamma'  : masked_array(data = [0.1 0.2 0.3], mask = False),
            'split0_test_score'  : [0.80, 0.90, 0.70],
            'split1_test_score'  : [0.82, 0.50, 0.70],
            'mean_test_score'    : [0.81, 0.70, 0.70],
            'std_test_score'     : [0.01, 0.20, 0.00],
            'rank_test_score'    : [3, 1, 1],
            'split0_train_score' : [0.80, 0.92, 0.70],
            'split1_train_score' : [0.82, 0.55, 0.70],
            'mean_train_score'   : [0.81, 0.74, 0.70],
            'std_train_score'    : [0.01, 0.19, 0.00],
            'mean_fit_time'      : [0.73, 0.63, 0.43],
            'std_fit_time'       : [0.01, 0.02, 0.01],
            'mean_score_time'    : [0.01, 0.06, 0.04],
            'std_score_time'     : [0.00, 0.00, 0.00],
            'params'             : [{'kernel' : 'rbf', 'gamma' : 0.1}, ...],
            }
        \`\`\`
        NOTE

        The key ``'params'`` is used to store a list of parameter
        settings dicts for all the parameter candidates.

        The ``mean_fit_time``, ``std_fit_time``, ``mean_score_time`` and
        ``std_score_time`` are all in seconds.

        For multi-metric evaluation, the scores for all the scorers are
        available in the ``cv_results_`` dict at the keys ending with that
        scorer's name (``'_<scorer_name>'``) instead of ``'_score'`` shown
        above. ('split0_test_precision', 'mean_train_precision' etc.)

    cv_predictions_ : dict of numpy (masked) ndarrays
        A dict with keys as column headers and values as columns, that can be
        imported into a pandas ``DataFrame``.  Contains the parameter values,
        row index of the data being predicted from `X`, predicted value, and
        the actual value from `y`.

    best_estimator_ : estimator or dict
        Estimator that was chosen by the search, i.e. estimator
        which gave highest score (or smallest loss if specified)
        on the left out data. Not available if ``refit=False``.

        For multi-metric evaluation, this attribute is present only if
        ``refit`` is specified.

        See ``refit`` parameter for more information on allowed values.

    best_score_ : float
        Mean cross-validated score of the best_estimator.

        For multi-metric evaluation, this is not available if ``refit`` is
        ``False``. See ``refit`` parameter for more information.

    best_params_ : dict
        Parameter setting that gave the best results on the hold out data.

        For multi-metric evaluation, this is not available if ``refit`` is
        ``False``. See ``refit`` parameter for more information.

    best_index_ : int
        The index (of the ``cv_results_`` arrays) which corresponds to the best
        candidate parameter setting.

        The dict at ``search.cv_results_['params'][search.best_index_]`` gives
        the parameter setting for the best model, that gives the highest
        mean score (``search.best_score_``).

        For multi-metric evaluation, this is not available if ``refit`` is
        ``False``. See ``refit`` parameter for more information.

    scorer_ : function or a dict
        Scorer function used on the held out data to choose the best
        parameters for the model.

        For multi-metric evaluation, this attribute holds the validated
        ``scoring`` dict which maps the scorer key to the scorer callable.

    n_splits_ : int
        The number of cross-validation splits (folds/iterations).

    NOTES:

    The parameters selected are those that maximize the score of the held-out
    data, according to the scoring parameter.

    If `n_jobs` was set to a value higher than one, the data is copied for each
    parameter setting(and not `n_jobs` times). This is done for efficiency
    reasons if individual jobs take very little time, but may raise errors if
    the dataset is large and not enough memory is available.  A workaround in
    this case is to set `pre_dispatch`. Then, the memory is copied only
    `pre_dispatch` many times. A reasonable value for `pre_dispatch` is `2 *
    n_jobs`.


    See Also:

    :class:`fkt.model_selection.search.TSGridSearchCV` :
        Does exhaustive search over a grid of parameters.

    sklearn.ParameterSampler_:
        A generator over parameter settins, constructed from
        param_distributions.

    :param estimator:
        A object of that type is instantiated for each grid point.
        This is assumed to implement the scikit-learn estimator interface.
        Either estimator needs to provide a ``score`` function,
        or ``scoring`` must be passed.
    :type estimator: estimator object.

    :param param_distributions:
        Dictionary with parameters names (string) as keys and distributions
        or lists of parameters to try. Distributions must provide a ``rvs``
        method for sampling (such as those from scipy.stats.distributions_).
        If a list is given, it is sampled uniformly.
    :type param_distributions: dict

    :param n_iter:
        Number of parameter settings that are sampled. n_iter trades
        off runtime vs quality of the solution.
    :type n_iter: int, default=10

    :param scoring:
        A single string (see :ref:`scoring_parameter`) or a callable
        (see :ref:`scoring`) to evaluate the predictions on the test set.

        For evaluating multiple metrics, either give a list of (unique) strings
        or a dict with names as keys and callables as values.

        NOTE that when using custom scorers, each scorer should return a single
        value. Metric functions returning a list/array of values can be wrapped
        into multiple scorers that return one value each.

        See :ref:`multimetric_grid_search` for an example.

        If None, the estimator's default scorer (if available) is used.
    :type scoring: string, callable, list/tuple, dict or None, default: None

    :param fit_params:
        Parameters to pass to the fit method.

        .. deprecated:: 0.19
           ``fit_params`` as a constructor argument was deprecated in version
           0.19 and will be removed in version 0.21. Pass fit parameters to
           the ``fit`` method instead.
    :type fit_params: dict, optional

    :param n_jobs:
        Number of jobs to run in parallel.
    :type n_jobs: int, default=1

    :param pre_dispatch:
        Controls the number of jobs that get dispatched during parallel
        execution. Reducing this number can be useful to avoid an
        explosion of memory consumption when more jobs get dispatched
        than CPUs can process. This parameter can be:

            - None, in which case all the jobs are immediately
              created and spawned. Use this for lightweight and
              fast-running jobs, to avoid delays due to on-demand
              spawning of the jobs

            - An int, giving the exact number of total jobs that are
              spawned

            - A string, giving an expression as a function of n_jobs,
              as in '2*n_jobs'
    :type pre_dispatch: int, or string, optional

    :param iid:
        If True, return the average score across folds, weighted by the number
        of samples in each test set. In this case, the data is assumed to be
        identically distributed across the folds, and the loss minimized is
        the total loss per sample, and not the mean loss across the folds. If
        False, return the average score across folds. Default is True, but
        will change to False in version 0.21, to correspond to the standard
        definition of cross-validation.

        ..versionchanged:: 0.20
            Parameter ``iid`` will change from True to False by default in
            version 0.22, and will be removed in 0.24.
    :type iid: boolean, default='warn'

    :param cv:
        Determines the cross-validation splitting strategy.
        Possible inputs for cv are:
          - None, to use the default 3-fold cross validation,
          - integer, to specify the number of folds in a `(Stratified)KFold`,
          - An object to be used as a cross-validation generator.
          - An iterable yielding train, test splits.

        For integer/None inputs, if the estimator is a classifier and ``y`` is
        either binary or multiclass, :class:`sklearn.StratifiedKFold` is used. In all
        other cases, :class:`sklearn.KFold` is used.

        Refer sklearn :ref:`User Guide <cross_validation>` for the various
        cross-validation strategies that can be used here.
    :type cv: int, cross-validation generator or an iterable, optional

    :param refit:
        Refit an estimator using the best found parameters on the whole
        dataset.

        For multiple metric evaluation, this needs to be a string denoting the
        scorer that would be used to find the best parameters for refitting
        the estimator at the end.

        The refitted estimator is made available at the ``best_estimator_``
        attribute and permits using ``predict`` directly on this
        ``RandomizedSearchCV`` instance.

        Also for multiple metric evaluation, the attributes ``best_index_``,
        ``best_score_`` and ``best_parameters_`` will only be available if
        ``refit`` is set and all of them will be determined w.r.t this specific
        scorer.

        See ``scoring`` parameter to know more about multiple metric
        evaluation.
    :type refit: boolean, or string default=True

    :param verbose:
        Controls the verbosity: the higher, the more messages.
    :type verbose: integer

    :param random_state:
        Pseudo random number generator state used for random uniform sampling
        from lists of possible values instead of scipy.stats distributions_.
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.
    :type random_state: int, RandomState instance or None, optional, default=None

    :param error_score:
        Value to assign to the score if an error occurs in estimator fitting.
        If set to 'raise', the error is raised. If a numeric value is given,
        FitFailedWarning is raised. This parameter does not affect the refit
        step, which will always raise the error. Default is 'raise' but from
        version 0.22 it will change to np.nan.
    :type error_score: 'raise' or numeric

    :param return_train_score:
        If ``False``, the ``cv_results_`` attribute will not include training
        scores.
        Current default is ``'warn'``, which behaves as ``True`` in addition
        to raising a warning when a training score is looked up.
        That default will be changed to ``False`` in 0.21.
        Computing training scores is used to get insights on how different
        parameter settings impact the overfitting/underfitting trade-off.
        However computing the scores on the training set can be computationally
        expensive and is not strictly required to select the parameters that
        yield the best generalization performance.
    :type return_train_score: boolean, optional

    """

    def fit(self, *args, **kwargs):
        return self.fit_retain_predictions(*args, **kwargs)

    def predict(self, *args, **kwargs):
        return self.predict_tsdf(*args, **kwargs)
