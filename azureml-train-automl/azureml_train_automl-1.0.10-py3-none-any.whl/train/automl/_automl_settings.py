# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Manages settings for AutoML experiment."""
import logging
import math

from automl.client.core.common.constants import ModelNameMappings, SupportedModelNames
from automl.client.core.common.metrics import (get_default_metrics,
                                               minimize_or_maximize)

from azureml.core.compute import ComputeTarget

from . import constants
from .utilities import _get_primary_metrics


class _AutoMLSettings(object):
    """Persist and validate settings for an AutoML experiment."""

    MAXIMUM_DEFAULT_ENSEMBLE_SELECTION_ITERATIONS = 15

    def __init__(self,
                 experiment=None,
                 path=None,
                 iterations=100,
                 data_script=None,
                 primary_metric=None,
                 task_type=None,
                 compute_target=None,
                 spark_context=None,
                 validation_size=None,
                 n_cross_validations=None,
                 y_min=None,
                 y_max=None,
                 num_classes=None,
                 preprocess=False,
                 lag_length=0,
                 max_cores_per_iteration=1,
                 max_concurrent_iterations=1,
                 iteration_timeout_minutes=None,
                 mem_in_mb=None,
                 enforce_time_on_windows=None,
                 experiment_timeout_minutes=None,
                 experiment_exit_score=None,
                 blacklist_models=None,
                 whitelist_models=None,
                 auto_blacklist=True,
                 exclude_nan_labels=True,
                 verbosity=logging.INFO,
                 debug_log='automl.log',
                 debug_flag=None,
                 enable_ensembling=True,
                 ensemble_iterations=None,
                 model_explainability=False,
                 enable_tf=True,
                 enable_cache=True,
                 enable_subsampling=False,
                 subsample_seed=None,
                 cost_mode=constants.PipelineCost.COST_NONE,
                 is_timeseries=False,
                 **kwargs):
        """
        Manage settings used by AutoML components.

        :param experiment: The azureml.core experiment
        :param path: Full path to the project folder
        :param iterations: Number of different pipelines to test
        :param data_script: File path to the script containing get_data()
        :param primary_metric: The metric that you want to optimize.
        :param task_type: Field describing whether this will be a classification or regression experiment
        :param compute_target: The AzureML compute to run the AutoML experiment on
        :param spark_context: Spark context, only applicable when used inside azure databricks/spark environment.
        :type spark_context: SparkContext
        :param validation_size: What percent of the data to hold out for validation
        :param n_cross_validations: How many cross validations to perform
        :param y_min: Minimum value of y for a regression experiment
        :param y_max: Maximum value of y for a regression experiment
        :param num_classes: Number of classes in the label data
        :param preprocess: Flag whether AutoML should preprocess your data for you
        :param lag_length: How many rows to lag data when preprocessing time series data
        :param max_cores_per_iteration: Maximum number of threads to use for a given iteration
        :param max_concurrent_iterations:
            Maximum number of iterations that would be executed in parallel.
            This should be less than the number of cores on the AzureML compute. Formerly concurrent_iterations.
        :param iteration_timeout_minutes: Maximum time in seconds that each iteration before it terminates
        :param mem_in_mb: Maximum memory usage of each iteration before it terminates
        :param enforce_time_on_windows: flag to enforce time limit on model training at each iteration under windows.
        :param experiment_timeout_minutes: Maximum amount of time that all iterations combined can take
        :param experiment_exit_score:
            Target score for experiment. Experiment will terminate after this score is reached.
        :param blacklist_models: List of algorithms to ignore for AutoML experiment
        :param whitelist_models: List of model names to search for AutoML experiment
        :param exclude_nan_labels: Flag whether to exclude rows with NaN values in the label
        :param auto_blacklist: Flag whether AutoML should try to exclude algorithms
            that it thinks won't perform well.
        :param verbosity: Verbosity level for AutoML log file
        :param debug_log: File path to AutoML logs
        :param enable_ensembling: Flag to enable/disable an extra iteration for model ensembling
        :param ensemble_iterations: Number of models to consider for the ensemble generation
        :param model_explainability: Flag whether to explain AutoML model
        :param enable_TF: Flag to enable/disable Tensorflow algorithms
        :param enable_cache: Flag to enable/disable disk cache for transformed, preprocessed data.
        :param enable_subsampling: Flag to enable/disable subsampling. Note that even if it's true,
            subsampling would not be enabled for small datasets or iterations.
        :param subsample_seed: random_state used to sample the data.
        :param cost_mode: Flag to set cost prediction modes. COST_NONE stands for none cost prediction,
            COST_FILTER stands for cost prediction per iteration.
        :type cost_mode: int or automl.client.core.common.constants.PipelineCost
        :param is_timeseries: Flag whether AutoML should process your data as time series data.
        :type is_timeseries: bool
        :param kwargs:
        """
        if experiment is None:
            self.name = None
            self.path = None
            self.subscription_id = None
            self.resource_group = None
            self.workspace_name = None
        else:
            # This is used in the remote case values are populated through
            # AMLSettings
            self.name = experiment.name
            self.path = path
            self.subscription_id = experiment.workspace.subscription_id
            self.resource_group = experiment.workspace.resource_group
            self.workspace_name = experiment.workspace.name

        self.iterations = iterations
        self.primary_metric = primary_metric
        self.data_script = data_script

        self.compute_target = compute_target
        self.task_type = task_type

        # TODO remove this once Miro/AutoML common code can handle None
        if validation_size is None:
            self.validation_size = 0.0
        else:
            self.validation_size = validation_size
        self.n_cross_validations = n_cross_validations

        self.y_min = y_min
        self.y_max = y_max

        self.num_classes = num_classes

        self.preprocess = preprocess
        self.lag_length = lag_length
        self.is_timeseries = is_timeseries

        self.max_cores_per_iteration = max_cores_per_iteration
        self.max_concurrent_iterations = max_concurrent_iterations
        self.iteration_timeout_minutes = iteration_timeout_minutes
        self.mem_in_mb = mem_in_mb
        self.enforce_time_on_windows = enforce_time_on_windows
        self.experiment_timeout_minutes = experiment_timeout_minutes
        self.experiment_exit_score = experiment_exit_score

        self.whitelist_models = self.filter_model_names_to_customer_facing_only(whitelist_models)
        self.blacklist_algos = self.filter_model_names_to_customer_facing_only(blacklist_models)
        self.auto_blacklist = auto_blacklist
        self.blacklist_samples_reached = False
        self.exclude_nan_labels = exclude_nan_labels

        self.verbosity = verbosity
        self.debug_log = debug_log
        self.show_warnings = False
        self.model_explainability = model_explainability
        self.service_url = None
        self.sdk_url = None
        self.sdk_packages = None

        # telemetry settings
        self.telemetry_verbosity = logging.getLevelName(logging.NOTSET)
        self.send_telemetry = False

        # time series settings
        if is_timeseries:
            self.time_column_name = kwargs.get(constants.TimeSeries.TIME_COLUMN_NAME, None)
            self.grain_column_names = kwargs.get(constants.TimeSeries.GRAIN_COLUMN_NAMES, None)
            self.drop_column_names = kwargs.get(constants.TimeSeries.DROP_COLUMN_NAMES, None)

        self.spark_context = spark_context
        self.spark_service = None
        if self.spark_context:
            self.spark_service = 'adb'

        if debug_flag:
            if 'service_url' in debug_flag:
                self.service_url = debug_flag['service_url']
            if 'show_warnings' in debug_flag:
                self.show_warnings = debug_flag['show_warnings']
            if 'sdk_url' in debug_flag:
                self.sdk_url = debug_flag['sdk_url']
            if 'sdk_packages' in debug_flag:
                self.sdk_packages = debug_flag['sdk_packages']

        # Deprecated param
        self.metrics = None

        if self.iterations > 2:
            self.enable_ensembling = enable_ensembling
            if ensemble_iterations is not None:
                self.ensemble_iterations = ensemble_iterations
            else:
                self.ensemble_iterations = min(_AutoMLSettings.MAXIMUM_DEFAULT_ENSEMBLE_SELECTION_ITERATIONS,
                                               self.iterations)
        else:
            self.enable_ensembling = False
            self.ensemble_iterations = None

        self.enable_tf = enable_tf
        self.enable_cache = enable_cache
        self.enable_subsampling = enable_subsampling
        self.subsample_seed = subsample_seed

        self.cost_mode = cost_mode
        self._verify_settings()

        # TODO remove this once JOS and Miro deployed to all regions, it is for backward compatibility
        self._map_filterlists()

        # Settings that need to be set after verification
        if self.task_type is not None and self.primary_metric is not None:
            self.metric_operation = minimize_or_maximize(
                task=self.task_type, metric=self.primary_metric)
        else:
            self.metric_operation = None

        # Deprecation of concurrent_iterations
        try:
            concurrent_iterations = kwargs.pop('concurrent_iterations')
            logging.warning("Parameter 'concurrent_iterations' will be deprecated. Use 'max_concurrent_iterations'")
            self.max_concurrent_iterations = concurrent_iterations
        except KeyError:
            pass

        # Deprecation of max_time_sec
        try:
            max_time_sec = kwargs.pop('max_time_sec')
            logging.warning("Parameter 'max_time_sec' will be deprecated. Use 'iteration_timeout_minutes'")
            if max_time_sec:
                self.iteration_timeout_minutes = math.ceil(max_time_sec / 60)
        except KeyError:
            pass

        # Deprecation of exit_time_sec
        try:
            exit_time_sec = kwargs.pop('exit_time_sec')
            logging.warning("Parameter 'exit_time_sec' will be deprecated. Use 'experiment_timeout_minutes'")
            if exit_time_sec:
                self.experiment_timeout_minutes = math.ceil(exit_time_sec / 60)
        except KeyError:
            pass

        # Deprecation of exit_score
        try:
            exit_score = kwargs.pop('exit_score')
            logging.warning("Parameter 'exit_score' will be deprecated. Use 'experiment_exit_score'")
            self.experiment_exit_score = exit_score
        except KeyError:
            pass

        # Deprecation of blacklist_algos
        try:
            blacklist_algos = kwargs.pop('blacklist_algos')
            self.blacklist_algos = blacklist_algos
        except KeyError:
            pass

        for key, value in kwargs.items():
            if key not in self.__dict__.keys():
                logging.warning(
                    "Received unrecognized parameter: {0} {1}".format(
                        key, value))
            setattr(self, key, value)

    def _verify_settings(self):
        """
        Verify that input automl_settings are sensible.

        :return:
        :rtype: None
        """
        if self.n_cross_validations is not None and self.validation_size is not None:
            if not (self.n_cross_validations > 0) and not (
                    self.validation_size > 0.0):
                logging.warning("Neither n_cross_validations nor validation_size specified. "
                                "You will need to either pass custom validation data or cv_split_indices to "
                                "the submit(), fit(), or get_data() methods.")

        if self.validation_size is not None:
            if self.validation_size > 1.0 or self.validation_size < 0.0:
                raise ValueError(
                    "validation_size parameter must be between 0 and 1 when specified.")

        if self.n_cross_validations is not None:
            if self.n_cross_validations == 1 or self.n_cross_validations < 0:
                raise ValueError(
                    "n_cross_validations must be greater than or equal to 2 when specified.")

        if self.iterations > constants.MAX_ITERATIONS:
            raise ValueError(
                "Number of iterations cannot be larger than {0}.".format(
                    constants.MAX_ITERATIONS))

        if self.primary_metric is None:
            if self.task_type is constants.Tasks.CLASSIFICATION:
                self.primary_metric = constants.Metric.Accuracy
            elif self.task_type is constants.Tasks.REGRESSION:
                self.primary_metric = constants.Metric.Spearman
        else:
            if self.task_type is not None:
                if self.primary_metric not in _get_primary_metrics(
                        self.task_type):
                    raise ValueError("Invalid primary metric specified for {0}. Please use on of: {1}".format(
                        self.task_type, _get_primary_metrics(self.task_type)))
            else:
                if self.primary_metric in constants.Metric.REGRESSION_PRIMARY_SET:
                    self.task_type = constants.Tasks.REGRESSION
                elif self.primary_metric in constants.Metric.CLASSIFICATION_PRIMARY_SET:
                    self.task_type = constants.Tasks.CLASSIFICATION
                else:
                    raise ValueError("Invalid primary metric specified. Please use one of {0} for classification or "
                                     "{1} for regression.".format(constants.Metric.CLASSIFICATION_PRIMARY_SET,
                                                                  constants.Metric.REGRESSION_PRIMARY_SET))

        if self.enable_ensembling and self.ensemble_iterations < 1:
            raise ValueError(
                "When ensembling is enabled, the ensemble_iterations setting can't be less than 1")

        if self.enable_ensembling and self.ensemble_iterations > self.iterations:
            raise ValueError(
                "When ensembling is enabled, the ensemble_iterations setting can't be greater than \
                the total number of iterations: {0}".format(self.iterations))

        if self.path is not None and not isinstance(self.path, str):
            raise ValueError('Input parameter \"path\" needs to be a string. '
                             'Received \"{0}\".'.format(type(self.path)))
        if self.compute_target is not None and not isinstance(self.compute_target, str) and \
                not isinstance(self.compute_target, ComputeTarget):
            raise ValueError('Input parameter \"compute_target\" needs to be an AzureML compute target. '
                             'Received \"{0}\". You may have intended to pass a run configuration, '
                             'if so, please pass it as \"run_configuration=\'{1}\'\".'
                             .format(type(self.compute_target), self.compute_target))
        if not isinstance(self.preprocess, bool):
            raise ValueError('Input parameter \"preprocess\" needs to be a boolean. '
                             'Received \"{0}\".'.format(type(self.preprocess)))
        if self.max_cores_per_iteration is not None and \
                (self.max_cores_per_iteration != -1 and self.max_cores_per_iteration < 1):
            raise ValueError('Input parameter \"max_cores_per_iteration\" '
                             'needs to be -1 or greater than or equal to 1. '
                             'Received \"{0}\".'.format(self.max_cores_per_iteration))
        if self.max_concurrent_iterations is not None and self.max_concurrent_iterations < 1:
            raise ValueError('Input parameter \"max_concurrent_iterations\" '
                             'needs to be greater than or equal to 1 if set. '
                             'Received \"{0}\".'.format(self.max_concurrent_iterations))
        if self.iteration_timeout_minutes is not None and self.iteration_timeout_minutes < 1:
            raise ValueError('Input parameter \"iteration_timeout_minutes\" needs to be greater than or equal to 1 '
                             'if set. Received \"{0}\".'.format(self.iteration_timeout_minutes))
        if self.mem_in_mb is not None and self.mem_in_mb < 1:
            raise ValueError('Input parameter \"mem_in_mb\" needs to be greater than or equal to 1 if set. '
                             'Received \"{0}\".'.format(self.mem_in_mb))
        if self.enforce_time_on_windows is not None and not isinstance(self.enforce_time_on_windows, bool):
            raise ValueError('Input parameter \"enforce_time_on_windows\" needs to be a boolean if set. '
                             'Received \"{0}\".'.format(type(self.enforce_time_on_windows)))
        if self.experiment_timeout_minutes is not None and self.experiment_timeout_minutes < 1:
            raise ValueError('Input parameter \"experiment_timeout_minutes\" needs to be greater than or equal to 1 '
                             'if set. Received \"{0}\".'.format(self.experiment_timeout_minutes))
        if self.blacklist_algos is not None and not isinstance(self.blacklist_algos, list):
            raise ValueError('Input parameter \"blacklist_algos\" needs to be a list of strings. '
                             'Received \"{0}\".'.format(type(self.blacklist_algos)))
        if not isinstance(self.auto_blacklist, bool):
            raise ValueError('Input parameter \"auto_blacklist\" needs to be a boolean. '
                             'Received \"{0}\".'.format(type(self.auto_blacklist)))
        if not isinstance(self.exclude_nan_labels, bool):
            raise ValueError('Input parameter \"exclude_nan_labels\" needs to be a boolean. '
                             'Received \"{0}\".'.format(type(self.exclude_nan_labels)))
        if self.debug_log is not None and not isinstance(self.debug_log, str):
            raise ValueError('Input parameter \"debug_log\" needs to be a string filepath. '
                             'Received \"{0}\".'.format(type(self.debug_log)))
        if self.is_timeseries:
            if self.preprocess:
                raise ValueError('Timeseries use its own preprocess, disable preprocess to run')
            if self.task_type == constants.Tasks.CLASSIFICATION:
                raise ValueError('Timeseries do not support classification yet.'
                                 'Received \"{0}\".'.format(type(self.task_type)))
            if self.time_column_name is None:
                raise ValueError('Timeseries need to set time column. ')
        if not isinstance(self.enable_subsampling, bool):
            raise ValueError('Input parameter \"enable_subsampling\" needs to be a boolean. '
                             'Received \"{0}\".'.format(type(self.enable_subsampling)))
        if not self.enable_subsampling and self.subsample_seed:
            logging.warning('Input parameter \"enable_subsampling\" is set to False '
                            'but \"subsample_seed\" was specified.')
        if self.enable_subsampling and self.subsample_seed and not \
                isinstance(self.subsample_seed, int):
            raise ValueError('Input parameter \"subsample_seed\" needs to be an integer. '
                             'Received \"{0}\".'.format(type(self.subsample_seed)))

        if self.whitelist_models is not None:
            if len(self.whitelist_models) == 0:
                raise ValueError('Input values for whitelist_models not recognized. Please use one of {}'.format(
                    self._get_supported_model_names()))

        if self.blacklist_algos is not None:
            if all([model in self.blacklist_algos for model in self._get_supported_model_names()]):
                raise ValueError('All models are blacklisted, please make sure at least one model is allowed')

    def filter_model_names_to_customer_facing_only(self, model_names):
        if model_names is None:
            return None
        supported_model_names = self._get_supported_model_names()
        return [model for model in model_names if model
                in supported_model_names]

    def _get_supported_model_names(self):
        supported_model_names = []
        if self.task_type == constants.Tasks.CLASSIFICATION:
            supported_model_names = [model.customer_model_name for model in
                                     SupportedModelNames.SupportedClassificationModelList]
        elif self.task_type == constants.Tasks.REGRESSION:
            supported_model_names = [model.customer_model_name for model in
                                     SupportedModelNames.SupportedRegressionModelList]
        return supported_model_names

    def _map_filterlists(self):
        """Temporarily map customer facing names to class back end names for JOS and Miro backwards compatibility."""
        new_blacklist = None
        new_whitelist = None

        if self.blacklist_algos is not None:
            new_blacklist = self.blacklist_algos.copy()
            for algo in self.blacklist_algos:
                if self.task_type == constants.Tasks.CLASSIFICATION:
                    new_blacklist.append(
                        ModelNameMappings.CustomerFacingModelToClassNameModelMapClassification.get(algo))
                elif self.task_type == constants.Tasks.REGRESSION:
                    new_blacklist.append(
                        ModelNameMappings.CustomerFacingModelToClassNameModelMapRegression.get(algo))
            new_blacklist = [model for model in new_blacklist if model is not None]

        if self.whitelist_models is not None:
            new_whitelist = self.whitelist_models.copy()
            for algo in self.whitelist_models:
                if self.task_type == constants.Tasks.CLASSIFICATION:
                    new_whitelist.append(
                        ModelNameMappings.CustomerFacingModelToClassNameModelMapClassification.get(algo))
                elif self.task_type == constants.Tasks.REGRESSION:
                    new_whitelist.append(
                        ModelNameMappings.CustomerFacingModelToClassNameModelMapRegression.get(algo))
            new_whitelist = [model for model in new_whitelist if model is not None]

        self.blacklist_algos = new_blacklist
        self.whitelist_models = new_whitelist

    @staticmethod
    def from_string_or_dict(val, experiment=None):
        if isinstance(val, str):
            val = eval(val)
        if isinstance(val, dict):
            val = _AutoMLSettings(experiment=experiment, **val)

        if isinstance(val, _AutoMLSettings):
            return val
        else:
            raise ValueError("`input` parameter is not of type string or dict")

    def __str__(self):
        output = [' - {0}: {1}'.format(k, v) for k, v in self.__dict__.items()]
        return '\n'.join(output)

    def _format_selective(self, black_list_keys):
        """
        Format selective items for logging.

        Returned string will look as follows below
        Example:
            - key1: value1
            - key2: value2

        :param black_list_keys: List of keys to ignore.
        :type black_list_keys: list(str)
        :return: Filterd settings as string
        :rtype: str
        """
        dict_copy = self._filter(black_list_keys=black_list_keys)
        output = [' - {0}: {1}'.format(k, v) for k, v in dict_copy.items()]
        return '\n'.join(output)

    def _as_serializable_dict(self):
        return self._filter(['spark_context'])

    def _filter(self, black_list_keys):
        return dict([(k, v) for k, v in self.__dict__.items()
                     if black_list_keys is None or k not in black_list_keys])
