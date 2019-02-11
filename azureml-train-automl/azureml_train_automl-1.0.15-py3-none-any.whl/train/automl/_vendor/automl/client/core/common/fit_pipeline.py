# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Code used to fit pipeline."""
from typing import Any, Dict, Optional
import json
import sys

import numpy as np
import scipy
import sklearn.pipeline

from . import constants, data_transformation, logging_utilities, pipeline_run_helper, training_utilities, utilities
from .automl_base_settings import AutoMLBaseSettings
from .automl_pipeline import AutoMLPipeline
from .automl_run_context import AutoMLAbstractRunContext
from .cache_store import FileCacheStore
from .fit_output import FitOutput
from .data_context import RawDataContext, TransformedDataContext
from .ensemble_base import EnsembleBase
from .systemusage_telemetry import SystemResourceUsageTelemetryFactory


def fit_pipeline(automl_pipeline: AutoMLPipeline,
                 automl_settings: AutoMLBaseSettings,
                 automl_run_context: AutoMLAbstractRunContext,
                 fit_iteration_parameters_dict: Optional[Dict[str, Any]] = None,
                 remote: bool = True,
                 logger: Optional[Any] = None,
                 transformed_data_context: Optional[TransformedDataContext] = None,
                 elapsed_time: Optional[int] = None) -> FitOutput:
    """
    Run a single iteration of an AutoML experiment.

    This method is automatically called during a regular AutoML
    experiment. fit_pipeline will evaluate the pipeline for this iteration, fit the pipeline with the provided data,
    calculate the various metrics relevant for this experiment, and log all the results in the specified AzureML Run's
    history.

    :param automl_pipeline: AutoMLPipeline object containing pipeline id and serialized script.
    :param automl_settings: User settings specified when creating AutoMLConfig.
    :param automl_run_context: child run context object
    :param fit_iteration_parameters_dict: Remaining data specific parameters for fit such as 'x_raw_column_names'.
    :param remote: flag whether this is a remote run or local run.
    :param logger: logger for info/error messages.
    :param transformed_data_context: Containing X, y and other transformed data info.
    :param elapsed_time: How long this experiment has already taken in minutes
    :return: AzureML Run Properties for this child run
    """
    logging_utilities.log_system_info(logger, prefix_message="[RunId:{}]".format(automl_pipeline.run_id))

    telemetry_logger = SystemResourceUsageTelemetryFactory.get_system_usage_telemetry(
        logger, interval=10)

    telemetry_logger.send_usage_telemetry_log(
        prefix_message="[RunId:{}][Starting fit_pipeline]".format(automl_pipeline.run_id),
        is_sending_telemetry=automl_settings.send_telemetry
    )

    X, y, X_valid, y_valid, sample_weight, sample_weight_valid, cv_splits_indices, x_raw_column_names = _extract_data(
        fit_iteration_parameters_dict, transformed_data_context
    )

    # validate X and y
    training_utilities.validate_training_data(X, y, X_valid, y_valid, sample_weight, sample_weight_valid,
                                              cv_splits_indices, automl_settings)

    # logging X and y info
    logger.info(
        "[ParentRunId:{}] X datatype is {}, shape is {}, datasize is {}.".format(
            automl_pipeline.run_id, type(X), X.shape, sys.getsizeof(X)
        )
    )
    logger.info(
        "[ParentRunId:{}] y datatype is {}, shape is {}, datasize is {}.".format(
            automl_pipeline.run_id, type(y), y.shape, sys.getsizeof(y)
        )
    )
    if X_valid is not None:
        logger.info(
            "[ParentRunId:{}] X_valid datatype is {}, shape is {}, datasize is {}.".format(
                automl_pipeline.run_id, type(X_valid), X_valid.shape, sys.getsizeof(X_valid)
            )
        )
    if y_valid is not None:
        logger.info(
            "[ParentRunId:{}] y_valid datatype is {}, shape is {}, datasize is {}.".format(
                automl_pipeline.run_id, type(y_valid), y_valid.shape, sys.getsizeof(y_valid)
            )
        )

    logger.info("Using child run {0}".format(automl_pipeline.run_id))
    fit_output = FitOutput(automl_settings, automl_pipeline)

    try:
        class_labels = None

        telemetry_logger.send_usage_telemetry_log(
            prefix_message="[RunId:{}][Before preprocess]".format(automl_pipeline.run_id),
            is_sending_telemetry=automl_settings.send_telemetry
        )

        if transformed_data_context is None:
            # ignore preprocess if x is sparse
            should_preprocess = automl_settings.preprocess and not scipy.sparse.issparse(X)
            raw_data_context = RawDataContext(task_type=automl_settings.task_type,
                                              X=X,
                                              y=y,
                                              X_valid=X_valid,
                                              y_valid=y_valid,
                                              sample_weight=sample_weight,
                                              sample_weight_valid=sample_weight_valid,
                                              x_raw_column_names=x_raw_column_names,
                                              preprocess=should_preprocess,
                                              lag_length=automl_settings.lag_length,
                                              cv_splits_indices=cv_splits_indices,
                                              automl_settings_obj=automl_settings)
            cache_store = None
            if automl_settings.enable_cache:
                cache_store = FileCacheStore()
            transformed_data_context = data_transformation.transform_data(
                raw_data_context=raw_data_context, logger=logger, cache_store=cache_store)

        telemetry_logger.send_usage_telemetry_log(
            prefix_message="[RunId:{}][After preprocess]".format(automl_pipeline.run_id),
            is_sending_telemetry=automl_settings.send_telemetry
        )

        if automl_settings.task_type == constants.Tasks.CLASSIFICATION:
            class_labels = np.unique(transformed_data_context.y)
            y_transformer = transformed_data_context.transformers.get('y_transformer')
            if y_transformer is not None:
                class_labels = y_transformer.inverse_transform(class_labels)

        telemetry_logger.send_usage_telemetry_log(
            prefix_message="[RunId:{}][Before executing pipeline]".format(automl_pipeline.run_id),
            is_sending_telemetry=automl_settings.send_telemetry
        )

        logger.info("Start executing pipeline {0}.".format(automl_pipeline.pipeline_script))
        logger.info("Running with the following AutoML settings:\n{}".format(
            automl_settings._format_selective(logging_utilities.BLACKLISTED_LOGGING_KEYS)))

        try:
            iteration_timeout_min = _check_iteration_time(automl_settings, elapsed_time)
            pipeline_run_output = pipeline_run_helper.run_pipeline(automl_settings, automl_pipeline,
                                                                   automl_run_context, iteration_timeout_min,
                                                                   transformed_data_context, logger, remote)
            fit_output.record_pipeline_results(pipeline_run_output)
        except Exception as e:
            fit_output.add_error('fit', e)
            logging_utilities.log_traceback(e, logger)

        telemetry_logger.send_usage_telemetry_log(
            prefix_message="[RunId:{}][After executing pipeline]".format(
                automl_pipeline.run_id),
            is_sending_telemetry=automl_settings.send_telemetry
        )

        logger.info("Pipeline execution finished with a score of {0}".format(fit_output.score))
        logger.info("Start logging metrics for child run.")

        with automl_run_context.get_run() as run:
            _log_metrics(run, fit_output.scores, logger)
            _log_metrics_info(fit_output.scores, logger)

            automl_run_context.save_model_output(fit_output.fitted_pipeline, constants.MODEL_PATH)

            if automl_settings.enable_ensembling and \
                    fit_output.fitted_pipelines_train != constants.Defaults.INVALID_PIPELINE_FITTED:
                # we need to persist the partially trained fitted models as well
                # they will be used for computing the scores during ensemble hill climbing
                automl_run_context.save_model_output(fit_output.fitted_pipelines_train, constants.MODEL_PATH_TRAIN)

            # check to see if model_explainability set or not
            if automl_settings.model_explainability:
                telemetry_logger.send_usage_telemetry_log(
                    prefix_message="[RunId:{}][Start model explain in fit pipeline]".format(automl_pipeline.run_id),
                    is_sending_telemetry=automl_settings.send_telemetry
                )
                _explain_model_in_fit(run, fit_output.fitted_pipeline, transformed_data_context, class_labels, logger)
                telemetry_logger.send_usage_telemetry_log(
                    prefix_message="[RunId:{}][End model explain in fit pipeline]".format(automl_pipeline.run_id),
                    is_sending_telemetry=automl_settings.send_telemetry
                )

            run.complete()
    except Exception as e:
        fit_output.add_error('overall', e)
        with automl_run_context.get_run() as run:
            logging_utilities.log_traceback(e, logger)
            run.fail()
    finally:
        # TODO: remove once backend can handle nulls
        fit_output_sanitized = fit_output.get_sanitized_output_dict()

        with automl_run_context.get_run() as run:
            run.set_tags(fit_output_sanitized)
            # TODO: move to tags once JOS is updated
            run.add_properties(fit_output_sanitized)
            run.add_properties({
                'dependencies_versions': json.dumps(utilities.get_sdk_dependencies())
            })

        telemetry_logger.send_usage_telemetry_log(
            prefix_message="[RunId:{}][End fit_pipeline]".format(automl_pipeline.run_id),
            is_sending_telemetry=automl_settings.send_telemetry
        )
        telemetry_logger.stop()
        return fit_output


def _extract_data(fit_iteration_parameters_dict=None, transformed_data_context=None):
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
    return X, y, X_valid, y_valid, sample_weight, sample_weight_valid, cv_splits_indices, x_raw_column_names


def _check_iteration_time(automl_settings, elapsed_time):
    iteration_timeout_min = automl_settings.iteration_timeout_minutes
    if iteration_timeout_min is not None:
        iteration_timeout_min = int(iteration_timeout_min)
    if automl_settings.experiment_timeout_minutes is not None and elapsed_time is not None:
        experiment_max_time_min = int(automl_settings.experiment_timeout_minutes) - elapsed_time
        if iteration_timeout_min is None or experiment_max_time_min < iteration_timeout_min:
            iteration_timeout_min = experiment_max_time_min

    if iteration_timeout_min and iteration_timeout_min <= 0:
        raise TimeoutError('Timeout reached, skipping iteration.')

    return iteration_timeout_min


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


def _explain_model_in_fit(child_run, pipeline, transformed_data_context, class_labels, logger):
    """
    Explain the model in the fit stage and store the explanation in child_run.

    :param child_run: the run to store information
    :type child_run: azureml.core.run.Run
    :param pipeline: the pipeline to explain
    :type pipeline: sklearn.pipeline.Pipeline
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
        pipeline = EnsembleBase._transform_single_fitted_pipeline(pipeline)

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
        logging_utilities.log_traceback(e, logger)
