# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The search function."""
import json
import tempfile
import os
import uuid

from azureml._base_sdk_common import _ClientSessionId
from azureml._base_sdk_common.create_snapshot import create_snapshot
from azureml.core import Experiment

from azureml.train.hyperdrive.run import HyperDriveRun
from azureml.exceptions import TrainingException

import azureml.train.restclients.hyperdrive as HyperDriveClient
from azureml.train.restclients.hyperdrive.rest import ApiException
from azureml.train._telemetry_logger import _TelemetryLogger

# after this max duration the HyperDrive run is cancelled.
MAX_DURATION_MINUTES = 10080


def _create_experiment_dto(hyperdrive_run_config, workspace, experiment_name,
                           telemetry_values=None, activity_logger=None):
    estimator = hyperdrive_run_config.estimator
    user_email = "nobody@example.com"

    if activity_logger is not None:
        activity_logger.info("Creating snapshot...")

    snapshot_id = create_snapshot(estimator.source_directory, hyperdrive_run_config.
                                  _get_project_context(workspace=workspace, run_name=experiment_name))

    if activity_logger is not None:
        activity_logger.info("Snapshot was created. SnapshotId=%s", snapshot_id)

    # collect client side telemetry
    platform_config = hyperdrive_run_config._get_platform_config(workspace, experiment_name)
    platform_config['Definition']['SnapshotId'] = snapshot_id

    if telemetry_values is not None:
        platform_config['Definition']['TelemetryValues'] = telemetry_values

    # TODO: once CreateExperimentDto() supports taking run config inputs, change this
    return HyperDriveClient.CreateExperimentDto(generator_config=hyperdrive_run_config._generator_config,
                                                max_concurrent_jobs=hyperdrive_run_config.
                                                _max_concurrent_runs,
                                                max_total_jobs=hyperdrive_run_config._max_total_runs,
                                                max_duration_minutes=hyperdrive_run_config.
                                                _max_duration_minutes,
                                                platform=hyperdrive_run_config._platform,
                                                platform_config=platform_config,
                                                policy_config=hyperdrive_run_config._policy_config,
                                                primary_metric_config=hyperdrive_run_config.
                                                _primary_metric_config,
                                                user=user_email, name=experiment_name)


def search(hyperdrive_run_config, workspace, experiment_name):
    """Launch a HyperDrive run on the given configs.

    :param hyperdrive_run_config: A `HyperDriveRunConfig` that defines the configuration for this HyperDrive run.
    :type hyperdrive_run_config: azureml.train.hyperdrive.HyperDriveRunConfig
    :param workspace: The workspace in which to run the experiment.
    :type workspace: azureml.core.workspace.Workspace
    :param experiment_name: Name of the experiment
    :type experiment_name: str
    :returns: A `HyperDriveRun` object that has the launched run id.
    :rtype: azureml.train.hyperdrive.HyperDriveRun
    :raises: ExperimentExecutionException: If the HyperDrive run is not launched successfully.
    """
    logger = _TelemetryLogger.get_telemetry_logger(__name__)
    telemetry_values = _get_telemetry_values(hyperdrive_run_config, workspace)
    with _TelemetryLogger.log_activity(logger,
                                       "train.hyperdrive.submit",
                                       custom_dimensions=telemetry_values) as activity_logger:

        auth_header = workspace._auth_object.get_authentication_header()

        HyperDriveClient.configuration.host = hyperdrive_run_config._get_host_url(workspace=workspace,
                                                                                  run_name=experiment_name)
        api_instance = HyperDriveClient.ExperimentApi()

        experiment_dto = _create_experiment_dto(hyperdrive_run_config, workspace, experiment_name,
                                                telemetry_values, activity_logger)

        try:
            with tempfile.TemporaryDirectory() as temporary_config:
                activity_logger.info("Write config.json to temporary folder.")
                config_path = os.path.join(temporary_config, "config.json")
                with open(config_path, 'w') as config_f:
                    json.dump(experiment_dto.to_dict(), config_f)

                activity_logger.info("Submitting HyperDrive experiment...")
                api_response = api_instance.create_experiment(experiment_dto.platform_config["ServiceArmScope"],
                                                              config_path,
                                                              auth_header['Authorization'])

                parent_run_id = api_response.result.platform_config["ParentRunId"]
                activity_logger.info("Experiment was submitted. ParentRunId=%s", parent_run_id)

                experiment = Experiment(workspace, experiment_name)
                return HyperDriveRun(experiment=experiment,
                                     hyperdrive_run_config=hyperdrive_run_config,
                                     run_id=parent_run_id,
                                     run_config=hyperdrive_run_config.estimator.run_config)

        except ApiException as e:
            raise TrainingException("Exception occurred while creating the "
                                    "HyperDrive run {}".format(str(e)), inner_exception=e) from None


def _get_telemetry_values(config, workspace):
    telemetry_values = {}

    # client common...
    telemetry_values['amlClientType'] = 'azureml-sdk-train'
    telemetry_values['amlClientModule'] = __name__
    telemetry_values['amlClientFunction'] = search.__name__
    try:
        from azureml._base_sdk_common.common import fetch_tenantid_from_aad_token
        telemetry_values['tenantId'] = fetch_tenantid_from_aad_token(workspace._auth_object._get_arm_token())
    except Exception as e:
        telemetry_values['tenantId'] = "Error retrieving tenant id: {}".format(e)

    # Used for correlating hyperdrive runs submitted to execution service
    telemetry_values['amlClientRequestId'] = str(uuid.uuid4())
    telemetry_values['amlClientSessionId'] = _ClientSessionId

    # hyperdrive related...
    telemetry_values['subscriptionId'] = workspace.subscription_id
    telemetry_values['estimator'] = config.estimator.__class__.__name__
    telemetry_values['samplingMethod'] = config._generator_config['name']
    telemetry_values['terminationPolicy'] = config._policy_config['name']
    telemetry_values['primaryMetricGoal'] = config._primary_metric_config['goal']
    telemetry_values['maxTotalRuns'] = config._max_total_runs
    telemetry_values['maxConcurrentRuns'] = config._max_concurrent_runs
    telemetry_values['maxDurationMinutes'] = config._max_duration_minutes
    telemetry_values['computeTarget'] = config._compute_target if isinstance(config._compute_target, str) else \
        config._compute_target.type if config._compute_target else "amlcompute"
    telemetry_values['vmSize'] = config.estimator.run_config.amlcompute.vm_size if \
        config.estimator.run_config.amlcompute else None

    return telemetry_values
