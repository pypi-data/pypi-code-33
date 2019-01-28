# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Access ArtifactsClient"""

import os
import requests

from io import IOBase

from msrest.exceptions import HttpOperationError

from azureml._async import TaskQueue
from azureml._file_utils import download_file, download_file_stream, upload_blob_from_stream

from azureml.exceptions import UserErrorException, AzureMLException

from .models.batch_artifact_container_sas_ingest_command import BatchArtifactContainerSasIngestCommand
from .models.artifact_path_dto import ArtifactPathDto
from .models.batch_artifact_create_command import BatchArtifactCreateCommand
from .workspace_client import WorkspaceClient

SUPPORTED_NUM_EMPTY_ARTIFACTS = 500


class ArtifactsClient(WorkspaceClient):
    """
    Artifacts client class

    :param host: The base path for the server to call.
    :type host: str
    :param auth: Client authentication
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param subscription_id:
    :type subscription_id: str
    :param resource_group_name:
    :type resource_group_name: str
    :param workspace_name:
    :type workspace_name: str
    """

    def __init__(self, *args, **kwargs):
        super(ArtifactsClient, self).__init__(*args, **kwargs)
        batch_size = SUPPORTED_NUM_EMPTY_ARTIFACTS
        self.session = requests.session()
        self.session.mount('https://', requests.adapters.HTTPAdapter(max_retries=3, pool_maxsize=batch_size))

    def create_empty_artifacts(self, origin, container, paths):
        """create empty artifacts"""
        if container is None:
            raise UserErrorException("DataContainerID cannot be null when creating empty artifacts")

        if isinstance(paths, str):
            paths = [paths]
        artifacts = [ArtifactPathDto(path) for path in paths]
        batch_create_command = BatchArtifactCreateCommand(artifacts)
        res = self._execute_with_workspace_arguments(
            self._client.artifact.batch_create_empty_artifacts,
            origin,
            container,
            batch_create_command)

        if res.errors:
            error_messages = []
            for artifact_name in res.errors:
                error = res.errors[artifact_name].error
                error_messages.append("{}: {}".format(error.code,
                                                      error.message))
            raise AzureMLException("\n".join(error_messages))

        return res

    def upload_stream_to_existing_artifact(self, stream, artifact, content_information,
                                           content_type=None, session=None):
        """upload a stream to existring artifact"""
        artifact = artifact
        artifact_uri = content_information.content_uri
        session = session if session is not None else self.session
        res = upload_blob_from_stream(stream, artifact_uri, content_type=content_type, session=session)
        return res

    def upload_artifact_from_stream(self, stream, origin, container, name, content_type=None, session=None):
        """upload a stream to a new artifact"""
        if container is None:
            raise UserErrorException("Cannot upload artifact when DataContainerID is None")
        # Construct body
        res = self.create_empty_artifacts(origin, container, name)
        artifact = res.artifacts[name]
        content_information = res.artifact_content_information[name]
        self.upload_stream_to_existing_artifact(stream, artifact, content_information,
                                                content_type=content_type, session=session)
        return res

    def upload_artifact_from_path(self, path, *args, **kwargs):
        """upload a local file to a new artifact"""
        path = os.path.normpath(path)
        path = os.path.abspath(path)
        with open(path, "rb") as stream:
            return self.upload_artifact_from_stream(stream, *args, **kwargs)

    def upload_artifact(self, artifact, *args, **kwargs):
        """upload local file or stream to a new artifact"""
        self._logger.debug("Called upload_artifact")
        if isinstance(artifact, str):
            self._logger.debug("Uploading path artifact")
            return self.upload_artifact_from_path(artifact, *args, **kwargs)
        elif isinstance(artifact, IOBase):
            self._logger.debug("Uploading io artifact")
            return self.upload_artifact_from_stream(artifact, *args, **kwargs)
        else:
            raise UserErrorException("UnsupportedType: type {} is invalid, "
                                     "supported input types: file path or file".format(type(artifact)))

    def upload_files(self, paths, origin, container, names=None):
        """
        upload files to artifact service
        :rtype: list[BatchArtifactContentInformationDto]
         """

        if container is None:
            raise UserErrorException("Data Container ID cannot be null when uploading artifact")

        names = names if names is not None else paths
        path_to_name = {}
        paths_and_names = []
        # Check for duplicates, this removes possible interdependencies
        # during parallel uploads
        for path, name in zip(names, paths):
            if path not in path_to_name:
                paths_and_names.append((path, name))
                path_to_name[path] = name
            else:
                self._logger.warning("Found repeat file {} with name {} in upload_files.\n"
                                     "Uploading file {} to the original name "
                                     "{}.".format(path, name, path, path_to_name[path]))

        batch_size = SUPPORTED_NUM_EMPTY_ARTIFACTS

        results = []
        for i in range(0, len(names), batch_size):
            with TaskQueue(worker_pool=self._pool, _ident="upload_files", _parent_logger=self._logger) as task_queue:
                batch_names = names[i:i + batch_size]
                batch_paths = paths[i:i + batch_size]

                content_information = self.create_empty_artifacts(origin, container, batch_names)

                def perform_upload(path, artifact, artifact_content_info, session):
                    with open(path, "rb") as stream:
                        return self.upload_stream_to_existing_artifact(stream, artifact, artifact_content_info,
                                                                       session=session)

                for path, name in zip(batch_paths, batch_names):
                    artifact = content_information.artifacts[name]
                    artifact_content_info = content_information.artifact_content_information[name]
                    task = task_queue.add(perform_upload, path, artifact, artifact_content_info, self.session)
                    results.append(task)

        return map(lambda task: task.wait(), results)

    def upload_dir(self, dir_path, origin, container, path_to_name_fn=None):
        """
        upload all files in path
        :rtype: list[BatchArtifactContentInformationDto]
        """
        if container is None:
            raise UserErrorException("Cannot upload when DataContainerID is None")
        paths_to_upload = []
        names = []
        for pathl, _subdirs, files in os.walk(dir_path):
            for _file in files:
                fpath = os.path.join(pathl, _file)
                paths_to_upload.append(fpath)
                if path_to_name_fn is not None:
                    name = path_to_name_fn(fpath)
                else:
                    name = fpath
                names.append(name)
        self._logger.debug("Uploading {}".format(names))
        result = self.upload_files(paths_to_upload, origin, container, names)
        return result

    def get_file_uri(self, origin, container, path, session=None):
        """get the sas uri of an artifact"""
        if container is None:
            raise UserErrorException("Cannot get URL for artifact with Null DataContainerID")
        res = self._execute_with_workspace_arguments(self._client.artifact.get_content_information,
                                                     origin=origin,
                                                     container=container,
                                                     path=path)
        return res.content_uri

    def get_file_by_artifact_id(self, artifact_id):
        """
        get sas uri of an artifact
        """
        # TODO change name to get file uri from artifact id
        # get SAS using get_content_info if id, else list sas by prefix
        # download sas to path
        [origin, container, path] = artifact_id.split("/", 2)
        local_path = os.path.abspath(path)
        return (local_path, self.get_file_uri(origin, container, path))

    def get_files_by_artifact_prefix_id(self, artifact_prefix_id):
        """
        get sas urls under a prefix artifact id
        """

        files_to_download = []
        # get SAS using get_content_info if id, else list sas by prefix
        # download sas to path
        [origin, container, prefix] = artifact_prefix_id.split("/", 2)
        self._logger.debug("Fetching files for prefix in {}, {}, {}".format(origin, container, prefix))
        dtos = self._execute_with_workspace_arguments(self._client.artifact.list_sas_by_prefix,
                                                      origin=origin,
                                                      container=container,
                                                      path=prefix,
                                                      is_paginated=True)
        for dto in dtos:
            path = dto.path
            local_path = path
            sas_uri = dto.content_uri
            files_to_download.append((local_path, sas_uri))
        return files_to_download

    def download_artifact(self, origin, container, path, output_file_path):
        """download artifact"""
        try:
            content_info = self._execute_with_workspace_arguments(self._client.artifact.get_content_information,
                                                                  origin, container, path)
            if not content_info:
                raise UserErrorException("Cannot find the artifact '{0}' in container '{1}'".format(path, container))
            uri = content_info.content_uri
        except HttpOperationError as operation_error:
            if operation_error.response.status_code == 404:
                existing_files = self.get_file_paths(origin, container)
                raise UserErrorException("File with path {0} was not found,\n"
                                         "available files include: "
                                         "{1}.".format(path, ",".join(existing_files)))
            else:
                raise
        download_file(uri, output_file_path, session=self.session)

    def download_artifact_contents_to_string(self, origin, container, path, encoding="utf-8"):
        """download metric stored as a json artifact"""
        if container is None:
            raise UserErrorException("DataContainerId is none so artifact contents cannot be found")
        try:
            content_info = self._execute_with_workspace_arguments(self._client.artifact.get_content_information,
                                                                  origin, container, path)
            if not content_info:
                raise UserErrorException("Cannot find the artifact '{0}' in container '{1}'".format(path, container))
            uri = content_info.content_uri
        except HttpOperationError as operation_error:
            if operation_error.response.status_code == 404:
                existing_files = self.get_file_paths(origin, container)
                raise UserErrorException("File with path {0} was not found,\n"
                                         "available files include: "
                                         "{1}.".format(path, ",".join(existing_files)))
            else:
                raise
        return download_file_stream(source_uri=uri, session=self.session, encoding=encoding)

    def get_file_paths(self, origin, container):
        """list artifact info"""
        artifacts = []
        if container is None:
            artifacts = []
            self._logger.debug("Container is set to none; setting artifacts to empty list")
        else:
            artifacts = self._execute_with_workspace_arguments(self._client.artifact.list_in_container,
                                                               origin=origin, container=container,
                                                               is_paginated=True)

        return map(lambda artifact_dto: artifact_dto.path, artifacts)

    def batch_ingest_from_sas(self, origin, container, container_sas,
                              container_uri, prefix, artifact_prefix):
        """get artifact info"""
        command = BatchArtifactContainerSasIngestCommand(container_sas,
                                                         container_uri,
                                                         prefix,
                                                         artifact_prefix)
        res = self._execute_with_workspace_arguments(self._client.artifact.batch_ingest_from_sas,
                                                     origin, container, command)
        return res

    def get_artifact_by_container(self, origin, container):
        """
        Get artifact names of a run by their run_id
        :param str container:  (required)
        :return: a generator of ~_restclient.models.ArtifactDto
        """
        if container is None:
            self._logger.debug("Container is set to none; returning empty list")
            return []
        return self._execute_with_workspace_arguments(self._client.artifact.list_in_container,
                                                      origin=origin,
                                                      container=container,
                                                      is_paginated=True)

    def get_artifact_uri(self, origin, container, attachment_name, is_async=False):
        """
        Get the uri of artifact being saved of a run by its run_id and name
        :param str container:  (required)
        :param str attachment_name: (required)
        :param is_async bool: execute request asynchronously
        :return:
            If is_async parameter is True,
            the request is called asynchronously.
            The method returns azureml._async.AsyncTask object
            If parameter is_async is False or missing,
            return ~_restclient.models.ArtifactContentInformationDto
        """
        return self._execute_with_workspace_arguments(self._client.artifact.get_content_information,
                                                      origin=origin,
                                                      container=container,
                                                      path=attachment_name,
                                                      is_async=is_async)

    def peek_artifact_content(self, source_uri):
        """
        Get the text of an artifact
        :param str source_uri:  (required)
        :return: Text of the source artifact
        """
        res = download_file(
            source_uri, max_retries=self._client.config.retry_policy.policy, stream=False)
        return res.text

    def upload_artifact_content(self, origin, container, attachment_name, content=None,
                                index=None, append=None, is_async=False):
        """
        Upload content to artifact of a run.
        :param str container:  (required)
        :param str attachment_name: (required)
        :param content: (optional)
        :param int index: block index in artifact to write to (optional)
        :param bool append: if true, content is appended to artifact (optional)
        :param is_async bool: execute request asynchronously (optional)
        :return:
            If is_async parameter is True,
            the request is called asynchronously.
            The method returns azureml._async.AsyncTask object
            If parameter is_async is False or missing,
            return: ~_restclient.models.ArtifactDto
        """
        if container is None:
            raise UserErrorException("Cannot upload content when DataContainerID is None")
        return self._execute_with_workspace_arguments(self._client.artifact.upload,
                                                      origin=origin,
                                                      container=container,
                                                      path=attachment_name,
                                                      content=content,
                                                      index=index,
                                                      append=append,
                                                      is_async=is_async)
