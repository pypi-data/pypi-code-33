# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=line-too-long
from __future__ import print_function

import collections
import json
import os
import shutil
import subprocess
import time
import urllib3
import zipfile
import uuid
from multiprocessing.dummy import Pool
import yaml
import sys
import platform
import requests


from azureml._base_sdk_common import _ClientSessionId
from azureml._base_sdk_common.user_agent import get_user_agent
from azureml._base_sdk_common.common import CLICommandOutput, get_project_files
from azureml._base_sdk_common.common import normalize_windows_paths, give_warning
from azureml._base_sdk_common.common import RUNCONFIGURATION_EXTENSION, COMPUTECONTEXT_EXTENSION
from azureml._base_sdk_common.execution_service_address import ExecutionServiceAddress
from azureml._base_sdk_common.process_utilities import start_background_process
from azureml._base_sdk_common.create_snapshot import create_snapshot
from azureml._base_sdk_common.project_context import create_project_context
from azureml._base_sdk_common.utils import create_session_with_retry, get_directory_size
from azureml.exceptions import ExperimentExecutionException, UserErrorException
from azureml.core.runconfig import RunConfiguration
from azureml.core.experiment import Experiment
from azureml._project.ignore_file import get_project_ignore_file
from azureml._restclient.run_client import RunClient
from azureml._restclient.models.create_run_dto import CreateRunDto

from backports import tempfile as temp_dir_back

_one_mb = 1024 * 1024
_num_max_mbs = 25
_max_zip_size_bytes = _num_max_mbs * _one_mb


def prepare_compute_target(project_object, run_config_object, check=False, run_id=None):
    """
    API to prepare a target for an experiment run.
    :param project_object: The project object.
    :type project_object: azureml.core.project.Project
    :param run_config_object: The run configuration object.
    :type run_config_object: azureml.core.runconfig.RunConfiguration
    :param check: True if it is only a prepare check operation, which will not do an actual prepare.
    :type check: bool
    :param run_id: A user specified run id.
    :type run_id: str
    :return: A run object except in only prepare check operation.
    :rtype: azureml.core.script_run.ScriptRun or bool in case of check=True
    """

    setup = _setup_run(project_object, run_config_object, prepare_only=True)

    custom_target_dict = setup.custom_target_dict

    if _is_local_target(run_config_object.target, custom_target_dict):
        if (check):
            raise ExperimentExecutionException("Can not check preparation of local targets")
        return _start_internal_local_cloud(project_object, run_config_object,
                                           prepare_only=True,
                                           custom_target_dict=custom_target_dict,
                                           run_id=run_id)
    else:
        return _start_internal(project_object, run_config_object, prepare_only=True,
                               prepare_check=check, custom_target_dict=custom_target_dict,
                               run_id=run_id)


# TODO - Delete injected files and all its references once automl moves to using the actual API.
def start_run(project_object, run_config_object,
              run_id=None, injected_files=None, telemetry_values=None):
    """
    Start an experiment run for a project.
    Returns a run object.
    :param project_object: Project object.
    :type project_object: azureml.core.project.Project
    :param run_config_object: The run configuration object.
    :type run_config_object: azureml.core.runconfig.RunConfiguration
    :param run_id: A users specified run id.
    :type run_id: str
    :param injected_files:
    :type injected_files: dict
    :param telemetry_values: Telemetry property bag.
    :type telemetry_values: dict
    :return: A run object.
    :rtype: azureml.core.script_run.ScriptRun
    """

    setup = _setup_run(project_object, run_config_object, injected_files=injected_files)
    custom_target_dict = setup.custom_target_dict

    # Collect common telemetry information for client side.
    telemetry_values = _get_telemetry_values(telemetry_values)

    """Submits an experiment."""
    if _is_local_target(run_config_object.target, custom_target_dict):
        return _start_internal_local_cloud(project_object,
                                           run_config_object,
                                           custom_target_dict=custom_target_dict,
                                           run_id=run_id, injected_files=injected_files,
                                           telemetry_values=telemetry_values)
    else:
        return _start_internal(project_object, run_config_object,
                               custom_target_dict=custom_target_dict, run_id=run_id,
                               injected_files=injected_files,
                               telemetry_values=telemetry_values)


def _setup_run(project_object, run_config_object, prepare_only=None, injected_files=None):
    """
    Setup run
    :param project_object: Project object.
    :type project_object: azureml.core.project.Project
    :param run_config_object: The run configuration object.
    :type run_config_object: azureml.core.runconfig.RunConfiguration
    :param prepare_only: prepare_only=True for only prepare operation.
    :type prepare_only: bool
    :param injected_files:
    :type injected_files: dict
    :return:
    """
    configuration_path = _get_configuration_path(project_object, run_config_object._name,
                                                 config_type=RUNCONFIGURATION_EXTENSION)
    configuration_path = normalize_windows_paths(configuration_path)

    target = run_config_object.target

    if not target:
        raise ExperimentExecutionException("Must specify a target either through run configuration or arguments.")

    if target == "amlcompute" and run_config_object.amlcompute.vm_size is None:
        raise ExperimentExecutionException("Must specify VM size for the compute target to be created.")

    custom_target_dict = _get_custom_target_dict(project_object, target)

    if not prepare_only and not injected_files:
        if not run_config_object.script:
            raise ExperimentExecutionException("Must specify a file to run.")

        full_script_path = os.path.normpath(os.path.join(project_object.project_directory, run_config_object.script))
        if os.path.isfile(full_script_path):
            run_config_object.script = normalize_windows_paths(os.path.relpath(full_script_path,
                                                                               project_object.project_directory))
        else:
            raise ExperimentExecutionException("{} script path doesn't exist. "
                                               "The script should be inside the project "
                                               "folder".format(full_script_path))

    setup = collections.namedtuple("setup", ['custom_target_dict', 'configuration_path'])
    return setup(custom_target_dict=custom_target_dict, configuration_path=configuration_path)


def _serialize_run_config_to_dict(run_config_object):
    result = RunConfiguration._serialize_to_dict(run_config_object)

    # Inline the Conda dependencies to the runconfig for job submission.
    # This means that changes SDK users made to the in-memory dependencies definition
    # will be respected without needing to save the definition to a temporary file.
    inline = run_config_object.environment.python.conda_dependencies._conda_dependencies
    result["environment"]["python"]["condaDependencies"] = inline
    del result["environment"]["python"]["condaDependenciesFile"]

    return result


def _start_internal_local_cloud(project_object, run_config_object,
                                prepare_only=False, custom_target_dict=None, run_id=None,
                                injected_files=None, telemetry_values=None):
    """
    :param project_object: Project object
    :type project_object: azureml.core.project.Project
    :param run_config_object: The run configuration object.
    :type run_config_object: azureml.core.runconfig.RunConfiguration
    :param prepare_only:
    :param custom_target_dict:
    :param run_id:
    :param injected_files:
    :type injected_files: dict
    :return: azureml.core.script_run.ScriptRun
    """
    project_context = create_project_context(project_object.workspace_object._auth_object,
                                             project_object.workspace_object.subscription_id,
                                             project_object.workspace_object.resource_group,
                                             project_object.workspace_object.name,
                                             project_object.history.name,
                                             project_object.workspace_object._workspace_id)
    addr = project_context.get_cloud_execution_service_address()
    execution_service_details = ExecutionServiceAddress(addr)
    service_address = execution_service_details.address
    service_arm_scope = project_context.get_experiment_uri_path()
    auth_header = project_object.workspace_object._auth_object.get_authentication_header()
    thread_pool = Pool(1)

    snapshot_async = None
    if run_config_object.history.snapshot_project:
        snapshot_async = thread_pool.apply_async(
            create_snapshot,
            (project_object.project_directory, project_context, auth_header))

    # Check size of config folder
    if get_directory_size(
            project_object.project_directory, _max_zip_size_bytes, include_function=_include) > _max_zip_size_bytes:
        error_message = "====================================================================\n" \
                        "\n" \
                        "Your configuration directory exceeds the limit of {0} MB.\n" \
                        "Please see http://aka.ms/aml-largefiles on how to work with large files.\n" \
                        "\n" \
                        "====================================================================\n" \
                        "\n".format(_max_zip_size_bytes / _one_mb)
        raise ExperimentExecutionException(error_message)

    with temp_dir_back.TemporaryDirectory() as temporary:
        archive_path = os.path.join(temporary, "aml_config.zip")
        archive_path_local = os.path.join(temporary, "temp_project.zip")

        if not run_id:
            run_id = _get_project_run_id(service_arm_scope)

        project_temp_dir = _get_project_temporary_directory(run_id)
        os.mkdir(project_temp_dir)

        # We send only aml_config zip to service and copy only necessary files to temp dir
        ignore_file = get_project_ignore_file(project_object.project_directory)
        _make_zipfile_include(project_object, archive_path, _include)
        _make_zipfile_exclude(project_object, archive_path_local, ignore_file.is_file_excluded)

        # Inject files into the user's project'
        if injected_files:
            _add_files_to_zip(archive_path, injected_files)

        # Copy current project dir to temp/azureml-runs folder.
        zip_ref = zipfile.ZipFile(archive_path_local, 'r')
        zip_ref.extractall(project_temp_dir)
        zip_ref.close()

        # TODO Missing driver arguments, job_name

        # Normalizing the conda path, as the execution service only works with linux-like paths.
        run_config_object.environment.python.conda_dependencies_file \
            = normalize_windows_paths(run_config_object.environment.python.conda_dependencies_file)

        with open(archive_path, "rb") as archive:
            definition = {
                "TargetDetails": custom_target_dict,
                "Configuration": _serialize_run_config_to_dict(run_config_object),
                "TelemetryValues": telemetry_values}
            files = [
                ("files", ("definition.json", json.dumps(definition))),
                ("files", ("aml_config.zip", archive))]

            headers = _get_common_headers()

            # Merging the auth header.
            headers.update(auth_header)

            run_id_query = urllib3.request.urlencode({'runId': run_id})

            uri = service_address
            if prepare_only:
                # Unfortunately, requests library does not take Queryparams nicely.
                # Appending run_id_query to the url for service to extract from it.
                uri += "/execution/v1.0" + service_arm_scope + "/localprepare" + '?' + run_id_query
            else:
                # Unfortunately, requests library does not take Queryparams nicely.
                # Appending run_id_query to the url for service to extract from it.
                uri += "/execution/v1.0" + service_arm_scope + "/localrun" + '?' + run_id_query

            # Submit run is not idempotent for some failure modes, so don't retry.
            response = requests.post(uri, files=files, headers=headers)
            _raise_request_error(response, "starting run")

            invocation_zip_path = os.path.join(project_temp_dir, "invocation.zip")
            with open(invocation_zip_path, "wb") as file:
                file.write(response.content)

            with zipfile.ZipFile(invocation_zip_path, 'r') as zip_ref:
                zip_ref.extractall(project_temp_dir)

            try:
                _invoke_command(project_temp_dir)
            except subprocess.CalledProcessError as ex:
                raise ExperimentExecutionException(ex.output)

            snapshot_id = snapshot_async.get() if snapshot_async else None
            thread_pool.close()

            return _get_run_details(project_object, project_context, run_config_object, run_id,
                                    snapshot_id=snapshot_id)


# TODO: Need to update the documentation.
# This function is used across prepare and start functions.
# For prepare, there are two parameters: 1) prepare_only and 2) prepare_check. If prepare_only=True, then only
# prepare operation is run, and actual experiment run is not run. If prepare_only=False, then both the prepare
# operation and experiment is run. If prepare_only=True and prepare_check=False, then the an experiment prepare
# is done. If prepare_only=True and prepare_check=True, then only prepare status is checked and an actual prepare is
# not performed.
# prepare_only=False and prepare_check=True has no effect, the experiment wil be run and prepare will be performed
# if needed.
# If prepare_only=True and prepare_check=True, then tracked_run, async, wait arguments have no effect.
def _start_internal(project_object, run_config_object,
                    prepare_only=False, prepare_check=False,
                    custom_target_dict=None, run_id=None,
                    injected_files=None, telemetry_values=None):
    """
    :param project_object: Project object
    :type project_object: azureml.core.project.Project
    :param run_config_object: The run configuration object.
    :param run_config_object: azureml.core.runconfig.RunConfiguration
    :param prepare_only:
    :param prepare_check:
    :param custom_target_dict:
    :param run_id:
    :param injected_files:
    :type injected_files: dict
    :return: azureml.core.script_run.ScriptRun or bool if prepare_check=True
    """
    project_context = create_project_context(
        project_object.workspace_object._auth_object,
        project_object.workspace_object.subscription_id,
        project_object.workspace_object.resource_group,
        project_object.workspace_object.name,
        project_object.history.name,
        project_object.workspace_object._workspace_id)

    execution_service_details = ExecutionServiceAddress(project_context.get_cloud_execution_service_address())
    service_address = execution_service_details.address
    service_arm_scope = project_context.get_experiment_uri_path()

    auth_header = project_object.workspace_object._auth_object.get_authentication_header()
    thread_pool = Pool(1)
    ignore_file = get_project_ignore_file(project_object.project_directory)

    snapshot_async = None
    execute_with_zip = True

    directory_size = get_directory_size(
        project_object.project_directory,
        _max_zip_size_bytes,
        exclude_function=ignore_file.is_file_excluded)

    if directory_size >= _max_zip_size_bytes:
        give_warning("Submitting {} directory for run. "
                     "The size of the directory >= {} MB, "
                     "so it can take a few minutes.".format(project_object.project_directory, _num_max_mbs))

    if run_config_object.history.snapshot_project:
        snapshot_async = thread_pool.apply_async(
            create_snapshot,
            (project_object.project_directory, project_context, auth_header))

        # These can be set by users in case we have any issues with zip/snapshot and need to force a specific path
        force_execute_snapshot = os.environ.get("AML_FORCE_EXECUTE_WITH_SNAPSHOT")
        force_execute_zip = os.environ.get("AML_FORCE_EXECUTE_WITH_ZIP")

        if force_execute_snapshot and not force_execute_zip:
            execute_with_zip = False
        elif force_execute_zip and not force_execute_snapshot:
            execute_with_zip = True
        else:
            # Only execute with zip if the project is small and snapshot would take longer
            if directory_size < _max_zip_size_bytes:
                execute_with_zip = True
            else:
                execute_with_zip = False

    temporary = None
    archive = None
    try:
        if execute_with_zip:
            temporary = temp_dir_back.TemporaryDirectory()
            archive_path = os.path.join(temporary.name, "project.zip")
            _make_zipfile_exclude(project_object, archive_path, ignore_file.is_file_excluded)

            # Inject files into the user's project'
            if injected_files:
                _add_files_to_zip(archive_path, injected_files)
            archive = open(archive_path, "rb")

        headers = _get_common_headers()
        # Merging the auth header.
        headers.update(auth_header)

        uri = service_address
        api_prefix = "" if execute_with_zip else "snapshot"
        if prepare_only:
            if prepare_check:
                uri += "/execution/v1.0" + service_arm_scope + "/{}checkprepare".format(api_prefix)
            else:
                uri += "/execution/v1.0" + service_arm_scope + "/{}prepare".format(api_prefix)

        else:
            uri += "/execution/v1.0" + service_arm_scope + "/{}run".format(api_prefix)

        if not run_id:
            run_id = _get_project_run_id(service_arm_scope)

        run_id_query = urllib3.request.urlencode({'runId': run_id})
        uri = uri + '?' + run_id_query

        snapshot_id = snapshot_async.get() if snapshot_async else None
        thread_pool.close()

        # Normalizing the conda path, as the execution service only works with linux-like paths.
        run_config_object.environment.python.conda_dependencies_file \
            = normalize_windows_paths(run_config_object.environment.python.conda_dependencies_file)

        definition = {
            "TargetDetails": custom_target_dict,
            "Configuration": _serialize_run_config_to_dict(run_config_object),
            "TelemetryValues": telemetry_values
        }

        if execute_with_zip:
            files = [
                ("files", ("definition.json", json.dumps(definition))),
                ("files", ("project.zip", archive))]

            # Submit run is not idempotent for some failure modes, so don't retry.
            response = requests.post(uri, files=files, headers=headers)
        else:
            definition["SnapshotId"] = snapshot_id

            # Submit run is not idempotent for some failure modes, so don't retry.
            response = requests.post(uri, json=definition, headers=headers)

        _raise_request_error(response, "starting run")

    finally:
        if archive:
            archive.close()
        if temporary:
            temporary.cleanup()

    result = response.json()
    if prepare_only and prepare_check:
        return result["environmentPrepared"]

    return _get_run_details(project_object, project_context, run_config_object, result["runId"],
                            snapshot_id=snapshot_id)


def _get_run_details(project_object, project_context, run_config_object, run_id, snapshot_id=None):
    """
    Returns a run object or bool in case prepare_check=True
    :param project_object:
    :type project_object: azureml.core.project.Project
    :param project_context: Project context.
    :type project_context: azureml._base_sdk_common.project_context.ProjectContext
    :param run_config_object:
    :type run_config_object: azureml.core.runconfig.RunConfiguration
    :return:
    :rtype: azureml.core.script_run.ScriptRun
    """
    from azureml.core.script_run import ScriptRun
    client = RunClient.create(project_object.workspace_object,
                              project_object.history.name,
                              run_id)

    run_properties = {
        "ContentSnapshotId": snapshot_id,
    }
    create_run_dto = CreateRunDto(run_id, properties=run_properties)
    run_dto = client.patch_run(create_run_dto)
    dto_as_dict = RunClient.dto_to_dictionary(run_dto)
    experiment = Experiment(project_object.workspace_object, project_object.history.name)
    return ScriptRun(experiment, run_id,
                     directory=project_object.project_directory,
                     _run_config=run_config_object, _run_dto=dto_as_dict)


def return_results(project_object, run_id, target, overwrite=False):
    """
    Returns results. The output is returned as an object of CLICommandOutput.
    :param project_object:
    :type project_object: azureml.core.project.Project
    :param run_id:
    :param target:
    :param overwrite:
    :return:
    :rtype CLICommandOutput:
    """
    command_output = CLICommandOutput("")

    with temp_dir_back.TemporaryDirectory() as temporary:
        diagnostics_zip = os.path.join(temporary, "diagnostics.zip")
        get_diagnostics(project_object, run_id, target, destination=diagnostics_zip)

        with zipfile.ZipFile(diagnostics_zip, "r") as archive:
            archive.extractall(temporary)

        source = os.path.join(temporary, run_id)
        shutil.rmtree(os.path.join(source, ".git"), ignore_errors=True)
        shutil.rmtree(os.path.join(source, ".azureml"), ignore_errors=True)
        shutil.rmtree(os.path.join(source, "azureml-setup"), ignore_errors=True)
        shutil.rmtree(os.path.join(source, "azureml-logs"), ignore_errors=True)

        # Calling get_diagnostics sets the cwd to the project.
        destination = "."

        for source_path, _, files in os.walk(source):
            relative = os.path.relpath(source_path, source)
            destination_directory = os.path.join(destination, relative)
            if not os.path.exists(destination_directory):
                os.makedirs(destination_directory)
            for source_file in files:
                destination_file = os.path.join(destination_directory, source_file)
                if os.path.isfile(destination_file):
                    if not overwrite:
                        continue

                command_output.append_to_command_output("Returning " + os.path.normpath(destination_file))
                shutil.move(os.path.join(source_path, source_file), destination_file)

    command_output.append_to_command_output("Return results completed successfully.")
    command_output.set_do_not_print_dict()
    return command_output


def cancel(project_object, run_config_object, run_id):
    """
    Cancels an experiment run.
    :param project_object: Project object.
    :type project_object: azureml.core.project.Project
    :param run_config_object: The run configuration object
    :type run_config_object: azureml.core.runconfig.RunConfiguration
    :param run_id: Run id
    :type run_id: str
    :return: Returns True if cancelled successfully.
    :rtype: bool
    """
    custom_target_dict = _get_custom_target_dict(project_object, run_config_object.target)

    project_context = create_project_context(project_object.workspace_object._auth_object,
                                             project_object.workspace_object.subscription_id,
                                             project_object.workspace_object.resource_group,
                                             project_object.workspace_object.name,
                                             project_object.history.name,
                                             project_object.workspace_object._workspace_id)

    execution_service_details = ExecutionServiceAddress(project_context.get_cloud_execution_service_address())

    if _is_local_target(run_config_object.target, custom_target_dict):
        _cancel_local(project_object, run_id, project_context)
    else:
        body = {
            "RunId": run_id,
            "Target": run_config_object.target,
            "CustomTarget": custom_target_dict}

        uri = execution_service_details.address + "/execution/v1.0" \
                                                + project_context.get_experiment_uri_path() + "/cancel"

        auth_header = project_object.workspace_object._auth_object.get_authentication_header()
        headers = _get_common_headers()

        # Merging with auth header
        headers.update(auth_header)

        session = create_session_with_retry()
        response = session.post(uri, json=body, headers=headers)
        _raise_request_error(response, "Canceling run")


def _cancel_local(project_object, run_id, project_context):
    project_temp_dir = _get_project_temporary_directory(run_id)

    killfile = normalize_windows_paths(os.path.join(project_temp_dir, "azureml-setup", "killfile"))
    if not os.path.exists(killfile):
        with open(killfile, 'w+') as f:
            f.write(run_id)

    from azureml._restclient.run_client import RunClient
    run_client = RunClient.create(project_object.workspace_object,
                                  project_object.history.name,
                                  run_id)
    run_client.post_event_canceled()


def run_status(project_object, run_config_object, run_id):
    """
    Retrieves the run status.
    :param project_object: Project object.
    :type project_object: azureml.core.project.Project
    :param run_id: The run id
    :type run_id: str
    :param run_config_object: The run configuration object.
    :type run_config_object: azureml.core.runconfig.RunConfiguration
    :return: The status in dict format.
    :rtype dict:
    """

    project_context = create_project_context(project_object.workspace_object._auth_object,
                                             project_object.workspace_object.subscription_id,
                                             project_object.workspace_object.resource_group,
                                             project_object.workspace_object.name,
                                             project_object.history.name,
                                             project_object.workspace_object._workspace_id)

    return _get_status_from_history(project_object, run_id, project_context)


def clean(project_object, run_config_object, run_id=None, all=False):
    """
    Removes files corresponding to azureml run(s) from a target.
    Doesn't delete docker images for the local docker target.
    :param project_object: Project object
    :type project_object: azureml.core.project.Project
    :param run_config_object: The run configuration object
    :type run_config_object: azureml.core.runconfig.RunConfiguration
    :param run_id: The run id for the experiment whose files should be removed.
    :type run_id: str
    :param all: all=True, removes files for all azureml runs.
    :return: List of files deleted.
    :rtype: list
    """
    def remove_docker_image():
        return "Docker images used by AzureML have not been removed; they can be deleted with \"docker rmi\""

    custom_target_dict = _get_custom_target_dict(project_object, run_config_object.target)

    if all and run_id:
        raise UserErrorException("Error: Specify either --all or specific run to clean "
                                 "with --run <run_id>, not both.")

    if _is_local_target(run_config_object.target, custom_target_dict):
        if run_id is not None:
            output_list = []
            project_temp_dir = _get_project_temporary_directory(run_id)
            if os.path.exists(project_temp_dir):
                shutil.rmtree(project_temp_dir)
                # TODO: We are adding some text, instead of returning the directory directly?
                output_list.append("Removed temporary run directory {0}".format(os.path.abspath(project_temp_dir)))
                return output_list
            else:
                raise ExperimentExecutionException("Temporary directory for this run does not exist.")
        else:
            output_list = []
            import tempfile
            azureml_temp_dir = os.path.join(tempfile.gettempdir(), "azureml_runs")
            temp_runs = os.listdir(azureml_temp_dir)
            for run_id in temp_runs:
                project_temp_dir = _get_project_temporary_directory(run_id)
                shutil.rmtree(project_temp_dir)
                output_list.append("Removed temporary run directory {0}".format(os.path.abspath(project_temp_dir)))
            if custom_target_dict["type"] in ["docker", "localdocker"]:
                output_list.append(remove_docker_image())
            if custom_target_dict["type"] == "local":
                dot_azureml_dir = os.path.join(os.path.expanduser("~"), ".azureml")
                envs_dir = os.path.join(dot_azureml_dir, "envs")
                locks_dir = os.path.join(dot_azureml_dir, "locks")
                shutil.rmtree(envs_dir)
                shutil.rmtree(locks_dir)
                output_list.append("Removed managed environment directory {0}".format(os.path.abspath(envs_dir)))
            return output_list
    else:
        project_context = create_project_context(project_object.workspace_object._auth_object,
                                                 project_object.workspace_object.subscription_id,
                                                 project_object.workspace_object.resource_group,
                                                 project_object.workspace_object.name,
                                                 project_object.history.name,
                                                 project_object.workspace_object._workspace_id)

        execution_service_details = ExecutionServiceAddress(project_context.get_cloud_execution_service_address())

        body = {
            "RunId": run_id if run_id else "null",
            "Target": run_config_object.target,
            "CustomTarget": custom_target_dict}

        uri = execution_service_details.address + "/execution/v1.0" \
                                                + project_context.get_experiment_uri_path() + "/clean"  \
                                                + "?all=" + str(all)

        auth_header = project_object.workspace_object._auth_object.get_authentication_header()
        headers = _get_common_headers()

        headers.update(auth_header)

        session = create_session_with_retry()
        response = session.post(uri, json=body, headers=headers)
        _raise_request_error(response, "Deleting vienna run(s).")

        clean_list = response.json()
        return clean_list


def get_diagnostics(project_object, run_config_object, run_id, destination=None):
    """
    Returns an experiment's diagnostics.
    :param project_object: Project object.
    :type project_object: azureml.core.project.Project
    :param run_id:
    :param run_config_object:
    :type run_config_object: azureml.core.runconfig.RunConfiguration
    :param destination:
    :return: True if diagnostic zip retrieved successfully.
    :rtype: bool
    """
    custom_target_dict = _get_custom_target_dict(project_object, run_config_object.target)

    if not destination:
        # Defaulting to project/assets folder
        destination = os.path.join(project_object.project_directory, "assets", run_id + "_diagnostics.zip")

    project_context = create_project_context(project_object.workspace_object._auth_object,
                                             project_object.workspace_object.subscription_id,
                                             project_object.workspace_object.resource_group,
                                             project_object.workspace_object.name,
                                             project_object.history.name,
                                             project_object.workspace_object._workspace_id)

    execution_service_details = ExecutionServiceAddress(project_context.get_cloud_execution_service_address())

    if _is_local_target(run_config_object.target, custom_target_dict):
        project_temp_dir = _get_project_temporary_directory(run_id)
        zip_name = os.path.basename(destination).split(".zip")[0]
        # We avoid changing directories inside sdk. But, shutil.make_archive
        # only creates an archive in the cwd, so we are changing cwd here and then reverting.
        try:
            current_dir = os.getcwd()
            os.chdir(os.path.dirname(destination))
            shutil.make_archive(zip_name, 'zip', os.path.dirname(project_temp_dir), run_id)
        finally:
            os.chdir(current_dir)
    else:
        body = {
            "RunId": run_id,
            "Target": run_config_object.target,
            "CustomTarget": custom_target_dict}

        uri = execution_service_details.address + "/execution/v1.0" \
                                                + project_context.get_experiment_uri_path() + "/diagnostics"

        auth_header = project_object.workspace_object._auth_object.get_authentication_header()
        headers = _get_common_headers()

        headers.update(auth_header)

        session = create_session_with_retry()
        response = session.post(uri, json=body, headers=headers)
        _raise_request_error(response, "Downloading diagnostics")

        with open(destination, "wb") as file:
            file.write(response.content)

    # Checks on zip file.
    return _check_diagnostics_zip_validity(destination, run_id)


def _check_diagnostics_zip_validity(diagnostics_zip_path, run_id):
    """
    Checks the validity of the diagnostics zip specified using diagnostics_zip_path for run_id.
    :param diagnostics_zip_path:
    :type diagnostics_zip_path: str
    :param run_id: Run id
    :type run_id: str
    :return: True for valid zip.
    :rtype: bool
    """
    if zipfile.is_zipfile(diagnostics_zip_path):
        with zipfile.ZipFile(diagnostics_zip_path, 'r') as diagnostic_zip:
            file_list = diagnostic_zip.namelist()
            if file_list:
                for file_name in file_list:
                    if not file_name.startswith(run_id):
                        return False
                return True
            else:
                return False
    else:
        return False


def _raise_request_error(response, action="calling backend service"):
    if response.status_code >= 400:
        from azureml._base_sdk_common.common import get_http_exception_response_string
        # response.text is a JSON from execution service.
        response_message = get_http_exception_response_string(response)
        raise ExperimentExecutionException(response_message)


def _include(path):
    return any(folder in path for folder in ["aml_config"])


# Adapted from shutil._make_zipfile with an added exclusion function.
def _make_zipfile_exclude(project_object, zip_filename, exclude_function):
    base_dir = project_object.project_directory

    with zipfile.ZipFile(zip_filename, "w") as zf:
        for dirpath, dirnames, filenames in os.walk(base_dir):
            relative_dirpath = os.path.relpath(dirpath, base_dir)
            for name in sorted(dirnames):
                full_path = os.path.normpath(os.path.join(dirpath, name))
                relative_path = os.path.normpath(os.path.join(relative_dirpath, name))
                if not exclude_function(full_path):
                    zf.write(full_path, relative_path)
            for name in filenames:
                full_path = os.path.normpath(os.path.join(dirpath, name))
                relative_path = os.path.normpath(os.path.join(relative_dirpath, name))
                if not exclude_function(full_path):
                    if os.path.isfile(full_path):
                        zf.write(full_path, relative_path)


def _make_zipfile_include(project_object, zip_filename, include_function):
    base_dir = project_object.project_directory

    with zipfile.ZipFile(zip_filename, "w") as zf:
        for dirpath, dirnames, filenames in os.walk(base_dir):
            relative_dirpath = os.path.relpath(dirpath, base_dir)
            for name in sorted(dirnames):
                full_path = os.path.normpath(os.path.join(dirpath, name))
                relative_path = os.path.normpath(os.path.join(relative_dirpath, name))
                if include_function(full_path):
                    zf.write(full_path, relative_path)
            for name in filenames:
                full_path = os.path.normpath(os.path.join(dirpath, name))
                relative_path = os.path.normpath(os.path.join(relative_dirpath, name))
                if include_function(full_path):
                    if os.path.isfile(full_path):
                        zf.write(full_path, relative_path)


def _is_local_target(target_name, custom_target_dict):
    # Local is a magic compute target name; no config file or MLC object is required.
    if target_name == "local":
        return True

    if not custom_target_dict:
        return False

    return custom_target_dict["type"] in ["local", "docker", "localdocker"]


def _get_status_from_history(project_object, run_id, project_context):
    """
    Queries the execution service for status of an experiment from history service.
    Returns the JSONObject returned by the service.
    :param project_object:
    :type project_object: azureml.core.project.Project
    :param run_id:
    :param project_context:
    :type project_context: azureml._base_sdk_common.project_context.ProjectContext
    :return:
    :rtype: dict
    """
    history_address = project_context.get_history_service_uri()

    auth_header = project_object.workspace_object._auth_object.get_authentication_header()
    headers = _get_common_headers()
    headers.update(auth_header)
    session = create_session_with_retry()
    runstatus_uri = history_address + "/history/v1.0" + project_context.get_experiment_uri_path()
    runstatus_uri += "/runs/" + run_id + "/runstatus"
    response = session.get(runstatus_uri, headers=headers)
    _raise_request_error(response, "Getting run status from history")
    return response.json()


def _get_content_from_uri(uri, session=None):
    """
    Queries the artifact service for an artifact and returns it's contents
    Returns the Response text by the service
    :return:
    :rtype: dict
    """

    if session is None:
        session = create_session_with_retry()
    response = session.get(uri)

    # Match old behavior from execution service's status API.
    if response.status_code == 404:
        return ""

    _raise_request_error(response, "Retrieving content from " + uri)
    return response.text


def _get_common_headers():
    headers = {
        "User-Agent": get_user_agent(),
        "x-ms-client-session-id": _ClientSessionId,
        "x-ms-client-request-id": str(uuid.uuid4())
    }
    return headers


def _get_configuration_path(project_object, name, config_type):
    files = get_project_files(project_object.project_directory, config_type)
    if name not in files:
        return None

    return files[name]


def _read_run_configuration(path):
    # TODO: Notebook calls this.
    with open(path, 'r') as file:
        return yaml.load(file.read())


def _get_custom_target_dict(project_object, target):
    project_targets = get_project_files(project_object.project_directory, COMPUTECONTEXT_EXTENSION)
    if target in project_targets:
        path_to_target = project_targets[target]
        with open(os.path.join(project_object.project_directory,
                               path_to_target), 'r') as file:
            return yaml.load(file.read())

    return None


def _add_files_to_zip(archive_path, injected_files):
    try:
        archive = zipfile.ZipFile(archive_path, 'a', zipfile.ZIP_DEFLATED)
        for file_path in injected_files.keys():
            dest_path = injected_files[file_path]
            archive.write(file_path, dest_path)
    finally:
        archive.close()


def _invoke_command(project_temp_dir):
    # Delete the zip file from tempdir - that comes from the service.
    invocation_zip_file = os.path.join(project_temp_dir, "Invocation.zip")
    if os.path.isfile(invocation_zip_file):
        os.remove(invocation_zip_file)

    if os.name == "nt":
        invocation_script = os.path.join(project_temp_dir, "azureml-setup", "Invocation.bat")
        invoke_command = ["cmd.exe", "/c", "{0}".format(invocation_script)]
    else:
        invocation_script = os.path.join(project_temp_dir, "azureml-setup", "Invocation.sh")
        subprocess.check_output(["chmod", "+x", invocation_script])
        invoke_command = ["/bin/bash", "-c", "{0}".format(invocation_script)]

    start_background_process(invoke_command, cwd=project_temp_dir)


def _get_project_temporary_directory(run_id):
    import tempfile
    azureml_temp_dir = os.path.join(tempfile.gettempdir(), "azureml_runs")
    if not os.path.isdir(azureml_temp_dir):
        os.mkdir(azureml_temp_dir)

    project_temp_dir = os.path.join(azureml_temp_dir, run_id)
    return project_temp_dir


def _get_project_run_id(project_uri):
    project_name = project_uri.split('/')[-1]
    run_id = project_name + "_" + str(int(time.time())) + "_" + str(uuid.uuid4())[:8]
    return run_id


def _get_telemetry_values(telemetry_values):
    if telemetry_values is None:
        telemetry_values = {}

    # Collect common client info
    telemetry_values['amlClientOSVersion'] = platform.platform()
    telemetry_values['amlClientPythonVersion'] = sys.version

    # Do not override client type if it already exists
    telemetry_values.setdefault('amlClientType', 'azureml-sdk-core')

    return telemetry_values
