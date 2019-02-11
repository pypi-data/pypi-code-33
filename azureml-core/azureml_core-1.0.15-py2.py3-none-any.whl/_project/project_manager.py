# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import shutil

from azureml._project.ignore_file import AmlIgnoreFile
import azureml._project.file_utilities as file_utilities
import azureml._project.project_info as project_info
import azureml._project.project_mapper as project_mapper

from azureml._base_sdk_common import __version__ as package_version

_default_git_folder_name = ".git"
_asset_folder_name = "assets"
_base_project_contents_folder_name = "base_project_files"
_conda_dependencies_file_name = "conda_dependencies.yml"
_config_folder_name = "aml_config"

_history_branch_name = "AzureMLHistory"

_link_repo_commit_message = "link"
_create_project_commit_message = "Initial commit"
_run_history_push_commit_message = "Run history"


def _current_index():
    requirements_index = None
    index_file_path = os.path.join(os.path.dirname(__file__), "index_location.txt")
    with open(index_file_path, "r") as file:
        prerelease_index = file.read().strip()
        if prerelease_index:
            requirements_index = prerelease_index
    return requirements_index


def _update_requirements_binding(repo_path):
    # These should remain None for the local development scenario.
    requirements_version = None

    # Set the package version from the __version__ if it's not local development default.
    if not package_version.endswith("+dev"):
        requirements_version = package_version

    requirements_index = _current_index()

    default_index = "https://azuremlsdktestpypi.azureedge.net/sdk-release/Preview/E7501C02541B433786111FE8E140CAA1"

    conda_dependencies_path = os.path.join(repo_path, _config_folder_name, _conda_dependencies_file_name)

    lines = []
    with open(conda_dependencies_path, "r") as infile:
        for line in infile:
            if requirements_version:
                line = line.replace("azureml-defaults", "azureml-defaults==" + requirements_version)
            if requirements_index:
                line = line.replace(default_index, requirements_index)

            lines.append(line)
    with open(conda_dependencies_path, 'w') as outfile:
        for line in lines:
            outfile.write(line)


def create_project(project_id, repo_path, scope):
    """
    Create a new project.

    :type project_id:  str
    :type repo_path:  str
    :type scope:  str
    :rtype: None
    """
    is_existing_dir = os.path.isdir(repo_path)
    _ensure_directory_is_valid(repo_path)
    try:
        if not is_existing_dir:
            os.makedirs(repo_path)

        _create_metadata_folders(repo_path)
        _copy_default_files(os.path.join(repo_path, _config_folder_name), _base_project_contents_folder_name)

        _update_requirements_binding(repo_path)

        # Creates local and docker runconfigs.
        _create_default_run_configs(repo_path)

        project_mapper.add_project(project_id, repo_path, scope)

    except Exception:
        project_mapper.remove_project(repo_path)
        if not is_existing_dir and os.path.isdir(repo_path):
            shutil.rmtree(repo_path)
        raise


def attach_project(project_id, project_path, scope):
    """
    Attaches a local folder specified by project_path as a project.

    :type project_id:  str
    :type project_path:  str
    :type scope:  str
    :rtype: None
    """
    is_existing_dir = os.path.isdir(project_path)
    if not is_existing_dir:
        # We creating all intermediate dirs too.
        os.makedirs(os.path.abspath(project_path))

    # check path is a full, rooted path
    if not os.path.isabs(project_path):
        raise ValueError("Selected directory is invalid")

    # check if path is already a project
    original_project_info = project_info.get(project_path, no_recursive_check=True)

    _create_metadata_folders(project_path)

    # Only copying when repo_path is not already a project.
    if not original_project_info:
        _copy_default_files(os.path.join(project_path, _config_folder_name), _base_project_contents_folder_name)
        _update_requirements_binding(project_path)

        # Creates local and docker runconfigs.
        _create_default_run_configs(project_path)

    # Overwriting if project.json already exists.
    project_mapper.add_project(project_id, project_path, scope)


def delete_project(path):
    """
    Removes project from mapping. Does not delete entire project from disk.

    :type path: str

    :rtype: None
    """
    project_mapper.remove_project(path)


def _copy_default_files(path, default_fileset):
    """
    Copy default files to folder

    :type path: str
    :type folder_name: str

    :rtype: None
    """
    this_dir, this_filename = os.path.split(__file__)
    default_files_path = os.path.join(this_dir, default_fileset)

    if not os.path.exists(path):
        os.mkdir(path)
    for filename in os.listdir(default_files_path):
        orig_path = os.path.join(default_files_path, filename)
        new_path = os.path.join(path, filename)
        if os.path.isdir(orig_path):
            shutil.copytree(orig_path, new_path)
        else:
            if not os.path.exists(new_path):
                shutil.copy(orig_path, new_path)


def _create_metadata_folders(path):
    """
    Create metadata files and folders

    :type path: str

    :rtype: None
    """
    file_utilities.create_directory(os.path.join(path, file_utilities.configuration_directory_name))
    file_utilities.create_directory(os.path.join(path, _asset_folder_name))

    aml_ignore = AmlIgnoreFile(path)
    aml_ignore.create_if_not_exists()


def _ensure_directory_is_valid(path):
    """
    Validate the directory

    :type path: str

    :rtype: None
    """
    # check path is a full, rooted path
    if not os.path.isabs(path):
        raise ValueError("Selected directory is invalid")

    # check if path is already a project
    if project_info.get(path):
        raise ValueError("Directory must not be an existing project")


def empty_function():
    return


def _create_default_run_configs(project_directory):
    """
    Creates a local.runconfig and docker.runconfig for a project.
    :return: None
    """
    from azureml.core.runconfig import RunConfiguration
    # Mocking a project object, as RunConfiguration requires a Project object, but only requires
    # project_directory field.
    project_object = empty_function
    project_object.project_directory = project_directory

    # Creating a local runconfig.
    local_run_config = RunConfiguration()
    local_run_config.history.output_collection = True
    local_run_config.save(name="local", path=project_directory)

    # Creating a docker runconfig.
    docker_run_config = RunConfiguration()
    docker_run_config.framework = "PySpark"
    docker_run_config.environment.docker.enabled = True
    docker_run_config.history.output_collection = True
    docker_run_config.save(name="docker", path=project_directory)
