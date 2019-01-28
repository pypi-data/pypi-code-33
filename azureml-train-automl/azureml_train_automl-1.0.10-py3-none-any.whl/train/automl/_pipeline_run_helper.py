# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Helper methods to execute an AutoML pipeline fit."""
from typing import Any, Dict, Optional, Tuple
import copy
import json
import os

from automl.client.core.common import pipeline_spec as pipeline_spec_module
from automl.client.core.common.metrics import get_default_metrics
from automl.client.core.common.limit_function_call_for_win import enforce_time_limit
from automl.client.core.common.resource_limits import default_resource_limits, safe_enforce_limits
from automl.client.core.common.datasets import ClientDatasets, SubsampleCacheStrategy
from automl.client.core.common.runner import ClientRunner
from automl.client.core.common.constants import ModelNameMappings

from . import constants
from ._automl_settings import _AutoMLSettings
from ._automl_pipeline import AutoMLPipeline
from ._automl_run_context import AutoMLRunContext
from ._logging import LogConfig
from ._preprocessorcontexts import TransformedDataContext
from .utilities import _sanitize_fit_output


SOURCE_WRAPPER_MODULE = 'automl.client.core.common.model_wrappers'


def _run_pipeline(automl_settings: _AutoMLSettings,
                  automl_pipeline: AutoMLPipeline,
                  automl_run_context: AutoMLRunContext,
                  iteration_timeout_min: Optional[int],
                  transformed_data_context: TransformedDataContext,
                  logger,
                  remote: bool,
                  y_transformer) -> Tuple[float, Dict[str, Any], object, object, Dict[str, Any]]:
    """
    Run a pipeline using the given settings and context.

    :param automl_settings: settings object to use for this job.
    :param automl_pipeline: the pipeline definition to use for this job.
    :param automl_run_context: the run context to use for this job.
    :param iteration_timeout_min: upper bound for how long this job can take. Passing None disables timeout.
    :param transformed_data_context: the data to use for this job.
    :param logger: the logger to use for this job.
    :param remote: whether we are running remotely or not.
    :param y_transformer: the y transformer to use for this job.
    :return: a tuple containing (fit time, scores, fitted model, partially fitted models)
    """
    enforce_time_on_win_required = False
    if iteration_timeout_min is not None and \
            not safe_enforce_limits.ok and \
            automl_settings.enforce_time_on_windows and \
            os.name == 'nt':
        enforce_time_on_win_required = True

    metrics = get_default_metrics(automl_settings.task_type)

    # for CV, we'll save the partially trained models on each split,
    # along with the model trained on full set

    dataset, pipeline_spec, training_type, problem_info = \
        _get_training_args(transformed_data_context.X,
                           transformed_data_context.y,
                           transformed_data_context.sample_weight,
                           transformed_data_context.X_valid,
                           transformed_data_context.y_valid,
                           transformed_data_context.sample_weight_valid,
                           transformed_data_context.cv_splits,
                           automl_settings.num_classes,
                           automl_settings.task_type,
                           automl_settings.y_min,
                           automl_settings.y_max,
                           automl_pipeline.pipeline_script,
                           automl_settings.max_cores_per_iteration,
                           logger=logger,
                           remote=remote,
                           y_transformer=y_transformer)

    pipeline = pipeline_spec.instantiate_pipeline_spec(problem_info)

    try:
        # for the Ensemble pipelines we will not have any preprocessors
        if len(pipeline.steps) == 1:
            run_preprocessor = None
            run_algorithm = pipeline.steps[0][0]
        else:
            run_preprocessor = pipeline.steps[0][0]
            run_algorithm = pipeline.steps[1][0]
    except Exception:
        run_preprocessor = None
        run_algorithm = None

    if run_algorithm:
        if automl_settings.task_type == constants.Tasks.CLASSIFICATION:
            run_algorithm = ModelNameMappings.ClassNameToCustomerFacingModelMapClassification.get(
                run_algorithm, run_algorithm)
        elif automl_settings.task_type == constants.Tasks.REGRESSION:
            run_algorithm = ModelNameMappings.ClassNameToCustomerFacingModelMapRegression.get(
                run_algorithm, run_algorithm)

    # TODO: Figure out a way to clean up this and other hanging bits of state
    pretrain_props = {
        "run_template": "automl_child",
        "run_algorithm": run_algorithm,
        "run_preprocessor": run_preprocessor
    }

    with automl_run_context.get_run() as run:
        run.add_properties(_sanitize_fit_output(pretrain_props))

    # min to sec conversion
    timeout = None
    if iteration_timeout_min:
        timeout = iteration_timeout_min * 60

    log_config = LogConfig(automl_settings.debug_log,
                           automl_settings.verbosity)

    if enforce_time_on_win_required:
        results, status = _train_pipeline_enforce_time_limit_on_windows(
            metrics=metrics,
            X=transformed_data_context.X,
            y=transformed_data_context.y,
            sample_weight=transformed_data_context.sample_weight,
            X_valid=transformed_data_context.X_valid,
            y_valid=transformed_data_context.y_valid,
            sample_weight_valid=transformed_data_context.sample_weight_valid,
            cv_splits=transformed_data_context.cv_splits,
            num_classes=automl_settings.num_classes,
            task_type=automl_settings.task_type,
            y_min=automl_settings.y_min,
            y_max=automl_settings.y_max,
            pipeline_spec=pipeline_spec,
            problem_info=problem_info,
            max_time_sec=timeout,
            is_ensemble_iteration=automl_pipeline.is_ensemble_pipeline,
            train_frac=automl_pipeline.training_size,
            subsample_seed=automl_settings.subsample_seed,
            remote=remote,
            y_transformer=y_transformer,
            log_config=log_config)

        runner = ClientRunner(dataset, metrics=metrics,
                              task=automl_settings.task_type,
                              log_config=log_config)
    else:
        # todo can move to helper, but not necessary
        runtime_constraints = default_resource_limits.copy()
        runtime_constraints['mem_in_mb'] = automl_settings.mem_in_mb
        runtime_constraints['wall_time_in_s'] = timeout
        problem_info.runtime_constraints = runtime_constraints

        runner = ClientRunner(dataset, metrics=metrics,
                              task=automl_settings.task_type)

        results, status = runner.run(dataset,
                                     pipeline_spec,
                                     problem_info,
                                     sets_to_run=[training_type],
                                     is_ensemble_iteration=automl_pipeline.is_ensemble_pipeline,
                                     subsample_percent=automl_pipeline.training_percent,
                                     subsample_seed=automl_settings.subsample_seed,
                                     enforce_limits=True,
                                     include_models=True)

    if isinstance(status, BaseException):
        raise RuntimeError from status
    if results is None:
        raise Exception("Failed to train pipeline.") from status

    # for cross validation train the model on full data set.
    if not automl_pipeline.is_ensemble_pipeline:
        results = _map_results(results, training_type)
        if results is not None and len(results) > 2:
            if training_type in \
                    [constants.TrainingType.CrossValidation, constants.TrainingType.MeanCrossValidation]:
                result_full, status = runner.run(
                    dataset, pipeline_spec, problem_info, sets_to_run=[
                        constants.TrainingType.TrainFull],
                    include_models=True)
                result_full = _map_results(
                    result_full, constants.TrainingType.TrainFull)
                if isinstance(status, BaseException):
                    raise RuntimeError from status

                if result_full is None or len(result_full) <= 2:
                    raise ValueError("Failed while training full result.")

                return results[0], results[1], result_full[2], results[2], pretrain_props

    score_valid, fit_time, fitted_pipeline = results
    fitted_pipelines_train = constants.Defaults.INVALID_PIPELINE_FITTED
    if isinstance(fitted_pipeline, list) and len(fitted_pipeline):
        fitted_pipeline = fitted_pipeline[0]

    return score_valid, fit_time, fitted_pipeline, fitted_pipelines_train, pretrain_props


def _train_pipeline_enforce_time_limit_on_windows(metrics,
                                                  X,
                                                  y,
                                                  sample_weight,
                                                  X_valid,
                                                  y_valid,
                                                  sample_weight_valid,
                                                  cv_splits,
                                                  num_classes,
                                                  task_type,
                                                  y_min,
                                                  y_max,
                                                  pipeline_spec,
                                                  problem_info,
                                                  max_time_sec,
                                                  is_ensemble_iteration,
                                                  train_frac=None,
                                                  subsample_seed=0,
                                                  remote=True,
                                                  y_transformer=None,
                                                  log_config=None):
    """
    Train the pipeline enforcing timeout.

    :param metrics:
    :param X:
    :param y:
    :param sample_weight:
    :param X_valid:
    :param y_valid:
    :param sample_weight_valid:
    :param cv_splits:
    :param num_classes:
    :param task_type:
    :param y_min:
    :param y_max:
    :param pipeline_spec:
    :param problem_info:
    :param max_time_sec:
    :param is_ensemble_iteration:
    :param train_frac:
    :param subsample_seed:
    :param remote:
    :param y_transformer:
    :param log_config:
    :return:
    """
    args = {
        "metrics": metrics,
        "X": X,
        "y": y,
        "sample_weight": sample_weight,
        "X_valid": X_valid,
        "y_valid": y_valid,
        "sample_weight_valid": sample_weight_valid,
        "cv_splits": cv_splits,
        "num_classes": num_classes,
        "task_type": task_type,
        "y_min": y_min,
        "y_max": y_max,
        "pipeline_spec": pipeline_spec,
        "problem_info": problem_info,
        "is_ensemble_iteration": is_ensemble_iteration,
        "train_frac": train_frac,
        "subsample_seed": subsample_seed,
        "remote": remote,
        "y_transformer": y_transformer,
        "log_config": log_config
    }
    return enforce_time_limit(max_time_sec, _train_pipeline_on_win_spawn_process, args)


def _get_dataset(X,
                 y,
                 sample_weight=None,
                 X_valid=None,
                 y_valid=None,
                 sample_weight_valid=None,
                 cv_splits=None,
                 num_classes=None,
                 task_type="classification",
                 y_min=None,
                 y_max=None,
                 init_all_stats=False,
                 remote=True,
                 y_transformer=None):
    """
    Get the ClientDataset.

    :param X:
    :param y:
    :param sample_weight:
    :param X_valid:
    :param y_valid:
    :param sample_weight_valid:
    :param cv_splits:
    :param num_classes:
    :return:
    """
    assert_failures = []

    if cv_splits:
        frac_valid = cv_splits.get_fraction_validation_size()
        cv_splits_indices = cv_splits.get_custom_split_indices()
        num_cv_folds = cv_splits.get_num_k_folds()
    else:
        frac_valid = None
        cv_splits_indices = None
        num_cv_folds = None

    subsample_cache_strategy = SubsampleCacheStrategy.Classic if remote \
        else SubsampleCacheStrategy.Preshuffle

    dataset = ClientDatasets(subsample_cache_strategy=subsample_cache_strategy)

    if X_valid is not None:
        training_type = _get_training_type(
            constants.TrainingType.TrainAndValidation)

        if not (num_cv_folds == 0 or num_cv_folds is None):
            assert_failures.append(
                'n_cross_validations cannot be specified when X_valid is provided.')

        if not (frac_valid == 0.0 or frac_valid is None):
            assert_failures.append(
                'validation_size cannot be specified when X_valid is provided.')

        if y_valid is None:
            assert_failures.append(
                'y_valid must also be provided when X_valid is provided.')

        if len(assert_failures) > 0:
            raise AssertionError("Bad fit parameters. Please review documentation for fit. " +
                                 ' '.join(assert_failures))
        dataset.parse_simple_train_validate(name="NoName",
                                            X=X,
                                            y=y,
                                            sample_weight=sample_weight,
                                            X_valid=X_valid,
                                            y_valid=y_valid,
                                            sample_weight_valid=sample_weight_valid,
                                            task=task_type,
                                            y_min=y_min,
                                            y_max=y_max,
                                            init_all_stats=init_all_stats,
                                            y_transformer=y_transformer)

    else:
        if(num_cv_folds == 0 or num_cv_folds is None) and cv_splits_indices is None:
            training_type = _get_training_type(
                constants.TrainingType.TrainAndValidation)
        else:
            if cv_splits_indices is not None:
                num_cv_folds = len(cv_splits_indices)
            training_type = _get_training_type(
                constants.TrainingType.MeanCrossValidation, num_cv_folds)

        if len(assert_failures) > 0:
            raise AssertionError("Bad fit parameters. Please review documentation for fit. " +
                                 ' '.join(assert_failures))

        dataset.parse_data(name="NoName",
                           X=X,
                           y=y,
                           sample_weight=sample_weight,
                           cv_splits=cv_splits,
                           num_classes=num_classes,
                           task=task_type,
                           y_min=y_min,
                           y_max=y_max,
                           init_all_stats=init_all_stats,
                           y_transformer=y_transformer)
    return dataset, training_type


def _get_pipeline(pipeline_script, problem_info, logger=None):
    """
    Get the Pipeline object.

    :param pipeline_script: returned from service that is a dictionary of pipeline
    : spec
    : or for backward compatibility a dictionary of normal and sparse pipeline
    : definition that can be eval'd
    :param problem_info: The metadata on the dataset.
    :return: a tuple of ProblemInfo object and a PipelineSpec object.
    """
    pipeline_dict = json.loads(pipeline_script)

    # Wrap the standard scaler.
    scaler = [o for o in pipeline_dict["objects"]
              if o['spec_class'] == pipeline_spec_module.PREPROC_NAME and o['class_name'] == 'StandardScaler']
    if len(scaler) == 1:
        scaler[0]['class_name'] = 'StandardScalerWrapper'
        scaler[0]['module'] = SOURCE_WRAPPER_MODULE

    # If there are any single threaded pipelines, force the number of threads to 1.
    pinfo = problem_info
    if problem_info.num_threads != 1:
        stmodel = [o for o in pipeline_dict["objects"]
                   if o['spec_class'] == pipeline_spec_module.SKLEARN_NAME and
                   'KNeighbors' in o['class_name']]
        if len(stmodel) == 1:
            pinfo = copy.deepcopy(problem_info)
            pinfo.num_threads = 1
            if logger:
                logger.warning("resetting the number of threads to 1\
                               for pipeline with {0}".
                               format(stmodel[0]['class_name']))
    spec = pipeline_spec_module.PipelineSpec.from_dict(pipeline_dict)
    return pinfo, spec


def _train_pipeline_on_win_spawn_process(metrics,
                                         X,
                                         y,
                                         sample_weight,
                                         X_valid,
                                         y_valid,
                                         sample_weight_valid,
                                         cv_splits,
                                         num_classes,
                                         task_type,
                                         y_min,
                                         y_max,
                                         pipeline_spec,
                                         problem_info,
                                         is_ensemble_iteration=False,
                                         train_frac=1,
                                         subsample_seed=0,
                                         remote=True,
                                         y_transformer=None,
                                         log_config=None):
    """
    Train the pipeline on a spawned process.

    :param metrics:
    :param X:
    :param y:
    :param sample_weight:
    :param X_valid:
    :param y_valid:
    :param sample_weight_valid:
    :param cv_splits:
    :param num_classes:
    :param task_type:
    :param y_min:
    :param y_max:
    :param pipeline_spec:
    :param is_ensemble_iteration:
    :param train_frac:
    :param subsample_seed:
    :param remote:
    :param y_transformer:
    :param log_config:
    :return:
    """
    from . import constants  # noqa: F401,F811
    from automl.client.core.common.datasets import ClientDatasets  # noqa: F401,F811
    from automl.client.core.common.model_wrappers import (
        LightGBMClassifier, SparseNormalizer, TruncatedSVDWrapper,
        CalibratedModel, LightGBMRegressor, LinearSVMWrapper,
        NBWrapper, NuSVCWrapper, SGDClassifierWrapper, SVCWrapper)  # noqa: F401,F811
    from automl.client.core.common.exceptions import DataException, ServiceException  # noqa: F401,F811
    from automl.client.core.common.metrics import minimize_or_maximize  # noqa: F401,F811
    from automl.client.core.common.preprocess import DataTransformer, LaggingTransformer  # noqa: F401,F811
    from automl.client.core.common.runner import ClientRunner   # noqa: F401,F811
    import logging  # noqa: F401,F811
    import numpy as np  # noqa: F401,F811
    import pandas as pd  # noqa: F401,F811
    import pickle  # noqa: F401,F811
    import os  # noqa: F401,F811
    import os.path  # noqa: F401,F811
    import scipy  # noqa: F401,F811
    import sys  # noqa: F401,F811
    import tempfile  # noqa: F401,F811
    import traceback  # noqa: F401,F811
    import sklearn  # noqa: F401,F811
    from sklearn import pipeline, preprocessing, linear_model, decomposition, ensemble  # noqa: F401,F811
    from sklearn.metrics import recall_score, precision_score  # noqa: F401,F811
    from sklearn.model_selection import cross_val_score  # noqa: F401,F811
    from sklearn.pipeline import make_pipeline  # noqa: F401,F811
    from azureml.core.run import Run  # noqa: F401,F811

    try:
        dataset, _, training_type, _ = \
            _get_training_args(X,
                               y,
                               sample_weight,
                               X_valid,
                               y_valid,
                               sample_weight_valid,
                               cv_splits,
                               num_classes,
                               task_type,
                               y_min,
                               y_max,
                               remote=remote,
                               y_transformer=y_transformer)
        runner = ClientRunner(dataset, metrics=metrics,
                              task=task_type)

        return runner.run(dataset,
                          pipeline_spec,
                          problem_info,
                          sets_to_run=[training_type],
                          is_ensemble_iteration=is_ensemble_iteration,
                          subsample_percent=train_frac * 100,
                          subsample_seed=subsample_seed,
                          include_models=True)
    except Exception as e:
        return None, e


def _get_training_args(X,
                       y,
                       sample_weight,
                       X_valid,
                       y_valid,
                       sample_weight_valid,
                       cv_splits,
                       num_classes,
                       task_type,
                       y_min,
                       y_max,
                       pipeline_script=None,
                       max_cores_per_iteration=None,
                       logger=None,
                       remote=True,
                       y_transformer=None):

    dataset, training_type = _get_dataset(X=X,
                                          y=y,
                                          sample_weight=sample_weight,
                                          X_valid=X_valid,
                                          y_valid=y_valid,
                                          sample_weight_valid=sample_weight_valid,
                                          cv_splits=cv_splits,
                                          num_classes=num_classes,
                                          task_type=task_type,
                                          y_min=y_min,
                                          y_max=y_max,
                                          init_all_stats=False,
                                          remote=remote,
                                          y_transformer=y_transformer)
    problem_info = dataset.get_problem_info()
    problem_info.num_threads = max_cores_per_iteration
    pipeline_spec = None
    if pipeline_script:
        problem_info, pipeline_spec = _get_pipeline(pipeline_script, problem_info, logger)
    return dataset, pipeline_spec, training_type, problem_info


def _map_results(results, training_type):
    training_types = constants.TrainingType
    result_types = constants.TrainingResultsType

    if training_type in [training_types.TrainAndValidation, training_types.TrainValidateTest]:
        status = results[result_types.TRAIN_VALIDATE_STATUS]
        if status:
            raise Exception(status)
        scores = results[result_types.VALIDATION_METRICS]
        train_time = results[result_types.VALIDATION_METRICS][result_types.TRAIN_TIME]
        model = results[result_types.MODELS][training_type]
    elif training_type == training_types.TrainFull:
        status = results[result_types.TRAIN_FULL_STATUS]
        if status:
            raise Exception(status)
        scores = results[result_types.TRAIN_FROM_FULL_METRICS]
        train_time = results[result_types.TRAIN_FROM_FULL_METRICS][result_types.TRAIN_TIME]
        model = results[result_types.MODELS][training_type]
    elif training_type == training_types.CrossValidation:
        status = results[result_types.CV_STATUS]
        if status:
            raise Exception(status)
        scores = results[result_types.CV_METRICS]
        train_time = [x[result_types.TRAIN_TIME]
                      for x in results[result_types.CV_METRICS]]
        model = results[result_types.MODELS][training_type]
    elif training_type == training_types.MeanCrossValidation:
        status = results[result_types.CV_STATUS]
        if status:
            raise Exception(status)
        scores = results[result_types.CV_MEAN_METRICS]
        train_time = results[result_types.CV_MEAN_METRICS][result_types.TRAIN_TIME]
        model = results[result_types.MODELS][training_types.CrossValidation]
    else:
        raise ValueError('Invalid training type {} specified.'.format(training_type))

    return scores, train_time, model


def _get_training_type(training_type, folds=0):
    """
    Determine what type of training and validation to do based on user inputs.

    :param training_type: str representing what type fo training and validation to do
    :param folds: int number of
    :return: None
    """
    valid_training_types = (constants.TrainingType.TrainAndValidation,
                            constants.TrainingType.MeanCrossValidation)
    if training_type not in valid_training_types:
        raise AssertionError(
            "%s and %s are the only supported training types." % valid_training_types)
    is_cv = training_type == constants.TrainingType.MeanCrossValidation
    if not ((is_cv and folds) or (not is_cv and not folds)):
        raise AssertionError("Cannot specify number of folds "
                             "if training type is not %s" % constants.TrainingType.MeanCrossValidation)
    if folds < 0 or folds == 1:
        raise AssertionError(
            "Cross validation folds must be greater than 1, got %d" % folds)
    return training_type
