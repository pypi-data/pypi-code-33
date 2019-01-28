# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Configuration for submitting an Automated Machine Learning experiment.

Classes include methods for defining training features and labels, iteration count and max time, optimization
metrics, compute targets, and algorithms to blacklist.
"""
import inspect
import logging
import math
import os
from functools import reduce

from azureml.core._experiment_method import experiment_method
from azureml.core.experiment import Experiment
from azureml.core.runconfig import RunConfiguration

from . import constants
from . import _dataprep_utilities

from ._azureautomlclient import AzureAutoMLClient


def _automl_static_submit(automl_config_object,
                          workspace,
                          experiment_name,
                          **kwargs):
    """
    Start AutoML execution with the given config on the given workspace.

    :param automl_config_object:
    :param workspace:
    :param experiment_name:
    :param kwargs:
    :return:
    """
    automl_config_object._validate_config_settings()
    automl_config_object._get_remove_fit_params()

    experiment = Experiment(workspace, experiment_name)

    show_output = kwargs.get('show_output', None)

    settings = automl_config_object.user_settings

    automl_estimator = AzureAutoMLClient(experiment, **settings)

    return automl_estimator.fit(**automl_config_object.fit_params,
                                show_output=show_output)


class AutoMLConfig(object):
    """
    Configuration for submitting an Automated Machine Learning experiment in Azure Machine Learning service.

    This configuration object contains and persists the parameters for configuring
    the experiment run parameters, as well as the training data to be used at run time. The following
    code shows a basic example of creating an AutoMLConfig object, and submitting an
    experiment with the defined configuration:

    .. code-block:: python

        from azureml.core.experiment import Experiment
        from azureml.core.workspace import Workspace
        from azureml.train.automl import AutoMLConfig

        automated_ml_config = AutoMLConfig(task = 'regression',
                                 X = your_training_features,
                                 y = your_training_labels,
                                 iterations=30,
                                 iteration_timeout_minutes=5,
                                 primary_metric="spearman_correlation")

        ws = Workspace.from_config()
        experiment = Experiment(ws, "your-experiment-name")
        run = experiment.submit(automated_ml_config, show_output=True)


    :param task: 'classification', 'regression', or 'forecasting' depending on what kind of ML problem to solve.
    :type task: str or azureml.train.automl.constants.Tasks
    :param path: Full path to the Azure Machine Learning project folder.
    :type path: str
    :param iterations:
        Total number of different algorithm and parameter combinations
        to test during an Automated Machine Learning experiment.
    :type iterations: int
    :param data_script: File path to the user authored script containing get_data() function.
    :type data_script: str
    :param primary_metric:
        The metric that Automated Machine Learning will optimize for model selection.
        Automated Machine Learning collects more metrics
        than it can optimize. Please consult azureml.train.automl.constants.Metric.CLASSIFICATION_PRIMARY_SET for
        valid metrics for a classification task and azureml.train.automl.constants.Metric.REGRESSION_PRIMARY_SET for
        valid metrics for a regression task.
    :type primary_metric: str or azureml.train.automl.constants.Metric
    :param compute_target: The Azure Machine Learning compute target to run the
        Automated Machine Learning experiment on.
        See https://docs.microsoft.com/azure/machine-learning/service/how-to-auto-train-remote for more
        information on compute targets.
    :type compute_target: azureml.core.compute.AbstractComputeTarget
    :param spark_context: Spark context, only applicable when used inside Azure Databricks/Spark environment.
    :type spark_context: SparkContext
    :param X: The training features to use when fitting pipelines during an experiment.
    :type X: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param y: Training labels to use when fitting pipelines during an experiment.
        This is the value your model will predict.
    :type y: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param sample_weight:
        The weight to give to each training sample when running fitting pipelines,
        each row should correspond to a row in X and y data.
    :type sample_weight: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param X_valid: validation features to use when fitting pipelines during an experiment.
    :type X_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param y_valid: validation labels to use when fitting pipelines during an experiment.
    :type y_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param sample_weight_valid:
        The weight to give to each validation sample when running scoring pipelines,
        each row should correspond to a row in X and y data.
    :type sample_weight_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param cv_splits_indices:
        Indices where to split training data for cross validation.
        Each row is a separate cross fold and within each crossfold, provide 2 arrays, t
        he first with the indices for samples to use for training data and the second with the indices to
        use for validation data. i.e [[t1, v1], [t2, v2], ...] where t1 is the training indices for the first cross
        fold and v1 is the validation indices for the first cross fold.
    :type cv_splits_indices: numpy.ndarray
    :param validation_size:
        What percent of the data to hold out for validation when user validation data
        is not specified.
    :type validation_size: float
    :param n_cross_validations: How many cross validations to perform when user validation data is not specified.
    :type n_cross_validations: int
    :param y_min: Minimum value of y for a regression experiment.
    :type y_min: float
    :param y_max: Maximum value of y for a regression experiment.
    :type y_max: float
    :param num_classes: Number of classes in the label data for a classification experiment.
    :type num_classes: int
    :param preprocess:
        Flag whether Automated Machine Learning should preprocess your data for you such as handling missing data,
        text data and other common feature extraction. Note: If input data is Sparse you cannot
        use preprocess as True.
    :type preprocess: bool
    :param lag_length: How many rows of historical data to include when preprocessing time series data.
    :type lag_length: int
    :param max_cores_per_iteration: Maximum number of threads to use for a given training iteration.
    :type max_cores_per_iteration: int
    :param max_concurrent_iterations:
        Maximum number of iterations that would be executed in parallel.
        This should be less than the number of cores on the compute target.
    :type max_concurrent_iterations: int
    :param iteration_timeout_minutes:
        Maximum time in minutes that each iteration can run for before it terminates.
    :type iteration_timeout_minutes: int
    :param mem_in_mb: Maximum memory usage that each iteration can run for before it terminates.
    :type mem_in_mb: int
    :param enforce_time_on_windows:
        Flag to enforce time limit on model training at each iteration under windows.
        If running from a python script file (.py) please refer to the documentation for allowing resource limits
        on windows.
    :type enforce_time_on_windows: bool
    :param experiment_timeout_minutes:
        Maximum amount of time in minutes that all iterations combined can take before the
        experiment terminates.
    :type experiment_timeout_minutes: int
    :param experiment_exit_score:
        Target score for experiment. Experiment will terminate after this score is reached.
    :type experiment_exit_score: int
    :param blacklist_models: List of algorithms to ignore for an experiment.
    :type blacklist_models: list(str) or list(azureml.train.automl.constants.SupportedAlgorithms)
    :param exclude_nan_labels: Flag whether to exclude rows with NaN values in the label.
    :type exclude_nan_labels: bool
    :param auto_blacklist:
        Flag whether Automated Machine Learning should try to automatically exclude algorithms
        that it thinks won't perform well or may take a disproportionally long time to train.
    :type auto_blacklist: bool
    :param verbosity: Verbosity level for log file.
    :type verbosity: int
    :param enable_tf:  Flag to enable/disable Tensorflow algorithms
    :type enable_tf: bool
    :param enable_cache: Flag to enable/disable disk cache for transformed, preprocessed data.
    :type enable_cache: bool
    :param cost_mode: Flag to set cost prediction modes. COST_NONE stands for none cost prediction,
        COST_FILTER stands for cost prediction per iteration.
    :type cost_mode: int or automl.client.core.common.constants.PipelineCost
    :param whitelist_models: List of model names to search for an experiment.
    :type whitelist_models: list(str) or list(azureml.train.automl.constants.SupportedAlgorithms)
    """

    @experiment_method(submit_function=_automl_static_submit)
    def __init__(self,
                 task,
                 path=None,
                 iterations=100,
                 data_script=None,
                 primary_metric=None,
                 compute_target=None,
                 spark_context=None,
                 X=None,
                 y=None,
                 sample_weight=None,
                 X_valid=None,
                 y_valid=None,
                 sample_weight_valid=None,
                 cv_splits_indices=None,
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
                 enforce_time_on_windows=(os.name == 'nt'),
                 experiment_timeout_minutes=None,
                 experiment_exit_score=None,
                 blacklist_models=None,
                 auto_blacklist=True,
                 exclude_nan_labels=True,
                 verbosity=logging.INFO,
                 enable_tf=True,
                 enable_cache=True,
                 cost_mode=constants.PipelineCost.COST_NONE,
                 whitelist_models=None,
                 **kwargs):
        """
        Create an AutoMLConfig.

        :param task: 'classification', 'regression', or 'forecasting' depending on what kind of ML problem.
        :type task: str or azureml.train.automl.constants.Tasks
        :param path: Full path to the AzureML project folder.
        :type path: str
        :param iterations:
            Total number of different algorithm and parameter combinations
            to test during an AutoML experiment.
        :type iterations: int
        :param data_script: File path to the user authored script containing get_data() function.
        :type data_script: str
        :param primary_metric:
            The metric that AutoML will optimize for model selection. AutoML collects more metrics
            than it can optimize. Please consult azureml.train.automl.constants.Metric.CLASSIFICATION_PRIMARY_SET for
            valid metrics for a classification task and azureml.train.automl.constants.Metric.REGRESSION_PRIMARY_SET
            for valid metrics for a regression task.
        :type primary_metric: str or azureml.train.automl.constants.Metric
        :param compute_target: The AzureML compute to run the AutoML experiment on.
        :type compute_target: azureml.core.compute.AbstractComputeTarget
        :param spark_context: Spark context, only applicable when used inside azure databricks/spark environment.
        :type spark_context: SparkContext
        :param X: The training features to use when fitting pipelines during AutoML experiment.
        :type X: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param y: Training labels to use when fitting pipelines during AutoML experiment.
        :type y: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param sample_weight:
            The weight to give to each training sample when running fitting pipelines,
            each row should correspond to a row in X and y data.
        :type sample_weight: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param X_valid: validation features to use when fitting pipelines during AutoML experiment.
        :type X_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param y_valid: validation labels to use when fitting pipelines during AutoML experiment.
        :type y_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param sample_weight_valid:
            The weight to give to each validation sample when running scoring pipelines,
            each row should correspond to a row in X and y data.
        :type sample_weight_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param cv_splits_indices:
            Indices where to split training data for cross validation.
            Each row is a separate cross fold and within each crossfold, provide 2 arrays, t
            he first with the indices for samples to use for training data and the second with the indices to
            use for validation data. i.e [[t1, v1], [t2, v2], ...] where t1 is the training indices for the first cross
            fold and v1 is the validation indices for the first cross fold.
        :type cv_splits_indices: numpy.ndarray
        :param validation_size:
            What percent of the data to hold out for validation when user validation data
            is not specified.
        :type validation_size: float
        :param n_cross_validations: How many cross validations to perform when user validation data is not specified.
        :type n_cross_validations: int
        :param y_min: Minimum value of y for a regression experiment.
        :type y_min: float
        :param y_max: Maximum value of y for a regression experiment.
        :type y_max: float
        :param num_classes: Number of classes in the label data for a classification experiment.
        :type num_classes: int
        :param preprocess:
            Flag whether AutoML should preprocess your data for you such as handling missing data, text
            data and other common feature extraction. Note: If input data is Sparse you cannot use preprocess as True.
        :type preprocess: bool
        :param lag_length: How many rows of historical data to include when preprocessing time series data.
        :type lag_length: int
        :param max_cores_per_iteration: Maximum number of threads to use for a given training iteration.
        :type max_cores_per_iteration: int
        :param max_concurrent_iterations:
            Maximum number of iterations that would be executed in parallel.
            This should be less than the number of cores on the AzureML compute. Formerly concurrent_iterations.
        :type max_concurrent_iterations: int
        :param iteration_timeout_minutes:
            Maximum time in minutes that each iteration can run for before it terminates.
        :type iteration_timeout_minutes: int
        :param mem_in_mb: Maximum memory usage that each iteration can run for before it terminates.
        :type mem_in_mb: int
        :param enforce_time_on_windows:
            flag to enforce time limit on model training at each iteration under windows.
            If running from a python script file (.py) please refer to the documentation for allowing resource limits
            on windows.
        :type enforce_time_on_windows: bool
        :param experiment_timeout_minutes:
            Maximum amount of time in minutes that all iterations combined can take before the
            experiment terminates.
        :type experiment_timeout_minutes: int
        :param experiment_exit_score:
            Target score for experiment. Experiment will terminate after this score is reached.
        :type experiment_exit_score: int
        :param blacklist_models: List of algorithms to ignore for AutoML experiment.
        :type blacklist_models: list(str) or list(azureml.train.automl.constants.CustomerFacingSupportedModelNames)
        :param exclude_nan_labels: Flag whether to exclude rows with NaN values in the label.
        :type exclude_nan_labels: bool
        :param auto_blacklist:
            Flag whether AutoML should try to automatically exclude algorithms
            that it thinks won't perform well or may take a disproportionally long time to train.
        :type auto_blacklist: bool
        :param verbosity: Verbosity level for AutoML log file.
        :type verbosity: int
        :param enable_tf: Flag to enable/disable Tensorflow algorithms
        :type enable_tf: bool
        :param enable_cache: Flag to enable/disable disk cache for transformed, preprocessed data.
        :type enable_cache: bool
        :param cost_mode: Flag to set cost prediction modes. COST_NONE stands for none cost prediction,
            COST_FILTER stands for cost prediction per iteration.
        :type cost_mode: int or automl.client.core.common.constants.PipelineCost
        :param whitelist_models: List of model names to search for AutoML experiment
        :type list(str) or list(azureml.train.automl.constants.SupportedAlgorithms)
        """
        self.user_settings = {}
        self.fit_params = {}
        self._run_configuration = None
        self.is_timeseries = False
        blacklist_tf = []

        if task not in constants.Tasks.ALL:
            raise ValueError("Invalid Task: '{0}'. Supported Tasks: "
                             "{1}".format(task, constants.Tasks.ALL))
        if task == constants.Tasks.CLASSIFICATION:
            # set default metric if not set
            if primary_metric is None:
                primary_metric = constants.Metric.Accuracy
            if y_min is not None or y_max is not None:
                raise ValueError("Classification tasks do not use"
                                 "'y_min' or 'y_max'")
            if not self.user_settings.get('enable_tf'):
                blacklist_tf = [constants.SupportedAlgorithms.TensorFlowDNNClassifier,
                                constants.SupportedAlgorithms.TensorFlowLinearClassifier]
        else:
            if task == constants.Tasks.FORECASTING:
                self.is_timeseries = True
                task = constants.Tasks.REGRESSION
            if primary_metric is None:
                primary_metric = constants.Metric.NormRMSE
            if num_classes is not None:
                raise ValueError("Regression tasks do not use 'num_classes'")
            if not self.user_settings.get('enable_tf'):
                blacklist_tf = [constants.SupportedAlgorithms.TensorFlowDNNRegressor,
                                constants.SupportedAlgorithms.TensorFlowLinearRegressor]
        # disable tensorflow if module is not present or data is preprocessed outside tf.
        if enable_tf:
            if not AzureAutoMLClient._is_tensorflow_module_present():
                enable_tf = False
                logging.warning("tensorflow module is not installed")
            elif preprocess:
                enable_tf = False
                logging.info("tensorflow models are not supported with preprocess=True")

        if not AzureAutoMLClient._is_xgboost_module_present():
            xgb_algos = ["XGBoost", "XGBoostRegressor"]
            if blacklist_models is None:
                blacklist_models = xgb_algos
            else:
                blacklist_models.extend(xgb_algos)

        # validate white list elements are not in black list
        if (not enable_tf or blacklist_models is not None) and whitelist_models is not None:
            blacklist = []
            if not enable_tf:
                blacklist.extend(blacklist_tf)
            if blacklist_models is not None:
                blacklist.extend(blacklist_models)
            if len(blacklist) > 0 and set(whitelist_models).issubset(set(blacklist)):
                raise ValueError("Can not find models to train, all whitelisted models are also in blacklist")

        for key, value in kwargs.items():
            self.user_settings[key] = value

        self.user_settings['task_type'] = task
        self.user_settings["primary_metric"] = primary_metric
        self.user_settings["compute_target"] = compute_target
        self.user_settings['X'] = X
        self.user_settings['y'] = y
        self.user_settings['sample_weight'] = sample_weight
        self.user_settings['X_valid'] = X_valid
        self.user_settings['y_valid'] = y_valid
        self.user_settings['sample_weight_valid'] = sample_weight_valid
        self.user_settings['cv_splits_indices'] = cv_splits_indices
        self.user_settings["num_classes"] = num_classes
        self.user_settings["y_min"] = y_min
        self.user_settings["y_max"] = y_max
        self.user_settings["path"] = path
        self.user_settings["iterations"] = iterations
        self.user_settings["data_script"] = data_script
        self.user_settings["validation_size"] = validation_size
        self.user_settings["n_cross_validations"] = n_cross_validations
        self.user_settings["preprocess"] = preprocess
        self.user_settings["lag_length"] = lag_length
        self.user_settings["max_cores_per_iteration"] = max_cores_per_iteration
        self.user_settings["max_concurrent_iterations"] = max_concurrent_iterations
        self.user_settings["iteration_timeout_minutes"] = iteration_timeout_minutes
        self.user_settings["mem_in_mb"] = mem_in_mb
        self.user_settings["enforce_time_on_windows"] = enforce_time_on_windows
        self.user_settings["experiment_timeout_minutes"] = experiment_timeout_minutes
        self.user_settings["experiment_exit_score"] = experiment_exit_score
        self.user_settings["blacklist_models"] = blacklist_models
        self.user_settings["auto_blacklist"] = auto_blacklist
        self.user_settings["exclude_nan_labels"] = exclude_nan_labels
        self.user_settings["verbosity"] = verbosity
        self.user_settings["enable_tf"] = enable_tf
        self.user_settings["is_timeseries"] = self.is_timeseries
        self.user_settings["enable_cache"] = enable_cache
        self.user_settings["spark_context"] = spark_context
        self.user_settings["enable_subsampling"] = kwargs.get("enable_subsampling", False)
        self.user_settings["subsample_seed"] = kwargs.get("subsample_seed", None)

        # Deprecation of concurrent_iterations
        try:
            concurrent_iterations = kwargs.pop('concurrent_iterations')
            logging.warning("Parameter 'concurrent_iterations' will be deprecated. Use 'max_concurrent_iterations'")
            self.user_settings["max_concurrent_iterations"] = concurrent_iterations
        except KeyError:
            pass

        # Deprecation of max_time_sec
        try:
            max_time_sec = kwargs.pop('max_time_sec')
            logging.warning("Parameter 'max_time_sec' will be deprecated. Use 'iteration_timeout_minutes'")
            self.user_settings["iteration_timeout_minutes"] = math.ceil(max_time_sec / 60)
        except KeyError:
            pass

        # Deprecation of exit_time_sec
        try:
            exit_time_sec = kwargs.pop('exit_time_sec')
            logging.warning("Parameter 'exit_time_sec' will be deprecated. Use 'experiment_timeout_minutes'")
            self.user_settings["experiment_timeout_minutes"] = math.ceil(exit_time_sec / 60)
        except KeyError:
            pass

        # Deprecation of exit_score
        try:
            exit_score = kwargs.pop('exit_score')
            logging.warning("Parameter 'exit_score' will be deprecated. Use 'experiment_exit_score'")
            self.user_settings["experiment_exit_score"] = exit_score
        except KeyError:
            pass

        # Deprecation of blacklist_algos
        try:
            blacklist_algos = kwargs.pop('blacklist_algos')
            logging.warning("Parameter 'blacklist_algos' will be deprecated. Use 'blacklist_models'")
            self.user_settings["blacklist_algos"] = blacklist_algos
        except KeyError:
            pass

        self.user_settings["whitelist_models"] = whitelist_models
        self.user_settings["cost_mode"] = cost_mode

        self._run_configuration = self.user_settings.get('run_configuration', None)

    def _get_remove_fit_params(self):
        """
        Remove fit parameters from config.

        Inspects _AzureMLClient.fit() signature and builds a dictionary
        of args to be passed in from settings, using defauls as required
        and removes these params from settings

        :returns:
        """
        if not self.fit_params:
            fit_signature = inspect.signature(AzureAutoMLClient.fit)
            for k, v in fit_signature.parameters.items():
                # skip parameters
                if k in ['self', 'run_configuration', 'data_script', 'show_output']:
                    continue

                default_val = v.default

                # Parameter.empty is returned for any parameters without a default
                # we will require these in settings
                if default_val is inspect.Parameter.empty:
                    try:
                        self.fit_params[k] = self.user_settings.pop(k)
                    except KeyError:
                        raise ValueError("To submit an experiment you will need"
                                         " to provide a value for '{0}'".format(k))
                else:
                    self.fit_params[k] = self.user_settings.pop(k, default_val)

        # overwrite default run_config with user provided or None
        self.fit_params['run_configuration'] = self._run_configuration

    def _validate_config_settings(self):
        """Validate the configuration attributes."""
        # assert we have a run_config, if not create default
        # and assume default config
        if self._run_configuration is None:
            if 'run_configuration' not in self.user_settings.keys():
                self._run_configuration = RunConfiguration()
                self._run_configuration.auto_prepare_environment = True
            elif isinstance(self.user_settings['run_configuration'], str):
                path = self.user_settings.get('path', '.')
                self._run_configuration = RunConfiguration.load(path=path,
                                                                name=self.user_settings['run_configuration'])
            else:
                self._run_configuration = self.user_settings['run_configuration']

        # ensure compute target is set
        if 'compute_target' in self.user_settings and self.user_settings['compute_target'] is not None:
            self._run_configuration.target = self.user_settings['compute_target']
            if self.user_settings['compute_target'] != 'local' and \
                    self.user_settings['compute_target'].type == constants.ComputeTargets.AMLCOMPUTE:
                self._run_configuration.environment.docker.enabled = True
        else:
            self.user_settings['compute_target'] = self._run_configuration.target
        # remove compute target from setting
        self.user_settings.pop('run_configuration', None)

        # validate data for remote
        settings = self.user_settings
        if settings['compute_target'] != 'local':
            data_script_provided = 'data_script' in settings.keys()

            def are_dataflows_valid():
                for key in ['X', 'y', 'sample_weight', 'X_valid', 'y_valid', 'sample_weight_valid']:
                    if key not in settings.keys():
                        continue
                    value = settings[key]
                    if value is not None and not _dataprep_utilities.is_dataflow(value):
                        return False
                if 'cv_splits_indices' in settings.keys():
                    cv_splits_indices = settings['cv_splits_indices']
                    if not isinstance(cv_splits_indices, list):
                        return False
                    for split in cv_splits_indices:
                        if not _dataprep_utilities.is_dataflow(split):
                            return False
                return True

            if not data_script_provided and not are_dataflows_valid():
                raise ValueError("You must provide a 'data_script'"
                                 " or provide data with `azureml.dataprep.Dataflow` "
                                 " to create a remote run")
