# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

""" This module handles syncing git repos with the backend. Used for pull
request features."""

import json
import logging
import os
import shutil
import tempfile
import threading
import zipfile
from os.path import join, splitext

import six

from ._reporting import FILE_UPLOADED_FAILED
from .connection import Reporting, get_backend_session

LOGGER = logging.getLogger(__name__)


def get_repo_root(endpoint, project_id, experiment_id, file_path):
    """
    Gets the git repo path from server.

    Args:
        endpoint: path to server endpoint
        project_id: unique project identifier (required)
        experiment_id: unique experiment identifier (required)
        file_path: current file path. Could be any file that belongs to the
        repo.

    Returns: path to git repo

    """
    payload = {
        "projectId": project_id,
        "filePath": file_path,
        "experimentId": experiment_id,
    }
    with get_backend_session() as session:
        r = session.get(endpoint, params=payload)

    ret_val = json.loads(r.text)

    if "root_path" in ret_val and ret_val["root_path"] is not None:
        return ret_val["root_path"]

    elif "msg" in ret_val:
        raise ValueError(ret_val["msg"])

    return None


def compress_git_patch(git_patch):
    # Create a zip
    zip_dir = tempfile.mkdtemp()

    zip_path = os.path.join(zip_dir, "patch.zip")
    archive = zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED)
    archive.writestr("git_diff.patch", git_patch)
    archive.close()

    return archive, zip_path


def compress_py_files(repo_root_path, extensions):
    """
    Compresses all files ending with given extensions in repo to a single zip
    file
    Args:
        repo_root_path: path of folder to zip
        extensions: list of strings containing extensions of files to zip

    Returns: (path to folder that contains zip file, full path to zip file)

    """
    zip_dir = tempfile.mkdtemp()
    zip_path = join(zip_dir, "repo.zip")

    archive = zipfile.ZipFile(zip_path, "w")

    for root, _, files in os.walk(repo_root_path):
        for afile in files:
            extension = splitext(afile)[-1].lower()
            if extension in extensions:
                arcname = join(root.replace(repo_root_path, ""), afile)
                archive.write(join(root, afile), arcname=arcname)
    archive.close()

    return zip_dir, zip_path


def _send_file(url, files, params):
    LOGGER.debug("Uploading file to %s with params %s", url, params)

    with get_backend_session() as session:
        r = session.post(url, params=params, files=files)

    LOGGER.debug("Uploading file to %s done", url)

    if r.status_code != 200:
        raise ValueError(
            "POSTing file failed (%s) on url %r: %s" % (r.status_code, url, r.content)
        )

    return r


def send_file(
    post_endpoint, api_key, experiment_id, project_id, file_path, additional_params=None
):
    params = {"experimentId": experiment_id, "projectId": project_id, "apiKey": api_key}

    if additional_params is not None:
        params.update(additional_params)

    with open(file_path, "rb") as _file:

        files = {"file": _file}

        return _send_file(post_endpoint, params=params, files=files)


def upload_file(
    project_id,
    experiment_id,
    file_path,
    upload_endpoint,
    api_key,
    additional_params=None,
    clean=True,
):
    try:
        response = send_file(
            upload_endpoint,
            api_key,
            experiment_id,
            project_id,
            file_path,
            additional_params,
        )

        if clean is True:
            # Cleanup file
            try:
                os.remove(file_path)
            except OSError:
                pass

        LOGGER.debug(
            "File successfully uploaded to (%s): %s",
            response.status_code,
            upload_endpoint,
        )
    except Exception as e:
        LOGGER.error("File could not be uploaded", exc_info=True)
        Reporting.report(
            event_name=FILE_UPLOADED_FAILED,
            experiment_key=experiment_id,
            project_id=project_id,
            api_key=api_key,
            err_msg=str(e),
        )


def upload_file_thread(*args, **kwargs):
    p = threading.Thread(target=upload_file, args=args, kwargs=kwargs)
    p.daemon = True
    p.start()
    return p


def write_file_like_to_tmp_file(file_like_object):
    # Copy of `shutil.copyfileobj` with binary / text detection

    buf = file_like_object.read(1)

    # Detect binary/text
    if isinstance(buf, six.binary_type):
        tmp_file_mode = "w+b"
    else:
        tmp_file_mode = "w+"

    tmp_file = tempfile.NamedTemporaryFile(mode=tmp_file_mode, delete=False)

    tmp_file.write(buf)

    # Main copy loop
    while True:
        buf = file_like_object.read(16 * 1024)

        if not buf:
            break

        tmp_file.write(buf)

    return tmp_file.name
