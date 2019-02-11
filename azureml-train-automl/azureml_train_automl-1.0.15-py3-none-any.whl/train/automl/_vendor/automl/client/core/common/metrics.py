# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Computation of available metrics."""
import copy
import sys

import numpy as np
import scipy.stats as st
import sklearn.metrics
import sklearn.preprocessing

from automl.client.core.common import constants
from automl.client.core.common import logging_utilities as log_utils


def minimize_or_maximize(metric, task=None):
    """Select the objective given a metric.

    Some metrics should be minimized and some should be maximized
    :param metric: the name of the metric to look up
    :param task: one of constants.Tasks.
    :return: returns one of constants.OptimizerObjectives.
    """
    if task is None:
        reg_metrics = get_default_metric_with_objective(
            constants.Tasks.REGRESSION)
        class_metrics = get_default_metric_with_objective(
            constants.Tasks.CLASSIFICATION)
        if metric in reg_metrics:
            task = constants.Tasks.REGRESSION
        elif metric in class_metrics:
            task = constants.Tasks.CLASSIFICATION
        else:
            msg = 'Could not find objective for metric "{0}"'.format(metric)
            raise ValueError(msg)
    return get_default_metric_with_objective(task)[metric]


def is_better(val1, val2, metric=None, task=None, objective=None):
    """Select the best of two values given metric or objectives.

    :param val1: scalar value
    :param val2: scalar value
    :param metric: the name of the metric to look up
    :param task: one of constants.Tasks.
    :param objective: one of constants.OptimizerObjectives.
    return: returns a boolean of if val1 is better than val2 in the situation
    """
    if objective is None:
        if metric is None:
            print("Must specific either Metric or Objective")
        else:
            objective = minimize_or_maximize(metric, task)
    if objective == constants.OptimizerObjectives.MAXIMIZE:
        return val1 > val2
    elif objective == constants.OptimizerObjectives.MINIMIZE:
        return val1 < val2


def get_all_nan(task):
    """Create a dictionary of metrics to values for the given task.

    All metric values are set to nan initially
    :param task: one of constants.Tasks.
    :return: returns a dictionary of nans for each metric for the task.
    """
    metrics = get_default_metric_with_objective(task)
    return {m: np.nan for m in metrics}


def get_metric_ranges(task, for_assert_sane=False):
    """Get the metric range for the task.

    :param task: string "classification" or "regression"
    :param for_assert_sane: boolean indicates that this is being used
        by assert_metrics_sane and it is unsafe to apply clips.
    :return: returns tuple with min values dict and max value dict.
    """
    minimums = get_min_values(task)
    maximums = get_max_values(task, for_assert_sane=for_assert_sane)
    return minimums, maximums


def get_worst_values(task, for_assert_sane=False):
    """Get the worst values for metrics of the task.

    :param task: string "classification" or "regression"
    :param for_assert_sane: boolean indicates that this is being used
        by assert_metrics_sane and it is unsafe to apply clips.
    :return: returns a dictionary of metrics with the worst values.
    """
    minimums, maximums = get_metric_ranges(
        task, for_assert_sane=for_assert_sane)
    metrics = get_default_metric_with_objective(task)
    _MAX = constants.OptimizerObjectives.MAXIMIZE
    bad = {m: minimums[m] if obj == _MAX else maximums[m]
           for m, obj in metrics.items()}
    return bad


def get_min_values(task):
    """Get the minimum values for metrics for the task.

    :param task: string "classification" or "regression"
    :return: returns a dictionary of metrics with the min values.
    """
    metrics = get_default_metric_with_objective(task)
    # 0 is the minimum for metrics that are minimized and maximized
    bad = {m: 0.0 for m, obj in metrics.items()}
    bad[constants.Metric.R2Score] = -10.0  # R2 is different, clipped to -10.0
    bad[constants.Metric.Spearman] = -1.0
    return bad


def get_max_values(task, for_assert_sane=False):
    """Get the maximum values for metrics of the task.

    :param task: string "classification" or "regression"
    :param for_assert_sane: boolean indicates that this is being used
        by assert_metrics_sane and it is unsafe to apply clips.
    :return: returns a dictionary of metrics with the max values.
    """
    metrics = get_default_metric_with_objective(task)
    _MAX = constants.OptimizerObjectives.MAXIMIZE
    bad = {m: 1.0 if obj == _MAX else sys.float_info.max
           for m, obj in metrics.items()}
    # so the assertions don't fail, could also clip metrics instead
    if not for_assert_sane:
        bad[constants.Metric.LogLoss] = 10.0
        bad[constants.Metric.NormRMSE] = 10.0
        bad[constants.Metric.NormRMSLE] = 10.0
        bad[constants.Metric.NormMeanAbsError] = 10.0
        bad[constants.Metric.NormMedianAbsError] = 10.0
    return bad


def assert_metrics_sane(metrics, task):
    """Assert that the given metric values are sane.

    The metric values should not be worse than the worst possible values
    for those metrics given the objectives for those metrics
    :param task: string "classification" or "regression"
    """
    worst = get_worst_values(task, for_assert_sane=True)
    obj = get_default_metric_with_objective(task)
    for k, v in metrics.items():
        if not np.isscalar(v) or np.isnan(v):
            continue
        # This seems to vary a lot.
        if k == constants.Metric.ExplainedVariance:
            continue
        if obj[k] == constants.OptimizerObjectives.MAXIMIZE:
            assert v >= worst[k], (
                '{0} is not worse than {1} for metric {2}'.format(
                    worst[k], v, k))
        else:
            assert v <= worst[k], (
                '{0} is not worse than {1} for metric {2}'.format(
                    worst[k], v, k))


def get_default_metric_with_objective(task):
    """Get the dictionary of metric -> objective for the given task.

    :param task: string "classification" or "regression"
    :return: dictionary of metric -> objective
    """
    if task == constants.Tasks.CLASSIFICATION:
        return constants.MetricObjective.Classification
    elif task == constants.Tasks.REGRESSION:
        return constants.MetricObjective.Regression
    else:
        raise NotImplementedError


def get_scalar_metrics(task):
    """Get the scalar metrics supported for a given task.

    :param task: string "classification" or "regression"
    :return: a list of the default metrics supported for the task
    """
    if task == constants.Tasks.CLASSIFICATION:
        return list(constants.Metric.SCALAR_CLASSIFICATION_SET)
    elif task == constants.Tasks.REGRESSION:
        return list(constants.Metric.SCALAR_REGRESSION_SET)
    else:
        raise NotImplementedError


def get_default_metrics(task):
    """Get the metrics supported for a given task as a set.

    :param task: string "classification" or "regression"
    :return: a list of the default metrics supported for the task
    """
    if task == constants.Tasks.CLASSIFICATION:
        return constants.Metric.CLASSIFICATION_SET
    elif task == constants.Tasks.REGRESSION:
        return constants.Metric.REGRESSION_SET
    else:
        raise NotImplementedError


def add_padding_for_missing_class_labels(pred_proba_result, trained_class_labels, class_labels):
    """Add padding to the predicted probabilities for missing class labels.

    For the case when a model was trained on less classes than what the dataset contains
    we'll add corresponding columns to predict_proba result with 0 probability.

    :param pred_proba_result: predicted value (in probability in case of classification)
    :param trained_class_labels: the class labels detected by the trained model
    :param class_labels: the class labels detected from the entire dataset
    :return: predicted probabilities
    """
    if trained_class_labels is not None and \
            class_labels is not None and \
            len(trained_class_labels) != len(class_labels):
        # in case the classifier was trained on less class labels than what the dataset contains,
        # we need to iterate through all the dataset classes and when we see a gap in the predictions
        # we'll have to insert an empty column with probability 0
        trained_class_labels_clone = copy.deepcopy(trained_class_labels)
        # we'll iterate through the dataset classes with the following index
        dataset_class_index = 0
        # we'll iterate through this model's classes with the following index
        model_class_index = 0
        dataset_class_number = len(class_labels)
        while len(trained_class_labels_clone) != dataset_class_number:
            expected_dataset_class = class_labels[dataset_class_index]
            # if the classes match we increment both indices
            if model_class_index < len(trained_class_labels_clone) and expected_dataset_class == \
                    trained_class_labels_clone[model_class_index]:
                model_class_index += 1
                dataset_class_index += 1
            else:
                # otherwise, we'll have to add the expected class and it's corresponding probabilities set to 0
                pred_proba_result = np.insert(pred_proba_result,
                                              model_class_index,
                                              np.zeros((pred_proba_result.shape[0],)),
                                              axis=1)
                trained_class_labels_clone = np.insert(trained_class_labels_clone,
                                                       model_class_index,
                                                       expected_dataset_class)
        if not np.array_equal(trained_class_labels_clone, class_labels):
            raise ValueError("The padding of trained model classes resulted in an inconsistency. ({}) vs ({})".
                             format(trained_class_labels_clone, class_labels))
    return pred_proba_result


def compute_metrics(y_pred,
                    y_test,
                    metrics=None,
                    task=constants.Tasks.CLASSIFICATION,
                    sample_weight=None,
                    num_classes=None,
                    class_labels=None,
                    trained_class_labels=None,
                    y_transformer=None,
                    y_max=None, y_min=None, y_std=None,
                    bin_info=None):
    """Compute the metrics given the test data results.

    :param y_pred: predicted value (in probability in case of classification)
    :param y_test: target value
    :param metrics: metric/metrics to compute
    :param num_classes: num of classes for classification task
    :param class_labels: labels for classification task
    :param trained_class_labels: labels for classification task as identified by the trained model
    :param task: ml task
    :param y_max: max target value for regression task
    :param y_min: min target value for regression task
    :param y_std: standard deviation of regression targets
    :param sample_weight: weights for samples in dataset
    :return: returns a dictionary with metrics computed
    """
    if metrics is None:
        metrics = get_default_metrics(task)

    if task == constants.Tasks.CLASSIFICATION:
        return compute_metrics_classification(y_pred, y_test, metrics,
                                              num_classes=num_classes,
                                              sample_weight=sample_weight,
                                              class_labels=class_labels,
                                              trained_class_labels=trained_class_labels,
                                              y_transformer=y_transformer)
    elif task == constants.Tasks.REGRESSION:
        return compute_metrics_regression(y_pred, y_test, metrics,
                                          y_max, y_min, y_std,
                                          sample_weight=sample_weight,
                                          bin_info=bin_info)
    else:
        raise NotImplementedError


def compute_metrics_classification(y_pred_probs, y_test, metrics,
                                   num_classes=None, sample_weight=None,
                                   class_labels=None, trained_class_labels=None,
                                   y_transformer=None, logger=None):
    """
    Compute the metrics for a classification task.

    All class labels for y should come
    as seen by the fitted model (i.e. if the fitted model uses a y transformer the labels
    should also come transformed).

    All metrics present in `metrics` will be present in the output dictionary with either
    the value(s) calculated or `nan` if metrics
    calculation failed.

    :param y_pred_probs: The probability predictions.
    :param y_test: The target value. Transformed if using a y transformer.
    :param metrics: metric/metrics to compute
    :type metrics: list
    :param class_labels:
        Labels for classification task. This should be the entire y label set. These should
         be transformed if using a y transformer. Required for all non-scalars to be calculated.
    :param trained_class_labels:
        Labels for classification task as seen (trained on) by the
        trained model. Required when training set did not see all classes from full set.
    :param num_classes: Number of classes in the entire y set. Required for all metrics.
    :param sample_weight:
        The sample weight to be used on metrics calculation. This does not need
        to match sample weights on the fitted model.
    :param y_transformer: Used to inverse transform labels from `y_test`. Required for non-scalar metrics.
    :param logger: A logger to log errors and warnings
    :return: A dictionary with metrics computed.
    """
    if logger is None:
        logger = log_utils.NULL_LOGGER

    logger.info("Computing classification metrics")

    if y_pred_probs is None:
        raise ValueError("y_pred_probs must not be None")
    if y_test is None:
        raise ValueError("y_test must not be None")

    if y_test.dtype == np.float32 or y_test.dtype == np.float64:
        # Assume that the task is set appropriately and that the data
        # just had a float label arbitrarily.
        y_test = y_test.astype(np.int64)

    # Some metrics use an eps of 1e-15 by default, which results in nans
    # for float32.
    if y_pred_probs.dtype == np.float32:
        y_pred_probs = y_pred_probs.astype(np.float64)

    if num_classes is None:
        num_classes = max(len(np.unique(y_test)), y_pred_probs.shape[1])

    if metrics is None:
        metrics = get_default_metrics(constants.Tasks.CLASSIFICATION)

    y_test = np.ravel(y_test)

    results = {}

    binarizer = sklearn.preprocessing.LabelBinarizer()

    if class_labels is not None:
        binarizer.fit(class_labels)
    else:
        binarizer.fit(y_test)

    y_test_bin = binarizer.transform(y_test)

    # we need to make sure that we have probabilities from all classes in the dataset
    # in case the trained model wasn't fitted on the entire set of class labels
    y_pred_probs = add_padding_for_missing_class_labels(y_pred_probs,
                                                        trained_class_labels,
                                                        class_labels)

    y_pred_probs_full = y_pred_probs
    y_pred_bin = np.argmax(y_pred_probs_full, axis=1)

    if class_labels is not None:
        y_pred_bin = class_labels[y_pred_bin]

    if num_classes is None:
        num_classes = max(len(np.unique(y_test)), len(np.unique(y_pred_bin)))

    if num_classes == 2:
        # if both classes probs are passed, pick the positive class probs as
        # binarizer only outputs single column
        y_pred_probs = y_pred_probs[:, 1]

    # For accuracy table and confusion matrix,
    # the y_test_original is used to keep label consistency.
    # For other metrics, the y_test is passed.
    y_test_original = y_test
    if class_labels is not None:
        class_labels_original = class_labels
    if y_transformer is not None:
        y_test_original = y_transformer.inverse_transform(y_test_original)
        if class_labels is not None:
            class_labels_original = y_transformer.inverse_transform(class_labels_original)

    if constants.Metric.Accuracy in metrics:
        results[constants.Metric.Accuracy] = try_calculate_metric(
            score=sklearn.metrics.accuracy_score,
            y_true=y_test, y_pred=y_pred_bin,
            sample_weight=sample_weight,
            logger=logger)

    if constants.Metric.WeightedAccuracy in metrics:
        # accuracy weighted by number of elements for each class
        w = np.ones(y_test.shape[0])
        for idx, i in enumerate(np.bincount(y_test.ravel())):
            w[y_test.ravel() == idx] *= (i / float(y_test.ravel().shape[0]))
        results[constants.Metric.WeightedAccuracy] = try_calculate_metric(
            score=sklearn.metrics.accuracy_score,
            y_true=y_test, y_pred=y_pred_bin,
            sample_weight=w,
            logger=logger)

    if constants.Metric.NormMacroRecall in metrics:
        # this is what is used here
        # https://github.com/ch-imad/AutoMl_Challenge/blob/2353ec0
        # /Starting_kit/scoring_program/libscores.py#L187
        # for the AutoML challenge
        # https://competitions.codalab.org/competitions/2321
        # #learn_the_details-evaluation
        # This is a normalized macro averaged recall, rather than accuracy
        # https://github.com/scikit-learn/scikit-learn/issues/6747
        # #issuecomment-217587210
        # Random performance is 0.0 perfect performance is 1.0
        cmat = try_calculate_metric(
            sklearn.metrics.confusion_matrix,
            y_true=y_test, y_pred=y_pred_bin,
            sample_weight=sample_weight,
            logger=logger)
        if isinstance(cmat, float):
            results[constants.Metric.NormMacroRecall] = \
                constants.Defaults.DEFAULT_PIPELINE_SCORE
        else:
            R = 1 / num_classes
            cms = cmat.sum(axis=1)
            if cms.sum() == 0:
                results[constants.Metric.NormMacroRecall] = \
                    constants.Defaults.DEFAULT_PIPELINE_SCORE
            else:
                results[constants.Metric.NormMacroRecall] = max(
                    0.0,
                    (np.mean(cmat.diagonal() / cmat.sum(axis=1)) - R) /
                    (1 - R))

    if constants.Metric.LogLoss in metrics:
        results[constants.Metric.LogLoss] = try_calculate_metric(
            sklearn.metrics.log_loss,
            y_true=y_test, y_pred=y_pred_probs,
            labels=np.arange(0, num_classes),
            sample_weight=sample_weight,
            logger=logger)

    for name in metrics:
        # TODO: Remove this conditional once all metrics implement
        # the Metric interface for compute and aggregate
        if name in [constants.Metric.AccuracyTable,
                    constants.Metric.ConfusionMatrix]:
            try:
                metric_class = Metric.get_metric_class(name)
                metric = metric_class(y_test_original, y_pred_probs_full)
                score = metric.compute(sample_weights=sample_weight,
                                       class_labels=class_labels_original)
                results[name] = score
            except Exception:
                if Metric.is_scalar(name):
                    results[name] = np.nan
                else:
                    results[name] = Metric.get_error_metric()

    for m in metrics:
        if 'AUC' in m:
            results[m] = try_calculate_metric(
                sklearn.metrics.roc_auc_score,
                y_true=y_test_bin, y_score=y_pred_probs,
                average=m.replace('AUC_', ''),
                sample_weight=sample_weight,
                logger=logger)

        if 'f1_score' in m:
            results[m] = try_calculate_metric(
                sklearn.metrics.f1_score,
                y_true=y_test, y_pred=y_pred_bin,
                average=m.replace('f1_score_', ''),
                sample_weight=sample_weight,
                logger=logger)

        if 'precision_score' in m and 'average' not in m:
            results[m] = try_calculate_metric(
                sklearn.metrics.precision_score,
                y_true=y_test, y_pred=y_pred_bin,
                average=m.replace('precision_score_', ''),
                sample_weight=sample_weight,
                logger=logger)

        if 'recall_score' in m or m == constants.Metric.BalancedAccuracy:
            if 'recall_score' in m:
                average_modifier = m.replace('recall_score_', '')
            elif m == constants.Metric.BalancedAccuracy:
                average_modifier = 'macro'
            results[m] = try_calculate_metric(
                sklearn.metrics.recall_score,
                y_true=y_test, y_pred=y_pred_bin,
                average=average_modifier,
                sample_weight=sample_weight,
                logger=logger)

        if 'average_precision_score' in m:
            results[m] = try_calculate_metric(
                sklearn.metrics.average_precision_score,
                y_true=y_test_bin, y_score=y_pred_probs,
                average=m.replace('average_precision_score_', ''),
                sample_weight=sample_weight,
                logger=logger)

    assert_metrics_sane(results, constants.Tasks.CLASSIFICATION)
    return results


def compute_mean_cv_scores(scores, metrics):
    """Compute mean scores across validation folds.

    :param scores: scores of matrics
    :param metrics: list of metrics to compute means for.
    :return: mean score for each of the metrics.
    """
    means = {}
    for name in metrics:
        if name in scores[0]:
            split_results = [score[name] for score in scores if name in score]
            if name in constants.Metric.SCALAR_FULL_SET:
                means[name] = float(np.mean(split_results))
            elif name in constants.Metric.NONSCALAR_FULL_SET:
                metric_class = Metric.get_metric_class(name)
                means[name] = metric_class.aggregate(split_results)

    for train_type in constants.TrainingResultsType.ALL_TIME:
        train_times = [res[train_type] for res in scores if train_type in res]
        if train_times:
            means[train_type] = float(np.mean(train_times))

    return means


def try_calculate_metric(score, logger=None, **kwargs):
    """Calculate the metric given a metric calculation function.

    :param score: an sklearn metric calculation function to score
    :param logger: a logger (or SafeLogger) for logging errors
    :return: the calculated score (or nan if there was an exception)
    """
    try:
        return score(**kwargs)
    except Exception as e:
        log_utils.log_traceback(e, logger)
        return constants.Defaults.DEFAULT_PIPELINE_SCORE


def compute_metrics_regression(y_pred, y_test, metrics,
                               y_max=None,
                               y_min=None,
                               y_std=None,
                               sample_weight=None,
                               bin_info=None,
                               logger=None):
    """
    Compute the metrics for a regression task.

    `y_max`, `y_min`, and `y_std` should be based on `y_test` information unless
    you would like to compute multiple metrics for comparison (ex. cross validation),
    in which case, you should use a common range and standard deviation. You may
    also pass in `y_max`, `y_min`, and `y_std` if you do not want it to be calculated.

    All metrics present in `metrics` will be present in the output dictionary with either
    the value(s) calculated or `nan` if metric calculation failed.

    :param y_pred: The predict values.
    :param y_test: The target values.
    :param metrics: List of metric names for metrics to calculate.
    :type metrics: list
    :param y_max: The max target value.
    :param y_min: The min target value.
    :param y_std: The standard deviation of targets value.
    :param sample_weight:
        The sample weight to be used on metrics calculation. This does not need
        to match sample weights on the fitted model.
    :param bin_info:
        The binning information for true values. This should be calculated from
        :class:`ClientDatasets` :func:`make_bin_info`. Required for calculating
        non-scalar metrics.
    :param logger: A logger to log errors and warnings
    :return: A dictionary with metrics computed.
    """
    if logger is None:
        logger = log_utils.NULL_LOGGER

    logger.info("Computing regression metrics")

    if y_pred is None:
        raise ValueError("y_pred must not be None")
    if y_test is None:
        raise ValueError("y_test must not be None")

    if y_min is None:
        y_min = np.min(y_test)
    if y_max is None:
        y_max = np.max(y_test)
        assert y_max > y_min
    if y_std is None:
        y_std = np.std(y_test)

    if metrics is None:
        metrics = get_default_metrics(constants.Tasks.REGRESSION)

    results = {}

    # Regression metrics The scale of some of the metrics below depends on the
    # scale of the data. For this reason, we rescale it by the distance between
    # y_max and y_min. Since this can produce negative values we take the abs
    # of the distance https://en.wikipedia.org/wiki/Root-mean-square_deviation

    if constants.Metric.ExplainedVariance in metrics:
        bac = sklearn.metrics.explained_variance_score(
            y_test, y_pred, sample_weight=sample_weight,
            multioutput='uniform_average')
        results[constants.Metric.ExplainedVariance] = bac

    if constants.Metric.R2Score in metrics:
        bac = sklearn.metrics.r2_score(
            y_test, y_pred,
            sample_weight=sample_weight, multioutput='uniform_average')
        results[constants.Metric.R2Score] = np.clip(
            bac, constants.Metric.CLIPS_NEG[constants.Metric.R2Score], 1.0)

    if constants.Metric.Spearman in metrics:
        bac = st.spearmanr(y_test, y_pred)[0]
        results[constants.Metric.Spearman] = bac

        # mean AE
    if constants.Metric.MeanAbsError in metrics:
        bac = sklearn.metrics.mean_absolute_error(
            y_test, y_pred,
            sample_weight=sample_weight, multioutput='uniform_average')
        results[constants.Metric.MeanAbsError] = bac

    if constants.Metric.NormMeanAbsError in metrics:
        bac = sklearn.metrics.mean_absolute_error(
            y_test, y_pred,
            sample_weight=sample_weight, multioutput='uniform_average')
        bac = bac / np.abs(y_max - y_min)
        results[constants.Metric.NormMeanAbsError] = bac

    # median AE
    if constants.Metric.MedianAbsError in metrics:
        bac = sklearn.metrics.median_absolute_error(y_test, y_pred)
        results[constants.Metric.MedianAbsError] = bac

    if constants.Metric.NormMedianAbsError in metrics:
        bac = sklearn.metrics.median_absolute_error(y_test, y_pred)
        bac = bac / np.abs(y_max - y_min)
        results[constants.Metric.NormMedianAbsError] = bac

    # RMSE
    if constants.Metric.RMSE in metrics:
        bac = np.sqrt(
            sklearn.metrics.mean_squared_error(
                y_test, y_pred, sample_weight=sample_weight,
                multioutput='uniform_average'))
        results[constants.Metric.RMSE] = bac

    if constants.Metric.NormRMSE in metrics:
        bac = np.sqrt(
            sklearn.metrics.mean_squared_error(
                y_test, y_pred, sample_weight=sample_weight,
                multioutput='uniform_average'))
        bac = bac / np.abs(y_max - y_min)
        results[constants.Metric.NormRMSE] = np.clip(
            bac, 0,
            constants.Metric.CLIPS_POS.get(constants.Metric.NormRMSE, 100))

    # RMSLE
    if constants.Metric.RMSLE in metrics:
        bac = None
        try:
            bac = np.sqrt(
                sklearn.metrics.mean_squared_log_error(
                    y_test, y_pred, sample_weight=sample_weight,
                    multioutput='uniform_average')
            )
            bac = np.clip(
                bac, 0,
                constants.Metric.CLIPS_POS.get(constants.Metric.RMSLE, 100))
        except ValueError as e:
            log_utils.log_traceback(e, logger)
            bac = np.nan
        results[constants.Metric.RMSLE] = bac

    if constants.Metric.NormRMSLE in metrics:
        bac = None
        try:
            bac = np.sqrt(
                sklearn.metrics.mean_squared_log_error(
                    y_test, y_pred, sample_weight=sample_weight,
                    multioutput='uniform_average'))
            bac = bac / np.abs(np.log1p(y_max) - np.log1p(y_min))
            bac = np.clip(
                bac, 0,
                constants.Metric.CLIPS_POS.get(
                    constants.Metric.NormRMSLE, 100))
        except ValueError as e:
            log_utils.log_traceback(e, logger)
            bac = np.nan
        results[constants.Metric.NormRMSLE] = bac

    for name in metrics:
        # TODO: Remove this conditional once all metrics implement
        # the Metric interface for compute and aggregate
        if name in [constants.Metric.Residuals,
                    constants.Metric.PredictedTrue]:
            try:
                metric_class = Metric.get_metric_class(name)
                metric = metric_class(y_test, y_pred)
                results[name] = metric.compute(bin_info=bin_info,
                                               y_std=y_std)
            except Exception:
                if Metric.is_scalar(name):
                    results[name] = np.nan
                else:
                    results[name] = Metric.get_error_metric()

    assert_metrics_sane(results, constants.Tasks.REGRESSION)
    return results


class Metric:
    """Abstract class for all metrics."""

    SCHEMA_TYPE = 'schema_type'
    SCHEMA_VERSION = 'schema_version'
    DATA = 'data'

    ERRORS = 'errors'

    def __init__(self, y, y_pred):
        """Initialize the metric class.

        :param y: True labels for computing the metric
        :param y_pred: predicted labels for computing the metric
        """
        if y.shape[0] != y_pred.shape[0]:
            raise ValueError("Mismatched input shapes: y={}, y_pred={}"
                             .format(y.shape, y_pred.shape))
        self._y = y
        self._y_pred = y_pred
        self._data = {}

    @staticmethod
    def aggregate(scores):
        """Fold several scores from a computed metric together.

        :param scores: a list of computed scores
        :return: the aggregated scores
        """
        raise NotImplementedError

    @staticmethod
    def check_aggregate_scores(scores):
        """
        Check that the scores to be aggregated are reasonable.

        :param scores: scores computed by a metric
        :return: an aggregated score of the same shape as each of the inputs
        """
        if len(scores) == 0:
            raise ValueError("Scores must not be empty to aggregate")
        if np.nan in scores:
            return False
        for score in scores:
            if Metric.is_error_metric(score):
                return False
        return True

    @staticmethod
    def is_error_metric(score):
        """
        Get whether the given score is an error metric.

        :param score: the score to test
        :return: True if the metric errored on computation, otherwise False
        """
        return Metric.ERRORS in score

    @staticmethod
    def get_error_metric(message=None):
        """
        Get a dictionary representation of a failed nonscalar metric.

        :param message: the error message that was thrown
        :return: dictionary with the error message
        """
        if message is None:
            message = "Unexpected error occurred while calculating metric"
        return {
            Metric.ERRORS: [str(message)]
        }

    @staticmethod
    def is_scalar(metric_name):
        """
        Check whether a given metric is scalar or nonscalar.

        :param metric_name: the name of the metric found in constants.py
        :return: boolean for if the metric is scalar
        """
        if metric_name in constants.Metric.SCALAR_FULL_SET:
            return True
        elif metric_name in constants.Metric.NONSCALAR_FULL_SET:
            return False
        raise ValueError("{} metric is not supported".format(metric_name))

    @staticmethod
    def _data_to_dict(schema_type, schema_version, data):
        return {
            Metric.SCHEMA_TYPE: schema_type,
            Metric.SCHEMA_VERSION: schema_version,
            Metric.DATA: data
        }

    @staticmethod
    def get_metric_class(metric_name):
        """Return the metric class based on the constant name of the metric.

        :param metric: the constant name of the metric
        :return: the class of the metric
        """
        class_map = {
            constants.Metric.AccuracyTable: AccuracyTableMetric,
            constants.Metric.ConfusionMatrix: ConfusionMatrixMetric,
            constants.Metric.Residuals: ResidualsMetric,
            constants.Metric.PredictedTrue: PredictedTrueMetric
        }
        if metric_name not in class_map:
            raise ValueError("Metric class {} was not found in \
                              Metric.get_metric_class".format(metric_name))
        return class_map[metric_name]

    @staticmethod
    def _make_json_safe(o):
        make_safe = Metric._make_json_safe
        scalar_types = [int, float, str, type(None)]
        if type(o) in scalar_types:
            return o
        elif isinstance(o, dict):
            return {k: make_safe(v) for k, v in o.items()}
        elif isinstance(o, list):
            return [make_safe(v) for v in o]
        elif isinstance(o, tuple):
            return tuple(make_safe(v) for v in o)
        elif isinstance(o, np.ndarray):
            return make_safe(o.tolist())
        else:
            raise ValueError("Cannot encode type {}".format(type(o)))


class ClassificationMetric(Metric):
    """Abstract class for classification metrics."""

    def compute(self, sample_weights=None, class_labels=None):
        """Compute the metric.

        :param sample_weights: the weighting of each sample in the calculation
        :param class_labels: the labels for the classes in the dataset
        :return: the computed metric
        """
        raise NotImplementedError


class RegressionMetric(Metric):
    """Abstract class for regression metrics."""

    def compute(self, sample_weights=None, bin_info=None,
                y_min=None, y_max=None, y_std=None):
        """Compute the metric.

        :param sample_weights: the weighting of each sample in the calculation
        :param bin_info: metadata about the dataset needed to compute bins
            for some metrics
        :param y_min: the minimum target value
        :param y_max: the maximum target value
        :param y_std: the standard deviation of targets
        :return: the computed metric
        """
        raise NotImplementedError


class AccuracyTableMetric(ClassificationMetric):
    """
    Accuracy Table Metric.

    The accuracy table metric is a multi-use non-scalar metric
    that can be used to produce multiple types of line charts
    that vary continuously over the space of predicted probabilities.
    Examples of these charts are ROC, precision-recall, and lift curves.

    The calculation of the accuracy table is similar to the calculation
    of an ROC curve. An ROC curve stores true positive rates and
    false positive rates at many different probability thresholds.
    The accuracy table stores the raw number of
    true positives, false positives, true negatives, and false negatives
    at many probability thresholds.

    Probability thresholds are evenly spaced thresholds between 0 and 1.
    If NUM_POINTS were 5 the probability thresholds would be
    [0.0, 0.25, 0.5, 0.75, 1.0].
    These thresholds are useful for computing charts where you want to
    sample evenly over the space of predicted probabilities.

    Percentile thresholds are spaced according to the distribution of
    predicted probabilities. Each threshold corresponds to the percentile
    of the data at a probability threshold.
    For example, if NUM_POINTS were 5, then the first threshold would be at
    the 0th percentile, the second at the 25th percentile, the
    third at the 50th, and so on.

    The probability tables and percentile tables are both 3D lists where
    the first dimension represents the class label*, the second dimension
    represents the sample at one threshold (scales with NUM_POINTS),
    and the third dimension always has 4 values: TP, FP, TN, FN, and
    always in that order.

    * The confusion values (TP, FP, TN, FN) are computed with the
    one vs. rest strategy. See the following link for more details:
    `https://en.wikipedia.org/wiki/Multiclass_classification`
    """

    SCHEMA_TYPE = constants.Metric.SCHEMA_TYPE_ACCURACY_TABLE
    SCHEMA_VERSION = 'v1'

    NUM_POINTS = 100

    PROB_TABLES = 'probability_tables'
    PERC_TABLES = 'percentile_tables'
    PROB_THOLDS = 'probability_thresholds'
    PERC_THOLDS = 'percentile_thresholds'
    CLASS_LABELS = 'class_labels'

    @staticmethod
    def _data_to_dict(data):
        schema_type = AccuracyTableMetric.SCHEMA_TYPE
        schema_version = AccuracyTableMetric.SCHEMA_VERSION
        return super(AccuracyTableMetric, AccuracyTableMetric)\
            ._data_to_dict(schema_type, schema_version, data)

    def _build_tables(self, class_labels):
        """Build the following items.

        builds tables and thresholds for probability
        and percentile threshold spacing.
        """
        y_labels = np.unique(self._y)
        y_label_map = {l: idx for idx, l in enumerate(y_labels)}
        y_indices = [y_label_map[v] for v in self._y]
        y_bin = np.eye(len(y_labels), dtype=int)[y_indices]
        data = zip(y_bin.T, self._y_pred.T)

        prob_tables, perc_tables = [], []
        num_points = AccuracyTableMetric.NUM_POINTS
        prob_thresholds = np.linspace(0, 1, num_points)
        percs = prob_thresholds * 100

        for c_y_bin, c_y_pred in data:
            perc_thresholds = np.percentile(c_y_pred, percs)
            prob_table = self._create_class_samples(c_y_bin, c_y_pred,
                                                    prob_thresholds)
            perc_table = self._create_class_samples(c_y_bin, c_y_pred,
                                                    perc_thresholds)
            prob_tables.append(prob_table)
            perc_tables.append(perc_table)

        # Add missing tables from classes not included in training data
        full_prob, full_perc = self._include_missing_labels(class_labels,
                                                            prob_tables,
                                                            perc_tables,
                                                            y_label_map)
        self._data[AccuracyTableMetric.PROB_TABLES] = full_prob
        self._data[AccuracyTableMetric.PERC_TABLES] = full_perc
        self._data[AccuracyTableMetric.PROB_THOLDS] = prob_thresholds
        self._data[AccuracyTableMetric.PERC_THOLDS] = percs

    def _include_missing_labels(self, class_labels, prob_tables,
                                perc_tables, y_label_map):
        full_prob_tables, full_perc_tables = [], []
        for class_label in class_labels:
            if class_label in y_label_map:
                y_index = y_label_map[class_label]
                full_prob_tables.append(prob_tables[y_index])
                full_perc_tables.append(perc_tables[y_index])
            else:
                empty_table = np.zeros((len(self._y), 4), dtype=int)
                full_prob_tables.append(empty_table)
                full_perc_tables.append(empty_table)
        return full_prob_tables, full_perc_tables

    def _create_class_samples(self, class_y_bin, class_y_pred, thresholds):
        """Calculate the confusion values at all thresholds for one class."""
        table = []
        num_positive = np.sum(class_y_bin)
        num_samples = class_y_bin.size
        for threshold in thresholds:
            under_threshold = class_y_bin[class_y_pred < threshold]
            fn = np.sum(under_threshold)
            tn = under_threshold.size - fn
            tp, fp = num_positive - fn, num_samples - num_positive - tn
            conf_values = np.array([tp, fp, tn, fn], dtype=int)
            table.append(conf_values)
        return table

    def compute(self, sample_weights=None, class_labels=None):
        """Compute the score for the metric."""
        if class_labels is None:
            raise ValueError("Class labels required to compute AccuracyTable")
        string_labels = [str(label) for label in class_labels]
        self._data[AccuracyTableMetric.CLASS_LABELS] = string_labels
        self._build_tables(class_labels)
        ret = AccuracyTableMetric._data_to_dict(self._data)
        return Metric._make_json_safe(ret)

    @staticmethod
    def aggregate(scores):
        """Fold several scores from a computed metric together.

        :param scores: a list of computed scores
        :return: the aggregated scores
        """
        if not Metric.check_aggregate_scores(scores):
            return Metric.get_error_metric()

        score_data = [score[Metric.DATA] for score in scores]
        prob_tables = [d[AccuracyTableMetric.PROB_TABLES] for d in score_data]
        perc_tables = [d[AccuracyTableMetric.PERC_TABLES] for d in score_data]
        data_agg = {
            AccuracyTableMetric.PROB_TABLES: (
                np.sum(prob_tables, axis=0)),
            AccuracyTableMetric.PERC_TABLES: (
                np.sum(perc_tables, axis=0)),
            AccuracyTableMetric.PROB_THOLDS: (
                score_data[0][AccuracyTableMetric.PROB_THOLDS]),
            AccuracyTableMetric.PERC_THOLDS: (
                score_data[0][AccuracyTableMetric.PERC_THOLDS]),
            AccuracyTableMetric.CLASS_LABELS: (
                score_data[0][AccuracyTableMetric.CLASS_LABELS])
        }
        ret = AccuracyTableMetric._data_to_dict(data_agg)
        return Metric._make_json_safe(ret)


class ConfusionMatrixMetric(ClassificationMetric):
    """
    Confusion Matrix Metric.

    This metric is a wrapper around the sklearn confusion matrix.
    The metric data contains the class labels and a 2D list
    for the matrix itself.
    See the following link for more details on how the metric is computed:
    `https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html`
    """

    SCHEMA_TYPE = constants.Metric.SCHEMA_TYPE_CONFUSION_MATRIX
    SCHEMA_VERSION = 'v1'

    MATRIX = 'matrix'
    CLASS_LABELS = 'class_labels'

    @staticmethod
    def _data_to_dict(data):
        schema_type = ConfusionMatrixMetric.SCHEMA_TYPE
        schema_version = ConfusionMatrixMetric.SCHEMA_VERSION
        return Metric._data_to_dict(schema_type, schema_version, data)

    def _compute_matrix(self, class_labels, sample_weights=None):
        """Compute the matrix from prediction data."""
        y_pred_indexes = np.argmax(self._y_pred, axis=1)
        y_pred_labels = class_labels[y_pred_indexes]
        y_true = self._y

        if y_pred_labels.dtype.kind == 'f':
            class_labels = class_labels.astype(str)
            y_true = y_true.astype(str)
            y_pred_labels = y_pred_labels.astype(str)

        return sklearn.metrics.confusion_matrix(y_true=y_true,
                                                y_pred=y_pred_labels,
                                                sample_weight=sample_weights,
                                                labels=class_labels)

    def compute(self, sample_weights=None, class_labels=None):
        """Compute the score for the metric."""
        if class_labels is None:
            raise ValueError("Class labels required to compute \
                             ConfusionMatrixMetric")
        string_labels = [str(label) for label in class_labels]
        self._data[ConfusionMatrixMetric.CLASS_LABELS] = string_labels
        matrix = self._compute_matrix(class_labels,
                                      sample_weights=sample_weights)
        self._data[ConfusionMatrixMetric.MATRIX] = matrix
        ret = ConfusionMatrixMetric._data_to_dict(self._data)
        return Metric._make_json_safe(ret)

    @staticmethod
    def aggregate(scores):
        """Folds several scores from a computed metric together.

        :param scores: a list of computed scores
        :return: the aggregated scores
        """
        if not Metric.check_aggregate_scores(scores):
            return Metric.get_error_metric()

        score_data = [score[Metric.DATA] for score in scores]
        matrices = [d[ConfusionMatrixMetric.MATRIX] for d in score_data]
        matrix_sum = np.sum(matrices, axis=0)
        agg_class_labels = score_data[0][ConfusionMatrixMetric.CLASS_LABELS]
        data_agg = {
            ConfusionMatrixMetric.CLASS_LABELS: agg_class_labels,
            ConfusionMatrixMetric.MATRIX: matrix_sum
        }
        ret = ConfusionMatrixMetric._data_to_dict(data_agg)
        return Metric._make_json_safe(ret)


class ResidualsMetric(RegressionMetric):
    """
    Residuals Metric.

    This metric contains the data needed to display a histogram of
    residuals for a regression task.
    The residuals are predicted - actual.

    The bounds of this histogram are determined by the standard
    deviation of the targets for the full dataset. This value is
    passed to the metrics module as y_std. This is why y_std is
    required to compute this metric.
    The first and last bins are not necessarily the same width as
    the other bins. The first bin is [y_min, -2 * y_std].
    The last bin is [2 * y_std, y_max].
    If the regressor performs fairly well most of the residuals will
    be around zero and less than the standard deviation of the original
    data.

    The internal edges are evenly spaced.
    """

    SCHEMA_TYPE = constants.Metric.SCHEMA_TYPE_RESIDUALS
    SCHEMA_VERSION = 'v1'

    EDGES = 'bin_edges'
    COUNTS = 'bin_counts'

    @staticmethod
    def _data_to_dict(data):
        schema_type = ResidualsMetric.SCHEMA_TYPE
        schema_version = ResidualsMetric.SCHEMA_VERSION
        return Metric._data_to_dict(schema_type, schema_version, data)

    def compute(self, sample_weights=None, bin_info=None,
                y_min=None, y_max=None, y_std=None):
        """Compute metric.

        :param sample_weights: a list of sample weights for the data
        :param bin_info: metadata about the dataset needed to compute bins
            for some metrics
        :param y_min: minimum target value for the full dataset
        :param y_max: maximum target value for the full dataset
        :param y_std: standard deviation of target values
        :return: the metric
        """
        if y_std is None:
            raise ValueError("y_std required to compute ResidualsMetric")

        num_bins = 10
        # If full dataset targets are all zero we still need a bin
        y_std = y_std if y_std != 0 else 1
        residuals = self._y_pred - self._y
        counts, edges = ResidualsMetric._hist_by_bound(residuals, 2 * y_std, num_bins)
        ResidualsMetric._simplify_edges(residuals, edges)

        self._data[ResidualsMetric.EDGES] = edges
        self._data[ResidualsMetric.COUNTS] = counts
        ret = ResidualsMetric._data_to_dict(self._data)
        return Metric._make_json_safe(ret)

    @staticmethod
    def _hist_by_bound(values, bound, num_bins):
        # Need to subtract one because num_bins needs (num_bins + 1) edges, but we also have inf/-inf.
        num_edges = num_bins - 1
        min_decimal_places = 2

        bound = abs(bound)
        num_bound_decimal_places = int(max(min_decimal_places, -1 * np.log10(bound) + (min_decimal_places + 1)))
        bound = np.ceil(bound * (10 ** num_bound_decimal_places)) / (10 ** num_bound_decimal_places)

        bin_size = bound / num_edges
        bin_edges = np.linspace(-bound, bound, num_edges)
        num_decimal_places = int(max(min_decimal_places, -1 * np.log10(bin_size) + (min_decimal_places + 1)))
        for i, edge in enumerate(bin_edges):
            bin_edges[i] = np.around(edge, decimals=num_decimal_places)
        bins = np.r_[-np.inf, bin_edges, np.inf]
        return np.histogram(values, bins=bins)

    @staticmethod
    def _simplify_edges(residuals, edges):
        """Set the first and last edges of the histogram to be real numbers.

        If the minimum residual is in the outlier bin then the left
        edge is set to that residual value. Otherwise, the left edge
        is set to be evenly spaced with the rest of the bins
        This is repeated on the right side of the histogram.
        """
        assert(len(edges) >= 4)
        min_residual = np.min(residuals)

        # Keep left edge greater than negative infinity
        if min_residual < edges[1]:
            edges[0] = min_residual
        else:
            edges[0] = edges[1] - np.abs(edges[2] - edges[1])

        # Keep right edge less than infinity
        max_residual = np.max(residuals)
        if max_residual >= edges[-2]:
            edges[-1] = max_residual
        else:
            edges[-1] = edges[-2] + np.abs(edges[-2] - edges[-3])

    @staticmethod
    def aggregate(scores):
        """Fold several scores from a computed metric together.

        :param scores: a list of computed scores
        :return: the aggregated scores
        """
        if not Metric.check_aggregate_scores(scores):
            return Metric.get_error_metric()

        score_data = [score[Metric.DATA] for score in scores]
        edges = [d[ResidualsMetric.EDGES] for d in score_data]
        counts = [d[ResidualsMetric.COUNTS] for d in score_data]
        agg_edges = ResidualsMetric._aggregate_edges(edges)
        agg_counts = np.sum(counts, axis=0)

        data_agg = {
            ResidualsMetric.EDGES: agg_edges,
            ResidualsMetric.COUNTS: agg_counts
        }
        ret = ResidualsMetric._data_to_dict(data_agg)
        return Metric._make_json_safe(ret)

    @staticmethod
    def _aggregate_edges(all_edges):
        all_edges_arr = np.array(all_edges)
        ret = np.copy(all_edges_arr[0])
        ret[0] = np.min(all_edges_arr[:, 0])
        ret[-1] = np.max(all_edges_arr[:, -1])
        return ret.tolist()


class PredictedTrueMetric(RegressionMetric):
    """
    Predicted vs True Metric.

    This metric can be used to compare the distributions of true
    target values to the distribution of predicted values.

    The predictions are binned and standard deviations are calculated
    for error bars on a line chart.
    """

    SCHEMA_TYPE = constants.Metric.SCHEMA_TYPE_PREDICTIONS
    SCHEMA_VERSION = 'v1'

    EDGES = 'bin_edges'
    COUNTS = 'bin_counts'
    MEANS = 'bin_averages'
    STDEVS = 'bin_errors'

    @staticmethod
    def _data_to_dict(data):
        schema_type = PredictedTrueMetric.SCHEMA_TYPE
        schema_version = PredictedTrueMetric.SCHEMA_VERSION
        return Metric._data_to_dict(schema_type, schema_version, data)

    def compute(self, sample_weights=None, bin_info=None,
                y_min=None, y_max=None, y_std=None):
        """Compute metric.

        :param sample_weights: a list of sample weights for the data
        :param bin_info: metadata about the dataset needed to compute bins
            for some metrics
        :param y_min: minimum target value for the full dataset
        :param y_max: maximum target value for the full dataset
        :param y_std: standard deviation of target values
        :return: the metric
        """
        if bin_info is None:
            raise ValueError("bin_info is required to \
                             compute PredictedTrueMetric")

        n_bins = bin_info['number_of_bins']
        bin_starts = bin_info['bin_starts']
        bin_ends = bin_info['bin_ends']
        bin_edges = np.r_[bin_starts, bin_ends[-1]]
        # As long as we guarantee all points fit in the edges of bin_info
        # we can use np.digitize only on the ends.
        bin_indices = np.digitize(self._y, bin_ends, right=True)

        bin_counts = []
        bin_means = []
        bin_stdevs = []
        for bin_index in range(n_bins):
            y_pred_in_bin = self._y_pred[np.where(bin_indices == bin_index)]
            bin_count = y_pred_in_bin.shape[0]
            bin_counts.append(bin_count)
            if bin_count == 0:
                bin_means.append(0)
                bin_stdevs.append(0)
            else:
                bin_means.append(y_pred_in_bin.mean())
                bin_stdevs.append(y_pred_in_bin.std())

        self._data[PredictedTrueMetric.EDGES] = bin_edges
        self._data[PredictedTrueMetric.COUNTS] = np.array(bin_counts, dtype=int)
        self._data[PredictedTrueMetric.MEANS] = np.array(bin_means)
        self._data[PredictedTrueMetric.STDEVS] = np.array(bin_stdevs)

        ret = PredictedTrueMetric._data_to_dict(self._data)
        return Metric._make_json_safe(ret)

    @staticmethod
    def _total_variance(counts, means, variances):
        """
        Compute total population variance.

        Computes the variance of a population given the counts, means, and
        variances of several sub-populations.
        This uses the law of total variance:
        `https://en.wikipedia.org/wiki/Law_of_total_variance`
        var(y) = E[var(y|x)] + var(E[y|x])
            y: predicted value
            x: cross-validation index

        var(y|x) = variances
        E[y|x] = means
        E[var(y|x)] = np.sum(counts * variances) / total_count
        var(E[y|x]) = np.sum(counts * (means - total_mean) ** 2) / total_count
        """
        total_count = np.sum(counts)
        total_mean = np.sum(counts * means) / total_count
        unweighted_vars = variances + (means - total_mean) ** 2
        total_var = np.sum(counts * unweighted_vars) / total_count
        return total_var

    @staticmethod
    def aggregate(scores):
        """Fold several scores from a computed metric together.

        :param scores: a list of computed scores
        :return: the aggregated scores
        """
        if not Metric.check_aggregate_scores(scores):
            return Metric.get_error_metric()

        EDGES = PredictedTrueMetric.EDGES
        COUNTS = PredictedTrueMetric.COUNTS
        MEANS = PredictedTrueMetric.MEANS
        STDEVS = PredictedTrueMetric.STDEVS

        score_data = [score[Metric.DATA] for score in scores]

        n_bins = len(score_data[0][COUNTS])

        bin_counts = []
        bin_means = []
        bin_stdevs = []
        for bin_index in range(n_bins):
            split_counts = np.array([d[COUNTS][bin_index] for d in score_data])
            split_means = np.array([d[MEANS][bin_index] for d in score_data])
            split_stdevs = np.array([d[STDEVS][bin_index] for d in score_data])

            bin_count = np.sum(split_counts)
            bin_counts.append(bin_count)
            if bin_count == 0:
                bin_means.append(0)
                bin_stdevs.append(0)
            else:
                bin_mean = np.sum(split_counts * split_means) / bin_count
                bin_means.append(bin_mean)
                split_vars = split_stdevs ** 2
                bin_var = PredictedTrueMetric._total_variance(
                    split_counts, split_means, split_vars)
                bin_stdevs.append(bin_var ** 0.5)

        data_agg = {
            EDGES: score_data[0][EDGES],
            COUNTS: np.array(bin_counts, dtype=int),
            MEANS: np.array(bin_means),
            STDEVS: np.array(bin_stdevs)
        }

        ret = PredictedTrueMetric._data_to_dict(data_agg)
        return Metric._make_json_safe(ret)
