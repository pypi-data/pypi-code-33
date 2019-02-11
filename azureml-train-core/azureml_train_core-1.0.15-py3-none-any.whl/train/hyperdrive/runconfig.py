# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The HyperDriveRunConfig module defines the allowed configuration options for a HyperDrive experiment."""
import os
import yaml
import copy
import warnings
import uuid

from azureml.train.hyperdrive._search import MAX_DURATION_MINUTES, search
from azureml.train.hyperdrive.policy import NoTerminationPolicy
from azureml.train.hyperdrive.sampling import BayesianParameterSampling
from azureml.train.estimator import MMLBaseEstimatorRunConfig

from azureml._base_sdk_common.common import AML_CONFIG_DIR, COMPUTECONTEXT_EXTENSION
from azureml._base_sdk_common.service_discovery import get_service_url
from azureml._base_sdk_common.project_context import create_project_context
from azureml.core._experiment_method import experiment_method
from azureml._execution._commands import _serialize_run_config_to_dict
from azureml.exceptions import UserErrorException
from azureml.core.compute_target import AbstractComputeTarget

HYPERDRIVE_URL_SUFFIX = "/hyperdrive/v1.0"


class HyperDriveRunConfig(object):
    """Configuration that defines a HyperDrive run.

    This includes information about parameter space sampling, termination policy,
    primary metric, estimator and the compute target to execute the experiment runs on.

    :param estimator: An estimator that will be called with sampled hyper parameters.
    :type estimator: azureml.train.estimator.MMLBaseEstimator
    :param hyperparameter_sampling: The hyperparameter sampling space.
    :type hyperparameter_sampling: azureml.train.hyperdrive.HyperParameterSampling
    :param policy: The early termination policy to use. If None - the default,
                   no early termination policy will be used.
                   The MedianTerminationPolicy with delay_evaluation of 5
                   is a good termination policy to start with. These are conservative settings,
                   that can provide 25%-35% savings with no loss on primary metric (based on our evaluation data).
    :type policy: azureml.train.hyperdrive.EarlyTerminationPolicy
    :param primary_metric_name: The name of the primary metric reported by the experiment runs.
    :type primary_metric_name: str
    :param primary_metric_goal: One of maximize / minimize.
                                It determines if the primary metric has to be
                                minimized/maximized in the experiment runs' evaluation.
    :type primary_metric_goal: azureml.train.hyperdrive.PrimaryMetricGoal
    :param max_total_runs: Maximum number of runs. This is the upper bound; there may
                           be fewer runs when the sample space is smaller than this value.
    :type max_total_runs: int
    :param max_concurrent_runs: Maximum number of runs to run concurrently. If None, all runs are launched in parallel.
    :type max_concurrent_runs: int
    :param max_duration_minutes: Maximum duration of the run. Once this time is exceeded, the run is cancelled.
    :type max_duration_minutes: int
    """

    _PLATFORM = "AML"

    @experiment_method(submit_function=search)
    def __init__(self,
                 estimator,
                 hyperparameter_sampling,
                 primary_metric_name, primary_metric_goal,
                 max_total_runs,
                 max_concurrent_runs=None,
                 max_duration_minutes=MAX_DURATION_MINUTES,
                 policy=None
                 ):
        """Initialize the HyperDriveRunConfig.

        :param estimator: An estimator that will be called with sampled hyper parameters.
        :type estimator: azureml.train.estimator.MMLBaseEstimator
        :param hyperparameter_sampling: Hyperparameter space sampling definition.
        :type hyperparameter_sampling: azureml.train.hyperdrive.HyperParameterSampling
        :param primary_metric_name: The name of the primary metric reported by the experiment runs.
        :type primary_metric_name: str
        :param primary_metric_goal: One of maximize / minimize.
                                    It determines if the primary metric has to be
                                    minimized/maximized in the experiment runs evaluation.
        :type primary_metric_goal: azureml.train.hyperdrive.PrimaryMetricGoal
        :param max_total_runs: Maximum number of runs. This is the upper bound - we may
                               have less for instance when the space samples is less than this value.
        :type max_total_runs: int
        :param max_concurrent_runs: Maximum number of runs to run concurrently. If None, launch all runs in parallel.
        :type max_concurrent_runs: int
        :param max_duration_minutes: Max duration of the run. After this time, the experiment is cancelled.
        :type max_duration_minutes: int
        :param policy: The early termination policy to use. If None - the default,
                       no early termination policy will be used.
                       The MedianTerminationPolicy with delay_evaluation of 5
                       is a good termination policy to start with. These are conservative settings,
                       that can provide 25%-35% savings with no loss on primary metric (based on our evaluation data).
        :type policy: azureml.train.hyperdrive.EarlyTerminationPolicy
        """
        self._estimator = estimator
        self._compute_target = estimator._compute_target

        if isinstance(hyperparameter_sampling, BayesianParameterSampling) and policy is not None:
            raise UserErrorException("No early termination policy is currently supported with Bayesian sampling.")

        if policy is None:
            policy = NoTerminationPolicy()

        self._policy_config = policy.to_json()
        self._generator_config = hyperparameter_sampling.to_json()
        self._primary_metric_config = {
            'name': primary_metric_name,
            'goal': primary_metric_goal.name.lower()}
        self._max_total_runs = max_total_runs
        self._max_concurrent_runs = max_concurrent_runs or max_total_runs
        self._max_duration_minutes = max_duration_minutes
        self._platform = self._PLATFORM
        self._host_url = None

    @property
    def estimator(self):
        """Return the estimator in this config.

        :return: The estimator.
        :rtype: azureml.train.estimator.Estimator
        """
        return self._estimator

    def _get_host_url(self, workspace, run_name):
        """Return the host url for the HyperDrive service.

        :param workspace: The workspace.
        :type workspace: azureml.core.workspace.Workspace
        :param run_name: The name of the run.
        :type run_name: str
        :return: The host url for HyperDrive service.
        :rtype: str
        """
        if not self._host_url:
            service_url = self._get_service_address("hyperdrive", workspace, run_name)
            self._host_url = service_url + HYPERDRIVE_URL_SUFFIX
        return self._host_url

    def _get_project_context(self, workspace, run_name):
        project_context = create_project_context(auth=workspace._auth_object,
                                                 subscription_id=workspace.subscription_id,
                                                 resource_group=workspace.resource_group,
                                                 workspace_name=workspace.name,
                                                 project_name=run_name,
                                                 workspace_id=workspace._workspace_id)
        return project_context

    def _get_service_address(self, service, workspace, run_name):
        project_context = self._get_project_context(workspace, run_name)
        service_address = get_service_url(project_context.get_auth(),
                                          project_context.get_workspace_uri_path(),
                                          workspace._workspace_id,
                                          service_name=service)
        return service_address

    def _get_platform_config(self, workspace, run_name):
        """Return `dict` containing platform config definition.

        Platform config contains the AML config information about the execution service.
        """
        project_context = self._get_project_context(workspace, run_name)
        service_address = self._get_service_address("experimentation", workspace, run_name)

        target_details = None
        if isinstance(self._compute_target, AbstractComputeTarget):
            # Compute target object has raw password information.
            # Encrypted target password is saved in the .compute file.
            # Deserialize from compute target file.
            compute_target_path = os.path.join(self.estimator.source_directory, AML_CONFIG_DIR,
                                               self._compute_target.name + COMPUTECONTEXT_EXTENSION)
            if not os.path.isfile(compute_target_path):
                raise UserErrorException("Compute target = {} doesn't exist at {}. Attach target to the project"
                                         .format(self._compute_target.name, compute_target_path))

            with open(compute_target_path, "r") as compute_target_file:
                target_details = yaml.load(compute_target_file)

        run_config = self._remove_duplicate_estimator_arguments()
        if run_config.target == "amlcompute":
            self._set_amlcompute_runconfig_properties(run_config)

        return \
            {
                "ServiceAddress": service_address,
                # FIXME: remove this fix once hyperdrive code updates ES URL creation
                # project_context.get_experiment_uri_path() gives /subscriptionid/id_value
                # where as hyperdrive expects subscriptionid/id_value
                # "ServiceArmScope": project_context.get_experiment_uri_path(),
                "ServiceArmScope": project_context.get_experiment_uri_path()[1:],
                "SubscriptionId": workspace.subscription_id,
                "ResourceGroupName": workspace.resource_group,
                "WorkspaceName": workspace.name,
                "ExperimentName": run_name,
                "Definition": {
                    "Overrides": _serialize_run_config_to_dict(run_config),
                    "TargetDetails": target_details
                }
            }

    def _remove_duplicate_estimator_arguments(self):
        """Remove duplicate estimator arguments.

        If HyperDrive parameter space definition has the same script parameter as the estimator,
        remove the script parameter from the estimator. If both have the same parameter, HyperDrive
        parameter space will take precedence over the estimator script parameters.
        """
        warning = False
        run_config_copy = copy.deepcopy(self._estimator.run_config)
        estimator_args_dict = self.estimator._estimator_config._script_params
        input_params = copy.deepcopy(estimator_args_dict).keys() if estimator_args_dict else []
        parameter_space = [item.lstrip("-") for item in self._generator_config["parameter_space"].keys()]
        duplicate_params = []

        for param in input_params:
            # Add lstrip: The estimator script param input expects the -- to be specified for script_params.
            # In HyperDrive, parameter space, user doesn't specify hyphens in the beginning of the parameter.
            if param.lstrip("-") in parameter_space:
                estimator_args_dict.pop(param)
                warning = True
                duplicate_params.append(param)
        if warning:
            warnings.formatwarning = _simple_warning
            warnings.warn("The same input parameter(s) are specified in estimator script params "
                          "and HyperDrive parameter space. HyperDrive parameter space definition will override "
                          "duplicate entries in estimator. "
                          "{} is the list of overridden parameter(s).".format(duplicate_params))
            run_config_copy.arguments = MMLBaseEstimatorRunConfig._get_arguments(estimator_args_dict)

        return run_config_copy

    def _set_amlcompute_runconfig_properties(self, run_config):
        # A new amlcompute cluster with this name will be created for this HyperDrive run.
        run_config.amlcompute._name = str(uuid.uuid4())
        # All the child runs will use the same cluster.
        # HyperDrive service will delete the cluster once the parent run reaches a terminal state.
        run_config.amlcompute._retain_cluster = True
        run_config.amlcompute._cluster_max_node_count = run_config.node_count * self._max_concurrent_runs
        warnings.formatwarning = _simple_warning
        warnings.warn("A AML compute with {} node count will be created for this HyperDriveRun. "
                      "Please consider modifying max_concurrent_runs if this will exceed the "
                      "quota on the Azure subscription.".format(run_config.amlcompute._cluster_max_node_count))


def _simple_warning(message, category, filename, lineno, file=None, line=None):
    """Override detailed stack trace warning with just the message."""
    return str(message) + '\n'
