# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import os
import shutil
from collections import namedtuple

import azureml._project.file_utilities as file_utilities

_project_filename = "project.json"


def add(project_id, scope, project_path):
    """
    Creates project info file

    :type project_id: str
    :type scope: str
    :type project_path: str

    :rtype: None
    """
    config_directory = os.path.join(project_path, file_utilities.configuration_directory_name)
    file_utilities.create_directory(config_directory, True)

    project_file_path = os.path.join(config_directory, _project_filename)
    # We overwriting if project.json exists.
    with open(project_file_path, "w") as fo:
        info = ProjectInfo(project_id, scope)
        fo.write(json.dumps(info.__dict__))


def get(project_path, no_recursive_check=False):
    """
    Get ProjectInfo for specified project

    :type project_path: str
    :param no_recursive_check:
    :type no_recursive_check: bool
    :rtype: ProjectInfo
    """
    while True:
        for config_path in [
                file_utilities.configuration_directory_name,
                file_utilities.legacy_configuration_directory_name]:
            info_path = os.path.join(project_path, config_path, _project_filename)
            if os.path.exists(info_path):
                with open(info_path) as info_json:
                    info = json.load(info_json)
                    info = namedtuple("ProjectInfo", info.keys())(*info.values())
                    return info

        parent_dir = os.path.dirname(project_path)
        if project_path == parent_dir:
            break
        else:
            project_path = parent_dir

        if no_recursive_check:
            return None
    return None


def delete_project_json(project_path):
    """
    Deletes the project.json from the project folder specified by project_path.
    :return: None, throws an exception if deletion fails.
    """
    for config_path in [file_utilities.configuration_directory_name,
                        file_utilities.legacy_configuration_directory_name]:
        info_path = os.path.join(project_path, config_path, _project_filename)
        if os.path.exists(info_path):
            os.remove(info_path)


def delete(project_path):
    """
    Deletes the metadata folder containing project info

    :type project_path: str

    :rtype: None
    """
    for config_path in [
                file_utilities.configuration_directory_name,
                file_utilities.legacy_configuration_directory_name]:
        config_directory = os.path.join(project_path, file_utilities.configuration_directory_name)
        if os.path.isdir(config_directory):
            shutil.rmtree(config_directory)


class ProjectInfo(object):
    def __init__(self, project_id, scope):
        """
        :type project_id: str
        :type scope: str
        """
        # Uppercase to work with existing JSON files
        self.Id = project_id
        self.Scope = scope
