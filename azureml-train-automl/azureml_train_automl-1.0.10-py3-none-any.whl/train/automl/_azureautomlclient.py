# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""AutoML object in charge of orchestrating various AutoML runs for predicting models."""
import json
import math
import os
import os.path
import re
import sys
import warnings
from datetime import datetime
from importlib.util import module_from_spec, spec_from_file_location
from threading import Timer

from msrest.exceptions import HttpOperationError
import numpy as np
import pandas as pd
import pytz
import sklearn

from azureml._restclient.service_context import ServiceContext
from azureml._restclient import JasmineClient, ExperimentClient
from azureml._restclient.models.create_parent_run_dto import CreateParentRunDto
from azureml.core import Run
from azureml.core.runconfig import RunConfiguration
from azureml.telemetry import get_diagnostics_collection_info, is_diagnostics_collection_info_available
from azureml.train.automl._preprocessorcontexts import RawDataContext
from azureml.train.automl._transform_data import _transform_data

from automl.client.core.common import pipeline_spec, logging_utilities, model_wrappers, utilities as common_utilities
from automl.client.core.common.console_interface import ConsoleInterface
from automl.client.core.common.systemusage_telemetry import SystemResourceUsageTelemetryFactory
from automl.client.core.common.exceptions import (DataException,
                                                  ServiceException)

from . import _dataprep_utilities, automl, constants
from ._adb_driver_node import _AdbDriverNode
from ._adb_run_experiment import adb_run_experiment
from ._automl_settings import _AutoMLSettings
from ._remote_console_interface import RemoteConsoleInterface
from ._logging import get_logger, _blacklist_logging_keys, TELEMETRY_AUTOML_COMPONENT_KEY
from .run import AutoMLRun
from .utilities import (_auto_blacklist, _format_training_data, _log_user_sdk_dependencies,
                        _set_task_parameters, _validate_training_data_dict,
                        _validate_data_splits, friendly_http_exception)


class AzureAutoMLClient(object):
    """Client to run AutoML experiments on Azure Machine Learning platform."""

    # Caches for querying and printing child runs
    run_map = {}
    metric_map = {}
    properties_map = {}

    def __init__(self,
                 experiment,
                 **kwargs):
        """
        Construct the AzureMLClient class.

        :param experiment: The azureml.core experiment
        :param kwargs: dictionary of keyword args
        :keyword something: something
        :keyword iterations: Number of different pipelines to test
        :keyword data_script: File path to the script containing get_data()
        :keyword primary_metric: The metric that you want to optimize.
        :keyword task_type: Field describing whether this will be a classification or regression experiment
        :keyword compute_target: The AzureML compute to run the AutoML experiment on
        :keyword validation_size: What percent of the data to hold out for validation
        :keyword n_cross_validations: How many cross validations to perform
        :keyword y_min: Minimum value of y for a regression experiment
        :keyword y_max: Maximum value of y for a regression experiment
        :keyword num_classes: Number of classes in the label data
        :keyword preprocess: Flag whether AutoML should preprocess your data for you
        :keyword lag_length: How many rows to lag data when preprocessing time series data
        :keyword max_cores_per_iteration: Maximum number of threads to use for a given iteration
        :keyword iteration_timeout_minutes: Maximum time in minutes that each iteration before it terminates
        :keyword mem_in_mb: Maximum memory usage of each iteration before it terminates
        :keyword enforce_time_on_windows: flag to enforce time limit on model training at each iteration under windows.
        :keyword experiment_timeout_minutes: Maximum amount of time that all iterations combined can take.
        :keyword experiment_exit_score:
            Target score for experiment. Experiment will terminate after this score is reached.
        :keyword blacklist_algos: List of algorithms to ignore for AutoML experiment
        :keyword exclude_nan_labels: Flag whether to exclude rows with NaN values in the label
        :keyword auto_blacklist: Flag whether AutoML should try to exclude algorithms
            that it thinks won't perform well.
        :keyword verbosity: Verbosity level for AutoML log file
        :keyword enable_tf: Flag to enable/disable Tensorflow  algorithms
        :keyword enable_subsampling: Flag to enable/disable subsampling. Note that even if it's true,
            subsampling would not be enabled for small datasets or iterations.
        :keyword subsample_seed: random_state used to sample the data.
        :keyword debug_log: File path to AutoML logs
        """
        if experiment is None:
            raise TypeError('AzureML experiment must be passed for AutoML.')

        self.automl_settings = _AutoMLSettings(experiment=experiment, **kwargs)

        self.experiment = experiment

        self._status = constants.Status.NotStarted
        self._loop = None
        self._score_max = None
        self._score_min = None
        self._score_best = None
        self._console_logger = open(os.devnull, "w")

        self.parent_run_id = None
        self.current_iter = None
        self.pipelines = None
        self.input_data = None
        self._adb_thread = None

        self._check_create_folders(self.automl_settings.path)

        telemetry_set_by_user = True
        # turn on default telemetry collection, if user is not set
        if not is_diagnostics_collection_info_available():
            telemetry_set_by_user = False

        self.logger = get_logger(self.automl_settings.debug_log, self.automl_settings.verbosity)

        if not telemetry_set_by_user:
            self.logger.info("Telemetry collection is not set, turning it on by default.")

        send_telemetry, level = get_diagnostics_collection_info(component_name=TELEMETRY_AUTOML_COMPONENT_KEY)
        self.automl_settings.telemetry_verbosity = level
        self.automl_settings.send_telemetry = send_telemetry
        self._usage_telemetry = SystemResourceUsageTelemetryFactory.get_system_usage_telemetry(
            self.logger)
        self._usage_telemetry.start()

        self.experiment_start_time = None

        if not self.automl_settings.show_warnings:
            # sklearn forces warnings, so we disable them here
            warnings.simplefilter('ignore', DeprecationWarning)
            warnings.simplefilter('ignore', RuntimeWarning)
            warnings.simplefilter('ignore', UserWarning)
            warnings.simplefilter('ignore', FutureWarning)
            warnings.simplefilter('ignore', sklearn.exceptions.UndefinedMetricWarning)

        module_path = self.automl_settings.data_script
        if self.automl_settings.data_script is not None:
            if not os.path.exists(self.automl_settings.data_script) and self.automl_settings.path is not None:
                script_path = os.path.join(
                    self.automl_settings.path, self.automl_settings.data_script)
                if os.path.exists(script_path):
                    module_path = script_path
                else:
                    raise DataException("Could not find data script with name '{0}' or '{1}'"
                                        .format(self.automl_settings.data_script, script_path))
            try:
                #  Load user script to get access to GetData function
                spec = spec_from_file_location('get_data', module_path)
                self.user_script = module_from_spec(spec)
                spec.loader.exec_module(self.user_script)
                if not hasattr(self.user_script, 'get_data'):
                    raise DataException(
                        "User script does not contain get_data() function.")
                try:
                    self.input_data = common_utilities.extract_user_data(
                        self.user_script)
                    _auto_blacklist(self.input_data, self.automl_settings)
                    if self.automl_settings.exclude_nan_labels:
                        self.input_data = common_utilities._y_nan_check(self.input_data)
                except Exception:
                    pass
            except Exception as e:
                # disabled traceback for compliance, enable it back once we have proper exception handling
                # logging_utilities.log_traceback(e, self.logger)
                raise DataException(
                    "Could not import get_data() function from {0}".format(self.automl_settings.data_script)) from None
        else:
            self.user_script = None

        # Set up clients to communicate with AML services
        self._jasmine_client = JasmineClient.create(self.experiment.workspace, experiment.name,
                                                    host=self.automl_settings.service_url)
        self.experiment_client = ExperimentClient.create(self.experiment.workspace, experiment.name,
                                                         host=self.automl_settings.service_url)

        self._validation_scores = []
        self.current_run = None

    def __del__(self):
        """Clean up AutoML loggers and close files."""
        try:
            logging_utilities.cleanup_log_map(self.automl_settings.debug_log,
                                              self.automl_settings.verbosity)

            if self._usage_telemetry is not None:
                self._usage_telemetry.stop()
        except Exception:
            # last chance, nothing can be done, so ignore any exception
            pass

    def cancel(self):
        """
        Cancel the ongoing local run.

        :return: None
        """
        self._status = constants.Status.Terminated

    def fit(self,
            run_configuration=None,
            compute_target=None,
            X=None,
            y=None,
            sample_weight=None,
            X_valid=None,
            y_valid=None,
            sample_weight_valid=None,
            data=None,
            label=None,
            columns=None,
            cv_splits_indices=None,
            show_output=False,
            existing_run=False):
        """
        Start a new AutoML execution on the specified compute target.

        :param run_configuration: The run confiuguration used by AutoML, should contain a compute target for remote
        :type run_configuration: Azureml.core RunConfiguration
        :param compute_target: The AzureML compute node to run this experiment on
        :type compute_target: azureml.core.compute.AbstractComputeTarget
        :param X: Training features
        :type X: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param y: Training labels
        :type y: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param sample_weight:
        :type sample_weight: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param X_valid: validation features
        :type X_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param y_valid: validation labels
        :type y_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param sample_weight_valid: validation set sample weights
        :type sample_weight_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param data: Training features and label
        :type data: pandas.DataFrame
        :param label: Label column in data
        :type label: str
        :param columns: whitelist of columns in data to use as features
        :type columns: list(str)
        :param cv_splits_indices: Indices where to split training data for cross validation
        :type cv_splits_indices: list(int), or list(Dataflow) in which each Dataflow represent a train-valid set
                                 where 1 indicates record for training and 0 indicates record for validation
        :param show_output: Flag whether to print output to console
        :type show_output: bool
        :param existing_run: Flag whether this is a continuation of a previously completed experiment
        :type existing_run: bool
        :return: AutoML parent run
        :rtype: azureml.train.automl.AutoMLRun
        """
        self._status = constants.Status.Started

        if show_output:
            self._console_logger = sys.stdout

        if run_configuration is None:
            run_configuration = RunConfiguration()
            if compute_target is not None:
                run_configuration.name = compute_target.name
                self._console_logger.write('No run_configuration provided, running on {0} with default configuration\n'
                                           .format(compute_target.name))
            else:
                self._console_logger.write(
                    'No run_configuration provided, running locally with default configuration\n')

        self.automl_settings.compute_target = run_configuration.target

        if self.automl_settings.spark_context:
            self._init_adb_driver_run(run_configuration=run_configuration, X=X, y=y, sample_weight=sample_weight,
                                      X_valid=X_valid, y_valid=y_valid, sample_weight_valid=sample_weight_valid,
                                      cv_splits_indices=cv_splits_indices, show_output=show_output)
        elif run_configuration.target == 'local':
            if self.automl_settings.path is None:
                self.automl_settings.path = '.'
            name = run_configuration._name if run_configuration._name else "local"
            run_configuration.save(self.automl_settings.path, name)
            self._console_logger.write('Running on local machine\n')
            self._fit_local(X=X, y=y, sample_weight=sample_weight, X_valid=X_valid, y_valid=y_valid,
                            data=data, label=label, columns=columns, cv_splits_indices=cv_splits_indices,
                            existing_run=existing_run, sample_weight_valid=sample_weight_valid)
        else:
            self._console_logger.write('Running on remote compute: ' + str(run_configuration.target) + '\n')
            self._fit_remote(run_configuration, X=X, y=y, sample_weight=sample_weight,
                             X_valid=X_valid, y_valid=y_valid, sample_weight_valid=sample_weight_valid,
                             cv_splits_indices=cv_splits_indices, show_output=show_output)
        return self.current_run

    def _init_adb_driver_run(self,
                             run_configuration=None,
                             X=None,
                             y=None,
                             sample_weight=None,
                             X_valid=None,
                             y_valid=None,
                             sample_weight_valid=None,
                             cv_splits_indices=None,
                             show_output=False,
                             existing_run=False):

        self._console_logger.write(
            'Running on ADB cluster experiment {0}.\n'.format(self.automl_settings.name))

        try:
            if not existing_run:
                self._fit_remote_core(run_configuration, X=X, y=y, sample_weight=sample_weight, X_valid=X_valid,
                                      y_valid=y_valid, sample_weight_valid=sample_weight_valid,
                                      cv_splits_indices=cv_splits_indices)
            # This should be refactored to have RunHistoryClient and make call on it to get token
            token_res = self.experiment_client._client.run.\
                get_token(experiment_name=self.automl_settings.name,
                          resource_group_name=self.automl_settings.resource_group,
                          subscription_id=self.automl_settings.subscription_id,
                          workspace_name=self.automl_settings.workspace_name,
                          run_id=self.current_run.run_id)
            aml_token = token_res.token
            aml_token_expiry = token_res.expiry_time_utc

            service_context = ServiceContext(
                subscription_id=self.automl_settings.subscription_id,
                resource_group_name=self.automl_settings.resource_group,
                workspace_name=self.automl_settings.workspace_name,
                workspace_id=self.experiment.workspace._workspace_id,
                authentication=self.experiment.workspace._auth_object)

            run_history_url = service_context._get_run_history_url()
            fn_script = None
            if self.automl_settings.data_script:
                with open(self.automl_settings.data_script, "r") as f:
                    fn_script = f.read()

            datapre_json = _dataprep_utilities.get_dataprep_json(X=X, y=y,
                                                                 sample_weight=sample_weight,
                                                                 X_valid=X_valid,
                                                                 y_valid=y_valid,
                                                                 sample_weight_valid=sample_weight_valid)
            # build dictionary of context
            run_context = {"subscription_id": self.automl_settings.subscription_id,
                           "resource_group": self.automl_settings.resource_group,
                           "location": self.experiment.workspace.location,
                           "workspace_name": self.automl_settings.workspace_name,
                           "experiment_name": self.automl_settings.name,
                           "parent_run_id": self.current_run.run_id,
                           "aml_token": aml_token,
                           "aml_token_expiry": aml_token_expiry,
                           "service_url": run_history_url,
                           "automl_settings_str": json.dumps(self.automl_settings._as_serializable_dict()),
                           'dataprep_json': datapre_json,
                           "get_data_content": fn_script}
            adb_automl_context = [(index, run_context) for index in range(
                0, self.automl_settings.max_concurrent_iterations)]

            if not hasattr(self.automl_settings, 'is_run_from_test'):
                self._adb_thread = _AdbDriverNode("ADB Experiment: {0}".format(self.experiment.name),
                                                  adb_automl_context,
                                                  self.automl_settings.spark_context,
                                                  self.automl_settings.max_concurrent_iterations)
                self._adb_thread.start()
            else:
                automlRDD = self.automl_settings.\
                    spark_context.parallelize(adb_automl_context,
                                              self.automl_settings.max_concurrent_iterations)
                automlRDD.map(adb_run_experiment).collect()

            if show_output:
                RemoteConsoleInterface._show_output(self.current_run,
                                                    self._console_logger,
                                                    self.logger,
                                                    self.automl_settings.primary_metric)
        except Exception as ex:
            logging_utilities.log_traceback(ex, self.logger)
            raise

    def _create_parent_run(self, X=None, y=None, sample_weight=None, X_valid=None, y_valid=None,
                           sample_weight_valid=None, data=None, label=None, columns=None, cv_splits_indices=None,
                           existing_run=False):
        """
        Create parent run in Run History containing AutoML experiment information.

        :return: AutoML parent run
        :rtype: azureml.train.automl.AutoMLRun
        """
        #  Prepare data before entering for loop
        self.logger.info("Extracting user Data")
        self.input_data = _format_training_data(X, y, sample_weight, X_valid, y_valid, sample_weight_valid,
                                                data, label, columns, cv_splits_indices, self.user_script)
        _validate_training_data_dict(self.input_data, self.automl_settings)

        _auto_blacklist(self.input_data, self.automl_settings)
        if self.automl_settings.exclude_nan_labels:
            self.input_data = common_utilities._y_nan_check(self.input_data)
        _set_task_parameters(y=self.input_data.get('y'), automl_settings=self.automl_settings)

        if not existing_run:
            # min to sec conversion
            timeout = None
            if self.automl_settings.iteration_timeout_minutes:
                timeout = self.automl_settings.iteration_timeout_minutes * 60
            # Call Jasmine to create experiment and parent run history entries
            parent_run_dto = CreateParentRunDto(target='local',
                                                num_iterations=self.automl_settings.iterations,
                                                training_type=None,  # use self.training_type when jasmine supports it
                                                acquisition_function=None,
                                                metrics=['accuracy'],
                                                primary_metric=self.automl_settings.primary_metric,
                                                train_split=self.automl_settings.validation_size,
                                                max_time_seconds=timeout,
                                                acquisition_parameter=0.0,
                                                num_cross_validation=self.automl_settings.n_cross_validations,
                                                raw_aml_settings_string=str(
                                                    self.automl_settings._as_serializable_dict()),
                                                aml_settings_json_string=json.dumps(
                                                    self.automl_settings._as_serializable_dict()),
                                                enable_subsampling=self.automl_settings.enable_subsampling)
            try:
                self.logger.info("Start creating parent run with DTO: {0}."
                                 .format(self.automl_settings._format_selective(_blacklist_logging_keys)))
                self.parent_run_id = self._jasmine_client.post_parent_run(parent_run_dto)
            except HttpOperationError as e:
                logging_utilities.log_traceback(e, self.logger)
                friendly_http_exception(e, constants.API.CreateParentRun)
            except Exception as e:
                logging_utilities.log_traceback(e, self.logger)
                raise ServiceException("Error when trying to create parent run in automl service") from None

            self.current_run = AutoMLRun(self.experiment,
                                         self.parent_run_id,
                                         host=self.automl_settings.service_url)

            # only log user sdk dependencies on initial parent creation
            _log_user_sdk_dependencies(self.current_run, self.logger)

        else:
            self.current_run = AutoMLRun(self.experiment,
                                         self.parent_run_id,
                                         host=self.automl_settings.service_url)

        if self.user_script:
            self.logger.info("[ParentRunID:{}] Local run using user script.".format(self.parent_run_id))
        else:
            self.logger.info("[ParentRunID:{}] Local run using input X and y.".format(self.parent_run_id))

        self._console_logger.write("Parent Run ID: " + self.parent_run_id)
        self.logger.info("Parent Run ID: " + self.parent_run_id)

        self._status = constants.Status.InProgress

        self._log_data_stat(self.input_data.get("X"), 'X', prefix="[ParentRunId:{}]".format(self.parent_run_id))
        self._log_data_stat(self.input_data.get("y"), 'y', prefix="[ParentRunId:{}]".format(self.parent_run_id))

    def _get_transformed_context(self):
        if self.input_data.get("X_valid") is not None:
            self._log_data_stat(
                self.input_data.get("X_valid"), 'X_valid', prefix="[ParentRunId:{}]".format(self.parent_run_id)
            )
        if self.input_data.get("y_valid") is not None:
            self._log_data_stat(
                self.input_data.get("y_valid"), 'y_valid', prefix="[ParentRunId:{}]".format(self.parent_run_id)
            )

        raw_data_context = RawDataContext(task_type=self.automl_settings.task_type,
                                          X=self.input_data.get("X"),
                                          y=self.input_data.get("y"),
                                          X_valid=self.input_data.get(
                                              "X_valid"),
                                          y_valid=self.input_data.get(
                                              "y_valid"),
                                          sample_weight=self.input_data.get(
                                              "sample_weight"),
                                          sample_weight_valid=self.input_data.get(
                                              "sample_weight_valid"),
                                          x_raw_column_names=self.input_data.get(
                                              "x_raw_column_names"),
                                          preprocess=self.automl_settings.preprocess,
                                          lag_length=self.automl_settings.lag_length,
                                          cv_splits_indices=self.input_data.get(
                                              "cv_splits_indices"),
                                          automl_settings_obj=self.automl_settings,
                                          enable_cache=self.automl_settings.enable_cache,
                                          data_store=None
                                          )

        transformed_data_context = _transform_data(raw_data_context=raw_data_context,
                                                   logger=self.logger,
                                                   run_id=self.parent_run_id)

        return transformed_data_context

    def _fit_local(self, X=None, y=None, sample_weight=None, X_valid=None, y_valid=None, sample_weight_valid=None,
                   data=None, label=None, columns=None, cv_splits_indices=None, existing_run=False):
        self._create_parent_run(X=X, y=y, sample_weight=sample_weight, X_valid=X_valid, y_valid=y_valid,
                                data=data, label=label, columns=columns,
                                cv_splits_indices=cv_splits_indices, existing_run=existing_run,
                                sample_weight_valid=sample_weight_valid)

        transformed_data_context = self._get_transformed_context()

        _validate_data_splits(X=transformed_data_context.X,
                              y=transformed_data_context.y,
                              X_valid=transformed_data_context.X_valid,
                              y_valid=transformed_data_context.y_valid,
                              cv_splits=transformed_data_context.cv_splits,
                              automl_settings=self.automl_settings)

        if not existing_run:
            self._jasmine_client.set_parent_run_status(
                self.parent_run_id, constants.RunState.START_RUN)

            num_samples = self.input_data.get("X").shape[0]
            subsampling = self.automl_settings.enable_subsampling and \
                common_utilities.subsampling_recommended(
                    num_samples, self.automl_settings.iterations)

            # set the problem info, so the JOS can use it to get pipelines.
            automl.set_problem_info(transformed_data_context.X, transformed_data_context.y,
                                    self.automl_settings.task_type,
                                    current_run=self.current_run,
                                    preprocess=self.automl_settings.preprocess,
                                    lag_length=self.automl_settings.lag_length,
                                    transformed_data_context=transformed_data_context,
                                    enable_cache=self.automl_settings.enable_cache,
                                    subsampling=subsampling)
        self.experiment_start_time = datetime.utcnow()
        if self.automl_settings.experiment_timeout_minutes:
            def experiment_expired():
                self.logger.info("Experiment timeout reached.")
                self.cancel()
            experiment_timeout_timer = Timer(self.automl_settings.experiment_timeout_minutes * 60, experiment_expired)
            experiment_timeout_timer.daemon = True
            experiment_timeout_timer.start()

        try:
            #  Set up interface to print execution progress
            ci = ConsoleInterface("score", self._console_logger)
            ci.print_descriptions()
            ci.print_columns()
        except Exception as e:
            logging_utilities.log_traceback(e, self.logger)
            raise
        if existing_run:
            self.current_iter = len(
                list(self.current_run.get_children(_rehydrate_runs=False)))
            self.pipelines = [(constants.Defaults.DEFAULT_PIPELINE_SCORE,
                               constants.Defaults.INVALID_PIPELINE_FITTED,
                               constants.Defaults.INVALID_PIPELINE_FITTED,
                               constants.Defaults.INVALID_PIPELINE_VALIDATION_SCORES,
                               None)] * self.current_iter
        else:
            self.current_iter = 0
            self.pipelines = []
        try:
            self.logger.info("Start local loop.")

            while self.current_iter < self.automl_settings.iterations:
                self.logger.info("Start iteration: {0}".format(self.current_iter))
                if self._status == constants.Status.Terminated:
                    self._console_logger.write(
                        "Stopping criteria reached at iteration {0}. Ending experiment.".format(self.current_iter - 1))
                    self.logger.info(
                        "Stopping criteria reached at iteration {0}. Ending experiment.".format(self.current_iter - 1))
                    self._jasmine_client.set_parent_run_status(self.parent_run_id, constants.RunState.COMPLETE_RUN)
                    return AutoMLRun(self.experiment, self.parent_run_id, host=self.automl_settings.service_url)

                self._fit_iteration(ci,
                                    transformed_data_context=transformed_data_context)

            self._status = constants.Status.Completed
        except KeyboardInterrupt:
            self._status = constants.Status.Terminated
            self.logger.info(
                "[ParentRunId:{}]Received interrupt. Returning now.".format(self.parent_run_id))
            self._console_logger.write("Received interrupt. Returning now.")
            self._jasmine_client.set_parent_run_status(self.parent_run_id, constants.RunState.CANCEL_RUN)
        finally:
            # turn off system usage collection on run completion or failure
            if self._usage_telemetry is not None:
                self._usage_telemetry.stop()

            if not existing_run and self._status != constants.Status.Terminated:
                self._jasmine_client.set_parent_run_status(
                    self.parent_run_id, constants.RunState.COMPLETE_RUN)
            # cleanup transformed, preprocessed data cache
            if transformed_data_context is not None:
                transformed_data_context.cleanup()

        self.logger.info("Run Complete.")

    def _fit_iteration(self, ci, transformed_data_context=None):
        start_iter_time = datetime.utcnow()

        #  Query Jasmine for the next set of pipelines to run
        pipeline_dto = self._get_pipeline()

        run_id = pipeline_dto.childrun_id
        pipeline_id = pipeline_dto.pipeline_id
        pipeline_script = pipeline_dto.pipeline_spec
        train_frac = float(pipeline_dto.training_percent or 100) / 100
        self.logger.info("Received pipeline: {0}".format(pipeline_script))

        ci.print_start(self.current_iter)
        validation_scores = {'metrics': None}
        error = None
        child_run_metrics = None
        try:
            child_run = Run(self.experiment, run_id, _batch_upload_metrics=False)
            # get total run time in seconds and convert to minutes
            elapsed_time = math.floor(int((datetime.utcnow() - self.experiment_start_time).total_seconds()) / 60)
            child_run.start()
            validation_scores = automl.fit_pipeline(
                child_run_metrics=child_run,
                pipeline_script=pipeline_script,
                automl_settings=self.automl_settings,
                run_id=run_id,
                experiment=self.experiment,
                pipeline_id=pipeline_id,
                logger=self.logger,
                remote=False,
                fit_iteration_parameters_dict=None,
                transformed_data_context=transformed_data_context,
                train_frac=train_frac,
                elapsed_time=elapsed_time
            )

            if len(validation_scores['errors']) > 0:
                err_type = next(iter(validation_scores['errors']))
                inner_exception = validation_scores['errors'][err_type]
                inner_type = validation_scores['errors'][err_type]['exception']
                if 'TimeoutError' in inner_exception['traceback']:
                    error = "Fit operation exceeded provided timeout, terminating and moving onto the next iteration."
                else:
                    raise RuntimeError("Run '{0}' failed. Check the log for more details.".format(
                        run_id)) from inner_type
            self._validation_scores.insert(self.current_iter, validation_scores)
            if validation_scores is None or len(validation_scores) == 0:
                raise RuntimeError("Fit failed for this iteration for unknown reasons. Check the log "
                                   "for more details.")
            score = float(validation_scores[self.automl_settings.primary_metric])
            fitted_pipeline = validation_scores['fitted_pipeline']
            pipeline_script = validation_scores['pipeline_spec']
            preprocessor = validation_scores['run_preprocessor']
            model_name = validation_scores['run_algorithm']
        except Exception as e:
            logging_utilities.log_traceback(e, self.logger)
            score = constants.Defaults.DEFAULT_PIPELINE_SCORE
            self._validation_scores.insert(self.current_iter, constants.Defaults.INVALID_PIPELINE_VALIDATION_SCORES)
            fitted_pipeline = constants.Defaults.INVALID_PIPELINE_FITTED
            preprocessor = ''
            model_name = ''
            if error is None:
                error = e

        ci.print_pipeline(preprocessor, model_name, train_frac)
        self._update_internal_scores_after_iteration(score)

        self.pipelines.append((score,
                               pipeline_script,
                               fitted_pipeline,
                               validation_scores,
                               AutoMLRun(self.experiment,
                                         self.parent_run_id,
                                         host=self.automl_settings.service_url)))

        end_iter_time = datetime.utcnow()
        end_iter_time = end_iter_time.replace(tzinfo=pytz.UTC)
        start_iter_time = start_iter_time.replace(tzinfo=pytz.UTC)
        if child_run_metrics is not None:
            created_time = child_run_metrics._run_dto['created_utc']
            if isinstance(created_time, str):
                created_time = datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%S.%fZ')
            start_iter_time = created_time.replace(tzinfo=pytz.UTC)
            details = child_run_metrics.get_details()
            if 'endTimeUtc' in details:
                end_iter_time = datetime.strptime(details['endTimeUtc'],
                                                  '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.UTC)
        iter_duration = str(end_iter_time - start_iter_time).split(".")[0]

        ci.print_end(iter_duration, score, self._score_best)
        self.current_iter = self.current_iter + 1

        if error is not None:
            ci.print_error(error)
        if self.automl_settings.experiment_exit_score is not None and isinstance(score, float):
            if self.automl_settings.metric_operation == constants.OptimizerObjectives.MINIMIZE:
                if score < self.automl_settings.experiment_exit_score:
                    self.logger.info("Experiment reached score {0} within exit score criteria {1}."
                                     .format(score, self.automl_settings.experiment_exit_score))
                    self.cancel()
            elif self.automl_settings.metric_operation == constants.OptimizerObjectives.MAXIMIZE:
                if score > self.automl_settings.experiment_exit_score:
                    self.logger.info("Experiment reached score {0} within exit score criteria {1}."
                                     .format(score, self.automl_settings.experiment_exit_score))
                    self.cancel()

    def _fit_remote(self, run_configuration, X=None, y=None, sample_weight=None, X_valid=None, y_valid=None,
                    sample_weight_valid=None, cv_splits_indices=None, show_output=False):

        self._fit_remote_core(run_configuration, X=X, y=y, sample_weight=sample_weight, X_valid=X_valid,
                              y_valid=y_valid, sample_weight_valid=sample_weight_valid,
                              cv_splits_indices=cv_splits_indices)
        if show_output:
            RemoteConsoleInterface._show_output(self.current_run,
                                                self._console_logger,
                                                self.logger,
                                                self.automl_settings.primary_metric)

    def _fit_remote_core(self, run_configuration, X=None, y=None, sample_weight=None, X_valid=None, y_valid=None,
                         sample_weight_valid=None, cv_splits_indices=None):
        if isinstance(run_configuration, str):
            run_config_object = RunConfiguration.load(
                self.automl_settings.path, run_configuration)
        else:
            # we alread have a run configuration object
            run_config_object = run_configuration
            run_configuration = run_config_object.target

        run_config_object = self._modify_run_configuration(run_config_object)

        dataprep_json = _dataprep_utilities.get_dataprep_json(X=X, y=y,
                                                              sample_weight=sample_weight,
                                                              X_valid=X_valid,
                                                              y_valid=y_valid,
                                                              sample_weight_valid=sample_weight_valid)

        # min to sec conversion
        timeout = None
        if self.automl_settings.iteration_timeout_minutes:
            timeout = self.automl_settings.iteration_timeout_minutes * 60
        parent_run_dto = CreateParentRunDto(target=run_configuration,
                                            num_iterations=self.automl_settings.iterations,
                                            training_type=None,  # use self.training_type when jasmine supports it
                                            acquisition_function=None,
                                            metrics=['accuracy'],
                                            primary_metric=self.automl_settings.primary_metric,
                                            train_split=self.automl_settings.validation_size,
                                            max_time_seconds=timeout,
                                            acquisition_parameter=0.0,
                                            num_cross_validation=self.automl_settings.n_cross_validations,
                                            raw_aml_settings_string=str(
                                                self.automl_settings._as_serializable_dict()),
                                            aml_settings_json_string=json.dumps(
                                                self.automl_settings._as_serializable_dict()),
                                            data_prep_json_string=dataprep_json,
                                            enable_subsampling=self.automl_settings.enable_subsampling)

        try:
            self.logger.info(
                "Start creating parent run with DTO: {0}.".format(
                    self.automl_settings._format_selective(_blacklist_logging_keys)))
            self.parent_run_id = self._jasmine_client.post_parent_run(
                parent_run_dto)
        except HttpOperationError as e:
            logging_utilities.log_traceback(e, self.logger)
            friendly_http_exception(e, constants.API.CreateParentRun)
        except Exception as e:
            logging_utilities.log_traceback(e, self.logger)
            raise ServiceException("Error occurred when trying to create new parent run in AutoML service.") from None

        if self.user_script:
            self.logger.info(
                "[ParentRunID:{}] Remote run using user script.".format(self.parent_run_id))
        else:
            self.logger.info(
                "[ParentRunID:{}] Remote run using input X and y.".format(self.parent_run_id))

        if self.current_run is None:
            self.current_run = AutoMLRun(self.experiment, self.parent_run_id, host=self.automl_settings.service_url)

        _log_user_sdk_dependencies(self.current_run, self.logger)

        self._console_logger.write("Parent Run ID: " + self.parent_run_id)
        self.logger.info("Parent Run ID: " + self.parent_run_id)

        snapshotId = ""
        if self.automl_settings.path is not None:
            snapshotId = self.current_run.take_snapshot(self.automl_settings.path)
        self.logger.info("Snapshotted folder: {0} with snapshot_id: {1}".format(
            self.automl_settings.path, snapshotId))

        self.pipelines = []

        definition = {
            "Configuration": RunConfiguration._serialize_to_dict(run_config_object)
        }

        # BUG: 287204
        del definition["Configuration"]["environment"]["python"]["condaDependenciesFile"]
        definition["Configuration"]["environment"]["python"]["condaDependencies"] = \
            run_config_object.environment.python.conda_dependencies._conda_dependencies

        self.logger.info("Starting a snapshot run (snapshotId : {0}) with following compute definition: {1}"
                         .format(snapshotId, definition))
        try:
            self._jasmine_client.post_remote_jasmine_snapshot_run(self.parent_run_id,
                                                                  json.dumps(
                                                                      definition),
                                                                  snapshotId)
        except HttpOperationError as e:
            logging_utilities.log_traceback(e, self.logger)
            friendly_http_exception(e, constants.API.StartRemoteSnapshotRun)
        except Exception as e:
            logging_utilities.log_traceback(e, self.logger)
            raise ServiceException("Error occurred when trying to submit a remote run to AutoML Service.") \
                from None

    def _get_pipeline(self):
        """
        Query Jasmine for the next set of pipelines.

        :return: List of pipeline specs to evaluate next
        """
        try:
            self.logger.info("Querying Jasmine for next pipeline.")
            return self._jasmine_client.get_pipeline(self.parent_run_id, self.current_iter)
        except HttpOperationError as e:
            logging_utilities.log_traceback(e, self.logger)
            friendly_http_exception(e, constants.API.GetNextPipeline)
        except Exception as e:
            logging_utilities.log_traceback(e, self.logger)
            raise ServiceException("Error occurred when trying to fetch next iteration from AutoML service.") from None

    def _check_create_folders(self, path):
        if path is None:
            path = os.getcwd()
        # Expand out the path because os.makedirs can't handle '..' properly
        aml_config_path = os.path.abspath(os.path.join(path, 'aml_config'))
        os.makedirs(aml_config_path, exist_ok=True)

    def _modify_run_configuration(self, run_config):
        """Modify the run configuration with the correct version of AutoML and pip feed."""
        import azureml.core
        from azureml.core.conda_dependencies import CondaDependencies, DEFAULT_SDK_ORIGIN
        try:
            core_version = azureml.core.VERSION
            automl_version = azureml.train.automl.VERSION

            # ignore version if it is a dev package and warn user
            warn_cannot_run_local_pkg = False
            if core_version and ("dev" in core_version or core_version == "0.1.0.0"):
                core_version = None
                warn_cannot_run_local_pkg = True
            if automl_version and ("dev" in automl_version or automl_version == "0.1.0.0"):
                automl_version = None
                warn_cannot_run_local_pkg = True

            if warn_cannot_run_local_pkg:
                self.logger.warning("You are running a developer or editable installation of required packages. Your "
                                    "changes will not be run on your remote compute. Latest versions of "
                                    "azureml-core and azureml-train-automl will be used unless you have "
                                    "specified an alternative index or version to use.")
        except Exception:
            self.logger.warning("Could not find the version info for azureml-core or azureml-train-automl")
            core_version = None
            automl_version = None

        sdk_origin_url = CondaDependencies.sdk_origin_url()

        run_config.auto_prepare_environment = True

        dependencies = run_config.environment.python.conda_dependencies
        # if debug flag sets an sdk_url use it
        if self.automl_settings.sdk_url is not None:
            dependencies.set_pip_option("--extra-index-url " + self.automl_settings.sdk_url)

        # if debug_flag sets packages, use those in remote run
        if self.automl_settings.sdk_packages is not None:
            for package in self.automl_settings.sdk_packages:
                dependencies.add_pip_package(package)

        automl_regex = r"azureml\S*automl\S*"
        numpy_regex = r"numpy([\=\<\>\~0-9\.\s]+|\Z)"

        # ensure numpy is included
        if not re.findall(numpy_regex, " ".join(dependencies.conda_packages)):
            dependencies.add_conda_package("numpy")

        # if automl package not present add it and pin the version
        if not re.findall(automl_regex, " ".join(dependencies.pip_packages)):
            azureml = "azureml-defaults"
            automl = "azureml-train-automl"
            if core_version:
                azureml = azureml + "==" + core_version
                # only add core if version should be pinned
                dependencies.add_pip_package(azureml)
            if automl_version:
                automl = automl + "==" + automl_version

            # if we pin the version we should make sure the origin index is added
            if (automl_version or core_version) and sdk_origin_url != DEFAULT_SDK_ORIGIN:
                dependencies.set_pip_option("--extra-index-url " + sdk_origin_url)

            dependencies.add_pip_package(automl)
            dependencies.add_pip_package("azureml-explain-model")

        run_config.environment.python.conda_dependencies = dependencies
        return run_config

    def _update_internal_scores_after_iteration(self, score):
        if self._score_max is None or np.isnan(self._score_max) or score > self._score_max:
            self._score_max = score
        if self._score_min is None or np.isnan(self._score_min) or score < self._score_min:
            self._score_min = score

        if self.automl_settings.metric_operation == constants.OptimizerObjectives.MINIMIZE:
            self._score_best = self._score_min
        elif self.automl_settings.metric_operation == constants.OptimizerObjectives.MAXIMIZE:
            self._score_best = self._score_max

    def _log_data_stat(self, data, data_name, prefix=None):
        if prefix is None:
            prefix = ""
        if type(data) is not np.ndarray and type(data) is not np.array and type(data) is not pd.DataFrame:
            try:
                data = data.to_pandas_dataframe()
            except AttributeError:
                self.logger.warning("The data type is not supported for logging.")
                return
        self.logger.info(
            "{}Input {} datatype is {}, shape is {}, datasize is {}.".format(
                prefix, data_name, type(data), data.shape, sys.getsizeof(data)
            )
        )

    @staticmethod
    def _is_tensorflow_module_present():
        try:
            return pipeline_spec.tf_wrappers.tf_found
        except Exception:
            return False

    @staticmethod
    def _is_xgboost_module_present():
        try:
            return model_wrappers.xgboost_present
        except Exception:
            return False
