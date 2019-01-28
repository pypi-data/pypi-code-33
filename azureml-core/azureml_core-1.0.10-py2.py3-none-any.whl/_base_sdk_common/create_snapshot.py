# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import os
import uuid

from azureml._base_sdk_common.common import get_http_exception_response_string
from azureml._base_sdk_common.merkle_tree import DirTreeJsonEncoder, create_merkletree
from azureml._base_sdk_common.merkle_tree_differ import compute_diff
from azureml._base_sdk_common.project_snapshot_cache import ContentSnapshotCache
from azureml._base_sdk_common.snapshot_dto import SnapshotDto
from azureml._base_sdk_common.utils import create_session_with_retry, get_directory_size
from azureml._project.ignore_file import get_project_ignore_file
from azureml.exceptions import SnapshotException

_one_mb = 1024 * 1024
_max_snapshot_size_bytes = 300 * _one_mb
_max_files = 2000
_batch_size = 500


def _validate_snapshot_size(file_or_folder_path, exclude_function):
    """
    Validates the project is not too large to snapshot

    :type file_or_folder_path: str
    :type exclude_function: Callable

    :rtype: None
    """
    if os.path.isfile(file_or_folder_path):
        size = os.path.getsize(file_or_folder_path)
    else:
        size = get_directory_size(
            file_or_folder_path, size_limit=_max_snapshot_size_bytes, exclude_function=exclude_function)

    if size > _max_snapshot_size_bytes:
        error_message = "====================================================================\n" \
                        "\n" \
                        "Your total project size exceeds the limit of {} MB.\n" \
                        "Please see http://aka.ms/aml-largefiles on how to work with large files.\n" \
                        "\n" \
                        "====================================================================\n" \
                        "\n".format(_max_snapshot_size_bytes / _one_mb)
        raise SnapshotException(error_message)


def create_snapshot(file_or_folder_path, project_context, auth_headers=None, retry_on_failure=True):
    ignore_file = get_project_ignore_file(file_or_folder_path)
    exclude_function = ignore_file.is_file_excluded

    _validate_snapshot_size(file_or_folder_path, exclude_function)

    # Get the previous snapshot for this project
    cache = ContentSnapshotCache(project_context)
    parent_root, parent_snapshot_id = cache.get_latest_snapshot()

    # Compute the dir tree for the current working set
    curr_root = create_merkletree(file_or_folder_path, exclude_function)

    # Compute the diff between the two dirTrees
    entries = compute_diff(parent_root, curr_root)

    # If there are no changes, just return the previous snapshot_id
    if not len(entries):
        return parent_snapshot_id

    entries_to_send = [entry for entry in entries if
                       (entry.operation_type == 'added' or entry.operation_type == 'modified') and entry.is_file]

    if len(entries_to_send) > _max_files and not os.environ.get("AML_SNAPSHOT_NO_FILE_LIMIT"):
        error_message = "====================================================================\n" \
                        "\n" \
                        "Your project exceeds the file limit of {}.\n" \
                        "\n" \
                        "====================================================================\n" \
                        "\n".format(_max_files)
        raise SnapshotException(error_message)

    custom_headers = {
        "dirTreeRootFile": "true"
    }
    dir_tree_file_contents = json.dumps(curr_root, cls=DirTreeJsonEncoder)

    if not auth_headers:
        auth_headers = project_context.get_auth().get_authentication_header()

    session = create_session_with_retry()

    # There is an OS limit on how many files can be open at once, so we must batch the snapshot to not exceed the
    # limit. We take multiple snapshots, each building on each other, and return the final snapshot.
    new_snapshot_id = None
    # We always need to do at least one pass, for the case where the only change is deleted files in dirTreeRootFile
    first_pass = True
    while len(entries_to_send) or first_pass:
        first_pass = False
        files_to_send = []
        files_to_close = []
        if new_snapshot_id:
            parent_snapshot_id = new_snapshot_id
        new_snapshot_id = str(uuid.uuid4())
        try:
            # Add entries until we hit batch limit
            while len(files_to_send) < _batch_size and len(entries_to_send):
                entry = entries_to_send.pop()
                path_env = (os.path.join(file_or_folder_path, entry.node_path)
                            if os.path.isdir(file_or_folder_path)
                            else entry.node_path)
                file_obj = open(path_env, "rb")
                files_to_send.append(("files", (entry.node_path, file_obj)))
                files_to_close.append(file_obj)

            # directory_tree needs to be added to all snapshot requests
            files_to_send.append(
                ("files", ("dirTreeRootFile", dir_tree_file_contents, "application/json", custom_headers)))
            url = project_context.get_history_service_uri() + "/content/v1.0" + \
                project_context.get_workspace_uri_path() + "/snapshots/" + \
                new_snapshot_id + "?parentSnapshotId=" + parent_snapshot_id

            response = session.post(url, files=files_to_send, headers=auth_headers)
            if response.status_code >= 400:
                if retry_on_failure:
                    # The cache may have been corrupted, so clear it and try again.
                    cache.remove_latest()
                    return create_snapshot(file_or_folder_path, project_context, auth_headers, retry_on_failure=False)
                else:
                    raise SnapshotException(get_http_exception_response_string(response))
        finally:
            for f in files_to_close:
                f.close()

    # Update the cache
    snapshot_dto = SnapshotDto(dir_tree_file_contents, new_snapshot_id)
    cache.update_cache(snapshot_dto)
    return new_snapshot_id
