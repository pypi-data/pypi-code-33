# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import tempfile

from azureml._base_sdk_common.utils import create_session_with_retry
from azureml.exceptions import ProjectSystemException


class RestoreSnapshot(object):
    def __init__(self, project_context):
        self.content_service_url = project_context.get_history_service_uri() + "/content/v1.0"
        self.arm_token = "Bearer " + project_context.get_auth()._get_arm_token()
        self.workspace_scope = project_context.get_workspace_uri_path()

    def restore_snapshot(self, snapshot_id, path):
        headers = {
            "Authorization": self.arm_token
        }
        session = create_session_with_retry()

        url = self.content_service_url + self.workspace_scope + "/snapshots/" + snapshot_id
        response = session.get(url, headers=headers)
        if response.status_code >= 400:
            from azureml._base_sdk_common.common import get_http_exception_response_string
            raise ProjectSystemException(get_http_exception_response_string(response))
        # This returns a sas url to blob store
        sas_url = response.content.decode('utf-8')
        sas_url = sas_url[1:-1]
        response = session.get(sas_url)
        if response.status_code >= 400:
            from azureml._base_sdk_common.common import get_http_exception_response_string
            raise ProjectSystemException(get_http_exception_response_string(response))

        if path is None:
            path = tempfile.gettempdir()

        snapshot_file_name = str(snapshot_id) + '.zip'
        temp_path = os.path.join(path, snapshot_file_name)

        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return os.path.abspath(temp_path)
