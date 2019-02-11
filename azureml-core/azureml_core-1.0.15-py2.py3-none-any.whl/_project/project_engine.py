# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

""" projectsystem.py, A file for handling new project system logic."""

from __future__ import print_function

import os
import requests
import traceback

import azureml._project.project_mapper as project_mapper
import azureml._project.project_manager as project_manager
import azureml._project.project_info as ProjectInfo
from azureml.exceptions import ProjectSystemException

# JSON File Keys
PROJECT_ID = "Id"
PROJECT_PATH = "Path"
EXPERIMENT_NAME = "RunHistoryName"
USER_EMAIL = "UserEmail"
USER_NAME = "Username"
BEHALF = "BehalfOfMicrosoft"
ACCOUNT_NAME = "AccountName"


def _raise_request_error(response, action="calling backend service"):
    if response.status_code >= 400:
        from azureml._base_sdk_common.common import get_http_exception_response_string
        raise ProjectSystemException(get_http_exception_response_string(response))


class ProjectEngineClient(object):
    def __init__(self, auth):
        """

        :param auth: auth object
        :type auth: azureml.core.authentication.AbstractAuthentication
        """
        self._auth = auth
        # Repo related information is none for now
        self._headers = auth.get_authentication_header()

    def create_project(self, project_id, path, project_name,
                       project_full_id):
        """Creates a project"""
        try:
            project_manager.create_project(
                project_id=project_id,
                repo_path=os.path.join(path, project_name),
                scope=project_full_id)

            return {
                PROJECT_ID: project_id,
                PROJECT_PATH: path,
                EXPERIMENT_NAME: project_name
            }
        except Exception:
            raise ProjectSystemException(traceback.format_exc())

    def attach_project(self, project_id, project_path, project_arm_scope):
        """
        Attaches a local folder, specified by project_path, as an
        azureml project.
        One thing to note is that in this we don't create or delete any project
        directory, otherwise we may end up deleting a users C drive in the worst case.
        """
        try:
            project_manager.attach_project(project_id, project_path, project_arm_scope)

            return {
                PROJECT_ID: project_id,
                PROJECT_PATH: project_path
            }

        except Exception:
            raise ProjectSystemException(traceback.format_exc())

    def show_sample(self, account_scope, sample_id):
        """Shows a project sample"""
        route = "/projects/v1.0/gallery/" + sample_id

        self._setup_gallery_coordinates(account_scope)

        response = requests.get(self._execution_details.address + route, headers=self._headers)

        _raise_request_error(response, "Return project sample")
        gallery_object = response.json()
        return gallery_object

    def list_samples(self, account_scope):
        """List all project samples"""
        route = "/projects/v1.0/gallery"

        self._setup_gallery_coordinates(account_scope)

        response = requests.get(self._execution_details.address + route, headers=self._headers)

        _raise_request_error(response, "Return project samples")
        gallery_objects = response.json()
        return gallery_objects

    @staticmethod
    def get_project_scope_by_path(project_path):
        try:
            project_info = ProjectInfo.get(project_path)
            if not project_info:
                return None

            return project_info.Scope

        except Exception:
            raise ProjectSystemException(traceback.format_exc())

    def get_local_projects(self):
        try:
            return project_mapper.get_project_id_to_path_map()

        except Exception:
            raise ProjectSystemException(traceback.format_exc())

    def get_project_path_from_id(self, project_id):
        try:
            project_map = project_mapper.get_project_id_to_path_map()
            return project_map.get(project_id)

        except Exception:
            raise ProjectSystemException(traceback.format_exc())
