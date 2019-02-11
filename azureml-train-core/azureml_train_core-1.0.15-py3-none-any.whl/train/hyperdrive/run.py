# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The HyperDrive Run object."""
import enum

from azureml.core import Run, ScriptRun
from azureml.exceptions import TrainingException
# noinspection PyProtectedMember
from azureml._base_sdk_common.service_discovery import get_service_url
# noinspection PyProtectedMember
from azureml._restclient.run_client import RunClient

import azureml.train.restclients.hyperdrive as HyperDriveClient
from azureml.train.restclients.hyperdrive.rest import ApiException


class PrimaryMetricGoal(enum.Enum):
    """The supported metric goals.

    A metric goal is used to determine whether a higher value for a metric is better or worse. This is used when
    comparing runs based on the primary metric. For example, you may want to maximize accuracy or minimize error.
    """

    MAXIMIZE = "MAXIMIZE"
    MINIMIZE = "MINIMIZE"


class HyperDriveRun(ScriptRun):
    """HyperDriveRun contains the details of a submitted HyperDrive experiment.

    This class can be used to manage, check status, and retrieve run details for the HyperDrive run and each of
    the generated child runs.

    :param experiment: The Experiment for the HyperDrive run.
    :type experiment: azureml.core.experiment.Experiment
    :param run_id: The HyperDrive run id.
    :type run_id: str
    :param run_config: The RunConfiguration used by the estimator in HyperDriveRunConfig.
    :type run_config: azureml.core.runconfig.RunConfiguration
    :param hyperdrive_run_config: A `HyperDriveRunConfig` that defines the configuration for this HyperDrive run.
    :type hyperdrive_run_config: azureml.train.hyperdrive.HyperDriveRunConfig

    """

    def __init__(self, experiment, run_id, hyperdrive_run_config, run_config=None):
        """Initialize a HyperDrive run.

        :param experiment: The Experiment for the HyperDrive run.
        :type experiment: azureml.core.experiment.Experiment
        :param run_id: The Hyperdrive run id.
        :type run_id: str
        :param run_config: The RunConfiguration used by the estimator in HyperDriveRunConfig.
        :type run_config: azureml.core.runconfig.RunConfiguration
        :param hyperdrive_run_config: A `HyperDriveRunConfig` that defines the configuration for this HyperDrive run.
        :type hyperdrive_run_config: azureml.train.hyperdrive.HyperDriveRunConfig
        """
        if not isinstance(run_id, str):
            raise TypeError("RunId must be a string")

        HYPER_DRIVE_RUN_USER_AGENT = "sdk_run_hyper_drive"
        self.run_client = RunClient.create(workspace=experiment.workspace, experiment_name=experiment.name,
                                           run_id=run_id, user_agent=HYPER_DRIVE_RUN_USER_AGENT)
        super().__init__(experiment=experiment, run_id=run_id,
                         directory=hyperdrive_run_config.estimator.source_directory, _run_config=run_config,
                         _user_agent=HYPER_DRIVE_RUN_USER_AGENT)
        self._hyperdrive_run_config = hyperdrive_run_config

    @property
    def hyperdrive_run_config(self):
        """Return the hyperdrive run config.

        :return: The hyperdrive run config.
        :rtype: azureml.train.hyperdrive.HyperDriveRunConfig
        """
        return self._hyperdrive_run_config

    def cancel(self):
        """Return True if the HyperDrive run was cancelled successfully.

        :return: Whether or not the run was cancelled successfully.
        :rtype: bool
        """
        project_context = self.hyperdrive_run_config._get_project_context(self.experiment.workspace,
                                                                          self.experiment.name)
        project_auth = self.experiment.workspace._auth_object
        run_history_host = get_service_url(project_auth, project_context.get_workspace_uri_path(),
                                           self.experiment.workspace._workspace_id)

        HyperDriveClient.configuration.host = self.hyperdrive_run_config._get_host_url(self.experiment.workspace,
                                                                                       self.experiment.name)
        api_instance = HyperDriveClient.ExperimentApi()

        try:
            # FIXME: remove this fix once hyperdrive code updates ES URL creation
            # project_context.get_experiment_uri_path() gives /subscriptionid/id_value
            # where as hyperdrive expects subscriptionid/id_value
            # project_context.get_experiment_uri_path()
            experiment_uri_path = project_context.get_experiment_uri_path()[1:]
            cancel_hyperdrive_run_result = api_instance.cancel_experiment(experiment_uri_path,
                                                                          self._run_id,
                                                                          project_auth.get_authentication_header()
                                                                          ["Authorization"],
                                                                          run_history_host)
            return cancel_hyperdrive_run_result
        except ApiException as e:
            raise TrainingException("Exception occurred while cancelling HyperDrive run. {}".format(str(e)),
                                    inner_exception=e) from None

    def get_best_run_by_primary_metric(self):
        """Find and return the Run instance that corresponds to the best performing run amongst all the completed runs.

        The best performing run is identified solely based on the primary metric parameter specified in the
        HyperDriveRunConfig. The PrimaryMetricGoal governs whether the minimum or maximum of the primary metric is
        used. To do a more detailed analysis of all the ExperimentRun metrics launched by this HyperDriveRun, use
        get_metrics. If all of the Runs launched by this HyperDrive run reached the same best metric, only one of the
        runs is returned.

        It ignores any run that is cancelled by HyperDrive or failed due to error.

        :return: The best Run.
        :rtype: azureml.core.run.Run
        """
        best_run_id = self._get_best_run_id_by_primary_metric()
        if best_run_id:
            return Run(self.experiment,
                       best_run_id)
        else:
            raise TrainingException("None of the ExperimentRuns launched by this HyperDrive run have logged the "
                                    "primary metric yet.")

    def _get_best_run_id_by_primary_metric(self):
        """Return the run id of the instance that corresponds to the best performing child run.

        It ignores any run that is cancelled by HyperDrive or failed due to error.

        :return: id of best Run.
        :rtype: str
        """
        run_metrics = self.get_metrics()
        # If none of the child runs has logged metrics, no metrics will be logged in History.
        if not run_metrics:
            raise TrainingException("No metrics have been logged for the ExperimentRuns launched by "
                                    "this HyperDriveRun.")
        metric_name = self.hyperdrive_run_config._primary_metric_config["name"]
        metric_goal = self.hyperdrive_run_config._primary_metric_config["goal"]
        metric_func = max if metric_goal == PrimaryMetricGoal.MAXIMIZE.value.lower() else min

        child_run_ids = [run.id for run in self.get_children()
                         if run.id in run_metrics and run.get_status() not in ["Failed", "Canceled"]]
        child_run_metrics = [run_metrics[run_id] for run_id in child_run_ids]
        child_run_metrics_by_metric_name = [run_metric[metric_name] for run_metric in child_run_metrics if (
                                            run_metric and metric_name in run_metric)]
        best_child_run_metrics = [metric_func(metrics) if isinstance(metrics, list) else metrics for metrics in
                                  child_run_metrics_by_metric_name]
        best_run_metrics = {run_id: metrics for (run_id, metrics) in zip(child_run_ids, best_child_run_metrics)}

        if best_run_metrics:
            best_run_id = metric_func(best_run_metrics, key=lambda k: best_run_metrics.get(k))
            return best_run_id
        else:
            return None

    def get_metrics(self):
        """Return the metrics from all the runs that were launched by this HyperDriveRun.

        :return: The metrics for all the children of this run.
        :rtype: dict
        """
        child_run_ids = [run.id for run in self.get_children()]
        # noinspection PyProtectedMember
        return self.run_client._get_metrics_by_run_ids(child_run_ids)

    # get_diagnostics looks for a zip in AFS based on run_id.
    # For HyperDrive runs, there is no entry in AFS.
    def get_diagnostics(self):
        """Do not use. The get_diagnostics method is not supported for the HyperDriveRun subclass."""
        raise NotImplementedError("Get diagnostics is unsupported for HyperDrive run.")

    def fail(self):
        """Do not use. The fail method is not supported for the HyperDriveRun subclass."""
        raise NotImplementedError("Fail is unsupported for HyperDrive run.")
