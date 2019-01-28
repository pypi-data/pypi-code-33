# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Global methods used during an automated machine learning iteration for both remote and local runs."""
import json
import logging
import sys
import traceback

import numpy as np
import pandas as pd
import scipy
import sklearn
from automl.client.core.common.datasets import ClientDatasets
from automl.client.core.common.model_wrappers import PipelineWithYTransformations
from automl.client.core.common.systemusage_telemetry import SystemResourceUsageTelemetryFactory
from automl.client.core.common.utilities import get_sdk_dependencies
from automl.client.core.common import logging_utilities as log_utils
from sklearn.pipeline import make_pipeline

from azureml.core import Experiment, Run
from azureml.telemetry import get_telemetry_log_handler
from azureml.telemetry.logging_handler import AppInsightsLoggingHandler
from azureml.train.automl._automl_pipeline import AutoMLPipeline
from azureml.train.automl._automl_run_context import AutoMLRunContext
from azureml.train.automl._pipeline_run_helper import _run_pipeline
from azureml.train.automl._preprocessorcontexts import (RawDataContext,
                                                        TransformedDataContext)
from azureml.train.automl._transform_data import _transform_data

from . import _constants_azureml, constants
from ._automl_settings import _AutoMLSettings
from ._logging import get_logger, _log_system_info, _blacklist_logging_keys, TELEMETRY_AUTOML_COMPONENT_KEY
from .ensemble import Ensemble
from .utilities import _validate_training_data, _sanitize_fit_output


def _get_problem_info(X, y, task_type, y_transformer=None):
    dataset = ClientDatasets()
    dataset.parse_data("parse", X, y, task_type,
                       init_all_stats=False, y_transformer=y_transformer)
    problem_info = dataset.get_problem_info()
    return problem_info


def set_problem_info(X, y, task_type, current_run=None, workspace=None,
                     experiment_name=None, run_id=None, preprocess=False,
                     lag_length=0, transformed_data_context=None,
                     enable_cache=True, subsampling=False,
                     timeseries=False, timeseries_param_dict=None, is_adb_run=False, **kwargs):
    """
    Set statistics about user data.

    :param X: The training features to use when fitting pipelines during AutoML experiment.
    :type X: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param y: Training labels to use when fitting pipelines during AutoML experiment.
    :type y: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param task_type: 'classification' or 'regression' depending on what kind of ML problem to solve.
    :type task_type: str or azureml.train.automl.constants.Tasks
    :param current_run: The AutoMLRun to set the info for.
    :type current_run: azureml.core.run.Run
    :param workspace: AzureML workspace containing this run.
    :type workspace: azureml.core.workspace.Workspace
    :param experiment_name: The experiemnt name.
    :type experiment_name: str
    :param run_id: ID of the run to set the info for.
    :type run_id: str
    :param preprocess: Flag whether to preprocess the data.
    :type preprocess: bool
    :param lag_length: How much to lag the features by for Lagging preprocessor.
    :type lag_length: int
    :param transformed_data_context: Containing X, y and other transformed data info.
    :type transformed_data_context: TransformedDataContext
    :param enable_cache: enable preprocessor cache
    :type enable_cache: Boolean
    :param subsampling: Flag to indicate whether this run should use subsampling.
    :type subsampling: bool
    :param timeseries: Flag whether to preprocess the data as timeseries.
    :type timeseries: bool
    :param timeseries_param_dict: Timeseries related parameters.
    :type timeseries_param_dict: dict
    :param is_adb_run: flag whether this is a azure databricks run or not.
    :type is_adb_run: bool
    :return: None
    """
    x_raw_column_names = None
    if isinstance(X, pd.DataFrame):
        x_raw_column_names = X.columns.values
    if run_id is None and current_run is not None:
        run_id = current_run._run_id
    if transformed_data_context is None:
        raw_data_context = RawDataContext(task_type=task_type,
                                          X=X,
                                          y=y,
                                          x_raw_column_names=x_raw_column_names,
                                          preprocess=preprocess,
                                          lag_length=lag_length,
                                          timeseries=timeseries,
                                          timeseries_param_dict=timeseries_param_dict,
                                          enable_cache=enable_cache)
        transformed_data_context = _transform_data(raw_data_context=raw_data_context,
                                                   logger=None, run_id=run_id)
    X = transformed_data_context.X

    problem_info_dict = {
        "dataset_num_categorical": 0,
        "dataset_classes": len(np.unique(y)),
        "dataset_features": X.shape[1],
        "dataset_samples": X.shape[0],
        "is_sparse": scipy.sparse.issparse(X),
        "subsampling": subsampling
    }

    problem_info_str = json.dumps(problem_info_dict)
    # This is required since token may expire
    if is_adb_run:
        current_run = Run.get_context(_batch_upload_metrics=False)

    if current_run is None:
        experiment = Experiment(workspace, experiment_name)
        current_run = Run(experiment, run_id)

    current_run.add_properties(
        {_constants_azureml.Properties.PROBLEM_INFO: problem_info_str})


def fit_pipeline(pipeline_script,
                 automl_settings,
                 run_id,
                 X=None,
                 y=None,
                 sample_weight=None,
                 X_valid=None,
                 y_valid=None,
                 sample_weight_valid=None,
                 cv_splits_indices=None,
                 train_frac=1,
                 fit_iteration_parameters_dict=None,
                 experiment=None,
                 pipeline_id=None,
                 score_min=None,
                 score_max=None,
                 remote=True,
                 is_adb_run=False,
                 logger=None,
                 child_run_metrics=None,
                 transformed_data_context=None,
                 elapsed_time=None,
                 **kwargs):
    """
    Run a single iteration of an automated machine learning experiment.

    This method is automatically called during a regular Automated Machine Learning
    experiment. fit_pipeline will evaluate the pipeline for this iteration, fit the pipeline with the provided data,
    calculate the various metrics relevant for this experiment, and log all the results in the specified Run's
    history.

    :param pipeline_script: serialized Pipeline returned from the server.
    :type pipeline_script: str
    :param automl_settings: User settings specified when creating AutoMLConfig.
    :type automl_settings: str or dict
    :param run_id: AzureML Child Run id for this fit.
    :type run_id: str
    :param X: Input training data.
    :type X: numpy.ndarray or pandas.DataFrame
    :param y: Input training labels.
    :type y: numpy.ndarray or pandas.DataFrame
    :param sample_weight: Sample weights for training data.
    :type sample_weight: numpy.ndarray or pandas.DataFrame
    :param X_valid: validation data.
    :type X_valid: numpy.ndarray or pandas.DataFrame
    :param y_valid: validation labels.
    :type y_valid: numpy.ndarray or pandas.DataFrame
    :param sample_weight_valid: validation set sample weights.
    :type sample_weight_valid: numpy.ndarray or pandas.DataFrame
    :param cv_splits_indices: Custom indices by which to split the data when running cross validation.
    :type cv_splits_indices: numpy.ndarray or pandas.DataFrame
    :param train_frac: Fraction of training data to use, (0,1].
    :type train_frac: float
    :param fit_iteration_parameters_dict: Remaining data specific parameters for fit such as 'x_raw_column_names'.
    :type fit_iteration_parameters_dict: dict
    :param experiment: The azureml.core experiment.
    :type experiment: azureml.core.experiment.Experiment
    :param pipeline_id: Hash Id of current pipeline being evaluated.
    :type pipeline_id: str
    :param score_min: current min score for the experiment if applicable.
    :type score_min: float or str
    :param score_max: current max score for the experiment if applicable.
    :type score_max: float or str
    :param remote: flag whether this is a remote run or local run.
    :type remote: bool
    :param is_adb_run: flag whether this is a azure databricks run or not.
    :type is_adb_run: bool
    :param logger: logger for info/error messages.
    :param child_run_metrics: child run metrics
    :type child_run_metrics: run context
    :param transformed_data_context: Containing X, y and other transformed data info.
    :type transformed_data_context: TransformedDataContext
    :param elapsed_time: How long this experiment has already taken in minutes
    :type elapsed_time: int
    :return: AzureML Run Properties for this child run
    :rtype: dict
    """
    """
    This bit of code is for backwards compatibility with remote runs. It should be removed after Vienna PR 175776
    has been merged and deployed.

    In all other cases, we already pass AutoMLSettings as an object instead of a string/dict and we use fit parameters
    or a transformed data context instead of passing the data directly.
    """

    automl_settings_obj = _AutoMLSettings.from_string_or_dict(automl_settings, experiment=experiment)
    if fit_iteration_parameters_dict is None and transformed_data_context is None:
        fit_iteration_parameters_dict = {
            'X': X,
            'y': y,
            'X_valid': X_valid,
            'y_valid': y_valid,
            'sample_weight': sample_weight,
            'sample_weight_valid': sample_weight_valid,
            'cv_splits_indices': cv_splits_indices,
            'x_raw_column_names': None
        }
    if child_run_metrics is None and remote:
        child_run_metrics = Run.get_context(_batch_upload_metrics=False)

    automl_pipeline = AutoMLPipeline(pipeline_script, pipeline_id, train_frac)
    automl_run_context = AutoMLRunContext(child_run_metrics, is_adb_run)

    return _fit_pipeline_internal(
        automl_pipeline,
        automl_settings_obj,
        automl_run_context,
        run_id,
        fit_iteration_parameters_dict,
        remote,
        logger,
        transformed_data_context,
        elapsed_time)


# TODO: Remove score_min and score_max from remote runs
def _fit_pipeline_internal(automl_pipeline,
                           automl_settings,
                           automl_run_context,
                           run_id,
                           fit_iteration_parameters_dict=None,
                           remote=True,
                           logger=None,
                           transformed_data_context=None,
                           elapsed_time=None):
    """
    Run a single iteration of an AutoML experiment.

    This method is automatically called during a regular AutoML
    experiment. fit_pipeline will evaluate the pipeline for this iteration, fit the pipeline with the provided data,
    calculate the various metrics relevant for this experiment, and log all the results in the specified AzureML Run's
    history.

    :param automl_pipeline: AutoMLPipeline object containing pipeline id and serialized script.
    :type automl_pipeline: AutoMLPipeline
    :param automl_settings: User settings specified when creating AutoMLConfig.
    :type automl_settings: _AutoMLSettings
    :param automl_run_context: child run context object
    :type automl_run_context: AutoMLRunContext
    :param run_id: AzureML Child Run id for this fit.
    :type run_id: str
    :param fit_iteration_parameters_dict: Remaining data specific parameters for fit such as 'x_raw_column_names'.
    :type fit_iteration_parameters_dict: dict
    :param remote: flag whether this is a remote run or local run.
    :type remote: bool
    :param logger: logger for info/error messages.
    :param transformed_data_context: Containing X, y and other transformed data info.
    :type transformed_data_context: TransformedDataContext
    :param elapsed_time: How long this experiment has already taken in minutes
    :type elapsed_time: int
    :return: AzureML Run Properties for this child run
    :rtype: dict
    """
    if logger is None:
        logger = get_logger()

    _log_system_info(logger, prefix_message="[RunId:{}]".format(run_id))

    telemetry_logger = SystemResourceUsageTelemetryFactory.get_system_usage_telemetry(
        logger, interval=10)

    # if transformed_data_context is not None, then use data in transformed_data_context. If None, then to
    # use data in fit_iteration_parameters_dict.
    if transformed_data_context is not None:
        X = transformed_data_context.X
        y = transformed_data_context.y
        X_valid = transformed_data_context.X_valid
        y_valid = transformed_data_context.y_valid
        sample_weight = transformed_data_context.sample_weight
        sample_weight_valid = transformed_data_context.sample_weight_valid
        cv_splits_indices = transformed_data_context.cv_splits_indices
        x_raw_column_names = transformed_data_context.x_raw_column_names
    elif fit_iteration_parameters_dict is not None:
        X = fit_iteration_parameters_dict.get('X')
        y = fit_iteration_parameters_dict.get('y')
        X_valid = fit_iteration_parameters_dict.get('X_valid')
        y_valid = fit_iteration_parameters_dict.get('y_valid')
        sample_weight = fit_iteration_parameters_dict.get('sample_weight')
        sample_weight_valid = fit_iteration_parameters_dict.get('sample_weight_valid')
        cv_splits_indices = fit_iteration_parameters_dict.get('cv_splits_indices')
        x_raw_column_names = fit_iteration_parameters_dict.get('x_raw_column_names')
    else:
        raise ValueError('Either a transformed data context or parameters dict is required.')

    _set_telemetry_collection(logger=logger, automl_settings=automl_settings)

    telemetry_logger.send_usage_telemetry_log(
        prefix_message="[RunId:{}][Starting fit_pipeline]".format(run_id),
        is_sending_telemetry=automl_settings.send_telemetry
    )

    # validate X and y
    _validate_training_data(X, y, X_valid, y_valid, sample_weight,
                            sample_weight_valid, cv_splits_indices, automl_settings)

    # logging X and y info
    logger.info(
        "[ParentRunId:{}] X datatype is {}, shape is {}, datasize is {}.".format(
            run_id, type(X), X.shape, sys.getsizeof(X)
        )
    )
    logger.info(
        "[ParentRunId:{}] y datatype is {}, shape is {}, datasize is {}.".format(
            run_id, type(y), y.shape, sys.getsizeof(y)
        )
    )
    if X_valid is not None:
        logger.info(
            "[ParentRunId:{}] X_valid datatype is {}, shape is {}, datasize is {}.".format(
                run_id, type(X_valid), X_valid.shape, sys.getsizeof(X_valid)
            )
        )
    if y_valid is not None:
        logger.info(
            "[ParentRunId:{}] y_valid datatype is {}, shape is {}, datasize is {}.".format(
                run_id, type(y_valid), y_valid.shape, sys.getsizeof(y_valid)
            )
        )

    logger.info("Using child run {0}".format(run_id))
    fit_output = {}
    errors = {}
    training_type = None
    dependencies = {
        'dependencies_versions': None
    }
    score_valid = constants.Defaults.INVALID_PIPELINE_VALIDATION_SCORES

    try:
        # TODO: Extract this out into standalone calculation
        iteration_timeout_min = automl_settings.iteration_timeout_minutes
        if iteration_timeout_min is not None:
            iteration_timeout_min = int(iteration_timeout_min)
        if automl_settings.experiment_timeout_minutes is not None and elapsed_time is not None:
            experiment_max_time_min = int(automl_settings.experiment_timeout_minutes) - elapsed_time
            if iteration_timeout_min is None or experiment_max_time_min < iteration_timeout_min:
                iteration_timeout_min = experiment_max_time_min

        if iteration_timeout_min and iteration_timeout_min <= 0:
            raise TimeoutError('Timeout reached, skipping iteration.')

        class_labels = None

        # ignore preprocess if x is sparse
        preprocess = automl_settings.preprocess and not scipy.sparse.issparse(X)

        telemetry_logger.send_usage_telemetry_log(
            prefix_message="[RunId:{}][Before preprocess]".format(run_id),
            is_sending_telemetry=automl_settings.send_telemetry
        )

        if transformed_data_context is None:
            raw_data_context = RawDataContext(task_type=automl_settings.task_type,
                                              X=X,
                                              y=y,
                                              X_valid=X_valid,
                                              y_valid=y_valid,
                                              sample_weight=sample_weight,
                                              sample_weight_valid=sample_weight_valid,
                                              x_raw_column_names=x_raw_column_names,
                                              preprocess=preprocess,
                                              lag_length=automl_settings.lag_length,
                                              cv_splits_indices=cv_splits_indices,
                                              automl_settings_obj=automl_settings,
                                              enable_cache=automl_settings.enable_cache)
            transformed_data_context = _transform_data(
                raw_data_context=raw_data_context, logger=logger, run_id=run_id)

        transformer = transformed_data_context.transformers.get('x_transformer')
        lag_transformer = transformed_data_context.transformers.get('lag_transformer')
        y_transformer = transformed_data_context.transformers.get('y_transformer')
        ts_transformer = transformed_data_context.transformers.get('ts_transformer')

        telemetry_logger.send_usage_telemetry_log(
            prefix_message="[RunId:{}][After preprocess]".format(run_id),
            is_sending_telemetry=automl_settings.send_telemetry
        )

        goal = _get_iteration_goal(automl_settings)

        if automl_settings.task_type == "classification":
            class_labels = np.unique(transformed_data_context.y)
            if y_transformer is not None:
                class_labels = y_transformer.inverse_transform(class_labels)

        telemetry_logger.send_usage_telemetry_log(
            prefix_message="[RunId:{}][Before executing pipeline]".format(run_id),
            is_sending_telemetry=automl_settings.send_telemetry
        )

        logger.info("Start executing pipeline {0}.".format(automl_pipeline.pipeline_script))
        logger.info("Running with the following AutoML settings:\n{}".format(
            automl_settings._format_selective(_blacklist_logging_keys)))

        try:
            score_valid, fit_time, fitted_pipeline, fitted_pipelines_train, pretrain_props = _run_pipeline(
                automl_settings, automl_pipeline, automl_run_context, iteration_timeout_min, transformed_data_context,
                logger, remote, y_transformer)
        except Exception as e:
            errors['fit'] = {'exception': e,
                             'traceback': traceback.format_exc()}
            log_utils.log_traceback(e, logger)
            fit_time = 0
            score_valid = constants.Defaults.INVALID_PIPELINE_VALIDATION_SCORES
            fitted_pipeline = constants.Defaults.INVALID_PIPELINE_FITTED
            fitted_pipelines_train = constants.Defaults.INVALID_PIPELINE_FITTED
            pretrain_props = {
                "run_template": "automl_child",
                "run_algorithm": None,
                "run_preprocessor": None
            }

        telemetry_logger.send_usage_telemetry_log(
            prefix_message="[RunId:{}][After executing pipeline]".format(
                run_id),
            is_sending_telemetry=automl_settings.send_telemetry
        )

        score = score_valid.get(automl_settings.primary_metric, constants.Defaults.DEFAULT_PIPELINE_SCORE)
        logger.info("Pipeline execution finished with a score of {0}".format(score))

        try:
            pipeline_step_str = str(fitted_pipeline.steps[1][1])
            run_properties = pipeline_step_str[pipeline_step_str.find("(") + 1:
                                               pipeline_step_str.find(")")]
        except Exception:
            run_properties = None

        fit_output = {
            "staticProperties": {},
            "score": score,
            "run_properties": run_properties,
            "pipeline_script": automl_pipeline.pipeline_script,
            "pipeline_id": automl_pipeline.pipeline_id,
            "training_type": training_type,
            "num_classes": automl_settings.num_classes,
            "framework": "sklearn",
            "fit_time": fit_time,
            "goal": goal,
            "class_labels": class_labels,
            "primary_metric": automl_settings.primary_metric,
            "errors": errors,
        }

        dependencies['dependencies_versions'] = json.dumps(get_sdk_dependencies())

        logger.info("Start logging metrics for child run.")

        with automl_run_context.get_run() as run:
            _log_metrics(run, score_valid, logger)
            _log_metrics_info(score_valid, logger)

            if (transformer is not None or lag_transformer is not None or ts_transformer is not None) and \
                    fitted_pipeline is not constants.Defaults.INVALID_PIPELINE_FITTED:
                fitted_pipeline = _add_transformer_x(
                    transformer, lag_transformer, ts_transformer, fitted_pipeline)
                if fitted_pipelines_train is not constants.Defaults.INVALID_PIPELINE_FITTED:
                    transformed_train_pipelines = []
                    for pipe in fitted_pipelines_train:
                        transformed_train_pipelines.append(
                            _add_transformer_x(transformer, lag_transformer, ts_transformer, pipe))
                    fitted_pipelines_train = transformed_train_pipelines

            if y_transformer is not None:
                # if y_transformer is not None, add a wrapper of the fitted model with transformer.
                if isinstance(fitted_pipeline, sklearn.pipeline.Pipeline) and \
                   fitted_pipeline is not constants.Defaults.INVALID_PIPELINE_FITTED:
                    fitted_pipeline = PipelineWithYTransformations(
                        fitted_pipeline, "LabelEncoder", y_transformer)
                if isinstance(fitted_pipelines_train, sklearn.pipeline.Pipeline) and \
                   fitted_pipelines_train is not constants.Defaults.INVALID_PIPELINE_FITTED:
                    fitted_pipeline = PipelineWithYTransformations(
                        transformed_train_pipelines, "LabelEncoder", y_transformer)

            fit_output['fitted_pipeline'] = fitted_pipeline
            fit_output['pipeline_python_obj'] = fitted_pipeline

            automl_run_context.save_model_output(fit_output['fitted_pipeline'], constants.MODEL_PATH)

            if automl_settings.enable_ensembling and \
                    fitted_pipelines_train != constants.Defaults.INVALID_PIPELINE_FITTED:
                # we need to persist the partially trained fitted models as well
                # they will be used for computing the scores during ensemble hill climbing
                automl_run_context.save_model_output(fitted_pipelines_train, constants.MODEL_PATH_TRAIN)

            # check to see if model_explainability set or not
            if automl_settings.model_explainability:
                telemetry_logger.send_usage_telemetry_log(
                    prefix_message="[RunId:{}][Start model explain in fit pipeline]".format(run_id),
                    is_sending_telemetry=automl_settings.send_telemetry
                )
                _explain_model_in_fit(run, fitted_pipeline,
                                      transformed_data_context, class_labels, logger)
                telemetry_logger.send_usage_telemetry_log(
                    prefix_message="[RunId:{}][End model explain in fit pipeline]".format(run_id),
                    is_sending_telemetry=automl_settings.send_telemetry
                )

            run.complete()
    except Exception as e:
        with automl_run_context.get_run() as run:
            errors['overall'] = {'exception': e,
                                 'traceback': traceback.format_exc()}
            log_utils.log_traceback(e, logger)
            run.fail()
    finally:
        fit_output['errors'] = errors
        fit_output['friendly_errors'] = json.dumps(_format_errors(errors))

        # TODO: remove once backend can handle nulls
        fit_output_str = _sanitize_fit_output(fit_output)

        with automl_run_context.get_run() as run:
            run.set_tags(fit_output_str)
            # TODO: move to tags once JOS is updated
            run.add_properties(fit_output_str)
            run.add_properties(dependencies)
        # TODO: move to tags once rest of SDK has been converted
        fit_output['pipeline_spec'] = automl_pipeline.pipeline_script
        fit_output[automl_settings.primary_metric] = score_valid.get(automl_settings.primary_metric,
                                                                     constants.Defaults.DEFAULT_PIPELINE_SCORE)
        fit_output.update(pretrain_props)

        telemetry_logger.send_usage_telemetry_log(
            prefix_message="[RunId:{}][End fit_pipeline]".format(run_id),
            is_sending_telemetry=automl_settings.send_telemetry
        )
        telemetry_logger.stop()
        return fit_output


def _explain_model_in_fit(child_run, pipeline, transformed_data_context, class_labels, logger):
    """
    Explain the model in the fit stage and store the explanation in child_run.

    :param child_run: the run to store information
    :type child_run: azureml.core.run.Run
    :param pipeline: the pipeline to explain
    :type pipeline: sklearn.pipeline
    :param transformed_data_context: Containing X, y and other transformed data info
    :type transformed_data_context: TransformedDataContext
    :param class_labels: a list of unique class labels
    :param class_labels: list
    :param logger: logger for info/error messages.
    :return: None
    """
    try:
        from azureml.explain.model._internal import TabularExplainer

        logger.info("[RunId:{}]Start model explanation in fit pipeline.".format(child_run.id))
        # Set the engineered/raw features information for model explanation
        columns = transformed_data_context._get_engineered_feature_names()

        # Convert columns from type ndarray to list
        if columns is not None and isinstance(columns, np.ndarray):
            columns = columns.tolist()

        # Pass the run object's ws, history and run id to construct TabularExplainer
        explainer = TabularExplainer(child_run.experiment.workspace,
                                     child_run.experiment.name, child_run.id)

        # To explain the pipeline which should exclude datatransformer and laggingtransformer
        pipeline = Ensemble._transform_single_fitted_pipeline(pipeline)

        # Explain the model and save the explanation information to artifact
        # And don't display explain status bar
        explainer.explain_model(
            pipeline, transformed_data_context.X, transformed_data_context.X_valid,
            columns, classes=class_labels, top_k=100, silent=True
        )

        child_run.tag(constants.MODEL_EXPLANATION_TAG, 'True')

        logger.info("[RunId:{}]End model explanation in fit pipeline.".format(child_run.id))
    except Exception as e:
        logger.warning(
            "[RunId:{}]Failed model explanation in fit pipeline. Error Message: {}.".format(child_run.id, e)
        )
        log_utils.log_traceback(e, logger)


def _add_transformer_x(transformer, lag_transformer, ts_transformer, pipeline_spec):
    """
    Add transformer as first step of the pipeline.

    :param pipeline_spec: pipeline to which the transformer should be added
    :param transformer: a pipeline compatible transformation that implements fit, transform and predict
    :return: pipeline with transformer prepended
    """
    transformers = filter(lambda x: x is not None, [
                          transformer, lag_transformer, ts_transformer])

    return make_pipeline(*transformers, *[s[1] for s in pipeline_spec.steps])


def _format_errors(errors):
    friendly_errors = {}
    for error in errors:
        friendly_errors[error] = str(errors[error]['exception'])
    return friendly_errors


def _log_metrics_info(scores, logger):
    reduced_scores = dict()
    for name, score in scores.items():
        if name in constants.Metric.SCALAR_FULL_SET or score is None:
            reduced_scores[name] = score
        else:
            reduced_scores[name] = type(score)
    log_msg = "The following metrics have been logged for the child run: {}."
    logger.info(log_msg.format(reduced_scores))


def _log_metrics(child_run, scores, logger):
    for name, score in scores.items():
        try:
            if name in constants.Metric.SCALAR_FULL_SET:
                child_run.log(name, score)
            elif name == constants.Metric.AccuracyTable:
                child_run.log_accuracy_table(name, score)
            elif name == constants.Metric.ConfusionMatrix:
                child_run.log_confusion_matrix(name, score)
            elif name == constants.Metric.Residuals:
                child_run.log_residuals(name, score)
            elif name == constants.Metric.PredictedTrue:
                child_run.log_predictions(name, score)
            else:
                logger.warning(
                    "Did not recognize metric: {}. Will not log.".format(name))
        except Exception as e:
            logger.warning(
                "Failed to log the metric {} with value {}, exception {}".format(name, score, e))


def _set_telemetry_collection(logger, automl_settings):
    """
    Set telemetry collection based on automl settings.

    :param logger: logger object
    :param automl_settings: automl settings
    :return: None
    """
    if not automl_settings.send_telemetry:
        return

    try:
        level = logging._checkLevel(automl_settings.telemetry_verbosity)

        if level is not logging.NOTSET:
            found_telemetry_handler = False

            for handler in logger.handlers:
                if isinstance(handler, AppInsightsLoggingHandler):
                    found_telemetry_handler = True
                    break

            if not found_telemetry_handler:
                logger.addHandler(get_telemetry_log_handler(component_name=TELEMETRY_AUTOML_COMPONENT_KEY))
    except Exception:
        pass  # do nothing


def _get_iteration_goal(automl_settings):
    if automl_settings.metric_operation == constants.OptimizerObjectives.MINIMIZE:
        return automl_settings.primary_metric + "_min"
    elif automl_settings.metric_operation == constants.OptimizerObjectives.MAXIMIZE:
        return automl_settings.primary_metric + "_max"
    elif automl_settings.metric_operation == constants.OptimizerObjectives.NA:
        return automl_settings.primary_metric + "_NA"
    raise NotImplementedError()
