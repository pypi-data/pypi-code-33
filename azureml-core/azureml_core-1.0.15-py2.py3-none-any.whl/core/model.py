# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains class for retrieving a cloud representation of a Model object associated with a Workspace."""
import copy
import json
import logging
import os
import tarfile
import tempfile
import uuid
from collections import OrderedDict
from datetime import datetime

import requests
from azureml.exceptions import (WebserviceException, RunEnvironmentException,
                                AzureMLException, ModelNotFoundException)
from azureml._model_management._constants import MMS_SYNC_TIMEOUT_SECONDS
from azureml._model_management._constants import MMS_WORKSPACE_API_VERSION
from azureml._model_management._util import _get_mms_url
from azureml._model_management._util import get_paginated_results
from azureml._model_management._util import model_payload_template

from azureml._restclient.artifacts_client import ArtifactsClient
from azureml._restclient.assets_client import AssetsClient
from dateutil.parser import parse

from azureml._file_utils import download_file

module_logger = logging.getLogger(__name__)
MODELS_DIR = "azureml-models"


class Model(object):
    """Class for AzureML models.

    Model constructor is used to retrieve a cloud representation of a Model object associated with the provided
    workspace. Must provide either name or ID.

    :param workspace: The workspace object containing the Model to retrieve
    :type workspace: azureml.core.workspace.Workspace
    :param name: Will retrieve the latest model with the corresponding name, if it exists
    :type name: str
    :param id: Will retrieve the model with the corresponding ID, if it exists
    :type id: str
    :param tags: Optional, will filter based on the provided list, searching by either 'key' or '[key, value]'.
        Ex. ['key', ['key2', 'key2 value']]
    :type tags: :class:`list`
    :param properties: Optional, will filter based on the provided list, searching by either 'key' or
        '[key, value]'. Ex. ['key', ['key2', 'key2 value']]
    :type properties: :class:`list`
    :param version: When provided along with name, will get the specific version of the specified named model,
        if it exists
    :type version: int
    """

    _expected_payload_keys = ['createdTime', 'description', 'id', 'mimeType', 'name', 'kvTags',
                              'properties', 'unpack', 'url', 'version']

    def __init__(self, workspace, name=None, id=None, tags=None, properties=None, version=None):
        """Model constructor.

        The Model constructor is used to retrieve a cloud representation of a Model object associated with the provided
        workspace. Must provide either name or ID.

        :param workspace: The workspace object containing the Model to retrieve
        :type workspace: azureml.core.workspace.Workspace
        :param name: Will retrieve the latest model with the corresponding name, if it exists
        :type name: str
        :param id: Will retrieve the model with the corresponding ID, if it exists
        :type id: str
        :param tags: Optional, will filter based on the provided list, searching by either 'key' or '[key, value]'.
            Ex. ['key', ['key2', 'key2 value']]
        :type tags: :class:`list`
        :param properties: Optional, will filter based on the provided list, searching by either 'key' or
            '[key, value]'. Ex. ['key', ['key2', 'key2 value']]
        :type properties: :class:`list`
        :param version: When provided along with name, will get the specific version of the specified named model,
            if it exists
        :type version: int
        :return: A model object, if one is found in the provided workspace
        :rtype: Model
        :raises: ModelNotFoundException
        """
        self.created_time = None
        self.description = None
        self.id = None
        self.mime_type = None
        self.name = None
        self.tags = None
        self.properties = None
        self.unpack = None
        self.url = None
        self.version = None
        self.workspace = None
        self._auth = None
        self._mms_endpoint = None

        if workspace:
            get_response_payload = self._get(workspace, name, id, tags, properties, version)
            if get_response_payload:
                self._validate_get_payload(get_response_payload)
                self._initialize(workspace, get_response_payload)
            else:
                error_message = 'ModelNotFound: Model with '
                if id:
                    error_message += 'ID {}'.format(id)
                else:
                    error_message += 'name {}'.format(name)
                if tags:
                    error_message += ', tags {}'.format(tags)
                if properties:
                    error_message += ', properties {}'.format(properties)
                if version:
                    error_message += ', version {}'.format(version)
                error_message += ' not found in provided workspace'

                raise WebserviceException(error_message)

    def _initialize(self, workspace, obj_dict):
        """Initialize the Model instance.

        This is used because the constructor is used as a getter.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param obj_dict:
        :type obj_dict: dict
        :return:
        :rtype: None
        """
        created_time = parse(obj_dict['createdTime'])
        model_id = obj_dict['id']
        self.created_time = created_time
        self.description = obj_dict['description']
        self.id = model_id
        self.mime_type = obj_dict['mimeType']
        self.name = obj_dict['name']
        self.tags = obj_dict['kvTags']
        self.properties = obj_dict['properties']
        self.unpack = obj_dict['unpack']
        self.url = obj_dict['url']
        self.version = obj_dict['version']
        self.workspace = workspace
        self._auth = workspace._auth
        self._mms_endpoint = _get_mms_url(workspace) + '/models/{}'.format(model_id)

    @staticmethod
    def _get(workspace, name=None, id=None, tags=None, properties=None, version=None):
        """Retrieve the Model object from the cloud.

        :param workspace:
        :type workspace: workspace: azureml.core.workspace.Workspace
        :param name:
        :type name: str
        :param id:
        :type id: str
        :param tags:
        :type tags: :class:`list`
        :param properties:
        :type properties: :class:`list`
        :param version:
        :type version: int
        :return:
        :rtype: dict
        """
        if not id and not name:
            raise WebserviceException('Error, one of id or name must be provided.')

        headers = workspace._auth.get_authentication_header()
        params = {'api-version': MMS_WORKSPACE_API_VERSION, 'orderBy': 'CreatedAtDesc', 'count': 1}
        base_url = _get_mms_url(workspace)
        mms_url = base_url + '/models'

        if id:
            mms_url += '/{}'.format(id)
        else:
            params['name'] = name
        if tags:
            tags_query = ""
            for tag in tags:
                if type(tag) is list:
                    tags_query = tags_query + tag[0] + "=" + tag[1] + ","
                else:
                    tags_query = tags_query + tag + ","
            tags_query = tags_query[:-1]
            params['tags'] = tags_query
        if properties:
            properties_query = ""
            for prop in properties:
                if type(prop) is list:
                    properties_query = properties_query + prop[0] + "=" + prop[1] + ","
                else:
                    properties_query = properties_query + prop + ","
            properties_query = properties_query[:-1]
            params['properties'] = properties_query
        if version:
            params['version'] = version

        resp = requests.get(mms_url, headers=headers, params=params)
        if resp.status_code == 200:
            content = resp.content
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            model_payload = json.loads(content)
            if id:
                return model_payload
            else:
                paginated_results = get_paginated_results(model_payload, headers)
                if paginated_results:
                    return paginated_results[0]
                else:
                    return None
        elif resp.status_code == 404:
            return None
        else:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content))

    @staticmethod
    def register(workspace, model_path, model_name, tags=None, properties=None, description=None):
        """Register a model with the provided workspace.

        :param workspace: The workspace to register the model under
        :type workspace: workspace: azureml.core.workspace.Workspace
        :param model_path: Local path to model file or folder
        :type model_path: str
        :param model_name: The name to register the model with
        :type model_name: str
        :param tags: Dictionary of key value tags to give the model
        :type tags: dict[str, str]
        :param properties: Dictionary of key value properties to give the model. These properties cannot
            be changed after model creation, however new key value pairs can be added
        :type properties: dict[str, str]
        :param description: A text description of the model
        :type description: str
        :return: The registered model object
        :rtype: Model
        """
        artifact_client = ArtifactsClient.create(workspace)
        asset_client = AssetsClient.create(workspace)
        model_path = model_path.rstrip(os.sep)

        tar_name = model_name + '.tar.gz'
        tmpdir = tempfile.mkdtemp()
        model_tar_path = os.path.join(tmpdir, tar_name)
        dependency_tar = tarfile.open(model_tar_path, 'w:gz')
        dependency_tar.add(model_path, arcname=os.path.basename(model_path))
        dependency_tar.close()

        origin = 'LocalUpload'
        container = '{}-{}'.format(datetime.now().strftime('%y%m%dT%H%M%S'), str(uuid.uuid4())[:8])
        artifact_client.upload_artifact_from_path(model_tar_path, origin, container, tar_name)
        prefix_values = [{'prefix': '{}/{}/{}'.format(origin, container, tar_name)}]
        create_asset_result = asset_client.create_asset(model_name, prefix_values, None)
        asset = create_asset_result.content
        if isinstance(asset, bytes):
            asset = asset.decode('utf-8')
        asset_dict = json.loads(asset)
        asset_id = asset_dict['id']
        print('Registering model {}'.format(model_name))
        model = Model._register_with_asset(workspace, model_name, asset_id, tags, properties,
                                           description, unpack=True)
        return model

    @staticmethod
    def get_model_path(model_name, version=None, _workspace=None):
        """Return path to model.

        | The function will search for the model in the following locations
        | If version is None:
        | 1) download from remote to cache
        | 2) load from cache `azureml-models/$MODEL_NAME/$LATEST_VERSION/`
        | 3) ./$MODEL_NAME

        | If version is not None:
        | 1) load from cache `azureml-models/$MODEL_NAME/$LATEST_VERSION/`
        | 2) download from remote to cache

        :param model_name: The name of the model to retrieve
        :type model_name: str
        :param version: The version of the model to retrieve
        :type version: int
        :param _workspace: The workspace to retrieve a model from. Can't use remotely
        :type _workspace: azureml.core.workspace.Workspace
        :return: The path on disk to the model
        :rtype: str
        :raises: ModelNotFoundException
        """
        if version is not None and not isinstance(version, int):
            raise Exception("version should be an int")
        # check if in preauthenticated env
        active_workspace = _workspace
        try:
            # get workspace from submitted run
            from azureml.core.run import Run
            run = Run.get_context(allow_offline=False)
            module_logger.debug("Run is {}".format(run))
            experiment = run.experiment
            module_logger.debug("RH is {}".format(experiment))
            active_workspace = experiment.workspace_object
        except RunEnvironmentException as ee:
            message = "RunEnvironmentException: {}".format(ee)
            module_logger.debug(message)

        if version is not None:
            try:
                return Model._get_model_path_local(model_name, version)
            except ModelNotFoundException as ee:
                module_logger.debug("Model not find in local")
                if active_workspace is not None:
                    module_logger.debug("Getting model from remote")
                    return Model._get_model_path_remote(model_name, version, active_workspace)
                raise ee
        else:
            if active_workspace is not None:
                return Model._get_model_path_remote(model_name, version, active_workspace)
            else:
                return Model._get_model_path_local(model_name, version)

    @staticmethod
    def _get_model_path_local(model_name, version=None):
        """Get the local path to the Model.

        :param model_name:
        :type model_name: str
        :param version:
        :type version: int
        :return:
        :rtype: str
        """
        if version is not None and not isinstance(version, int):
            raise Exception("version should be an int")
        if model_name is None:
            raise ValueError("model_name is None")

        candidate_model_path = os.path.join(MODELS_DIR, model_name)
        # Probing azureml-models/<name>
        if not os.path.exists(candidate_model_path):
            return Model._get_model_path_local_from_root(model_name)
        else:
            # Probing azureml-models/<name> exists, probing version
            if version is None:
                latest_version = Model._get_latest_version(os.listdir(os.path.join(MODELS_DIR, model_name)))
                module_logger.debug("version is None. Latest version is {}".format(latest_version))
            else:
                latest_version = version
                module_logger.debug("Using passed in version {}".format(latest_version))

            candidate_model_path = os.path.join(candidate_model_path, str(latest_version))
            # Probing azureml-models/<name>/<version> exists
            if not os.path.exists(candidate_model_path):
                return Model._get_model_path_local_from_root(model_name)
            else:
                # Checking one file system node
                file_system_entries = os.listdir(candidate_model_path)
                if len(file_system_entries) != 1:
                    raise AzureMLException(
                        "Dir {} can contain only 1 file or folder. Found {}".format(candidate_model_path,
                                                                                    file_system_entries))

                candidate_model_path = os.path.join(candidate_model_path, file_system_entries[0])
                module_logger.debug("Found model path at {}".format(candidate_model_path))
                return candidate_model_path

    @staticmethod
    def _get_model_path_local_from_root(model_name):
        """Get the path to the Model from the root of the directory.

        :param model_name:
        :type model_name: str
        :return:
        :rtype: str
        """
        paths_in_scope = Model._paths_in_scope(MODELS_DIR)
        module_logger.debug("Checking root for {} because candidate dir {} had {} nodes: {}".format(
            model_name, MODELS_DIR, len(paths_in_scope), "\n".join(paths_in_scope)))

        candidate_model_path = model_name
        if os.path.exists(candidate_model_path):
            return candidate_model_path
        raise ModelNotFoundException("Model not found in cache or in root at ./{}. For more info,"
                                     "set logging level to DEBUG.".format(candidate_model_path))

    @staticmethod
    def _paths_in_scope(dir):
        """Get a list of paths in the provided directory.

        :param dir:
        :type dir: str
        :return:
        :rtype: :class:`list[str]`
        """
        paths_in_scope = []
        for root, dirs, files in os.walk(dir):
            for file in files:
                paths_in_scope.append(os.path.join(root, file))
        return paths_in_scope

    @staticmethod
    def _get_last_path_segment(path):
        """Get the last segment of the path.

        :param path:
        :type path: str
        :return:
        :rtype: str
        """
        last_segment = os.path.normpath(path).split(os.sep)[-1]
        module_logger.debug("Last segment of {} is {}".format(path, last_segment))
        return last_segment

    @staticmethod
    def _get_strip_prefix(prefix_id):
        """Get the prefix to strip from the path.

        :param prefix_id:
        :type prefix_id: str
        :return:
        :rtype: str
        """
        path = prefix_id.split("/", 2)[-1]
        module_logger.debug("prefix id {} has path {}".format(prefix_id, path))
        path_to_strip = os.path.dirname(path)
        module_logger.debug("prefix to strip from path {} is {}".format(path, path_to_strip))
        return path_to_strip

    def _get_asset(self):
        from azureml._restclient.assets_client import AssetsClient
        asset_id = self.url[len("aml://asset/"):]
        client = AssetsClient.create(self.workspace)
        asset = client.get_asset_by_id(asset_id)
        return asset

    def _get_sas_to_relative_download_path_map(self, asset):
        artifacts_client = ArtifactsClient.create(self.workspace)
        sas_to_relative_download_path = OrderedDict()
        for artifact in asset.artifacts:
            module_logger.debug("Asset has artifact {}".format(artifact))
            if artifact.id is not None:
                # download by id
                artifact_id = artifact.id
                module_logger.debug("Artifact has id {}".format(artifact_id))
                (path, sas) = artifacts_client.get_file_by_artifact_id(artifact_id)
                sas_to_relative_download_path[sas] = Model._get_last_path_segment(path)
            else:
                # download by prefix
                prefix_id = artifact.prefix
                module_logger.debug("Artifact has prefix id {}".format(prefix_id))
                paths = artifacts_client.get_files_by_artifact_prefix_id(prefix_id)
                prefix_to_strip = Model._get_strip_prefix(prefix_id)
                for path, sas in paths:
                    path = os.path.relpath(path, prefix_to_strip)  # same as stripping prefix from path per AK
                    sas_to_relative_download_path[sas] = path

        if len(sas_to_relative_download_path) == 0:
            raise AzureMLException("No files to download. Did you upload files?")
        module_logger.debug("sas_to_download_path map is {}".format(sas_to_relative_download_path))
        return sas_to_relative_download_path

    def _download_model_files(self, sas_to_relative_download_path, target_dir, exist_ok):
        for sas, path in sas_to_relative_download_path.items():
            target_path = os.path.join(target_dir, path)
            if not exist_ok and os.path.exists(target_path):
                raise AzureMLException(
                    "File already exists. To overwrite, set exist_ok to True. {}".format(target_path))
            sas_to_relative_download_path[sas] = target_path
            download_file(sas, target_path, stream=True)

        if self.unpack:
            # handle packed model
            tar_path = list(sas_to_relative_download_path.values())[0]
            file_paths = self._handle_packed_model_file(tar_path, target_dir, exist_ok)
        else:
            # handle unpacked model
            file_paths = sas_to_relative_download_path.values()
        return file_paths

    def _handle_packed_model_file(self, tar_path, target_dir, exist_ok):
        module_logger.debug("Unpacking model {}".format(tar_path))
        if not os.path.exists(tar_path):
            raise AzureMLException("tar file not found at {}. Paths in scope:\n{}".format(
                tar_path,
                "\n".join(Model._paths_in_scope(MODELS_DIR))))
        with tarfile.open(tar_path) as tar:
            if not exist_ok:
                for tar_file_path in tar.getnames():
                    candidate_path = os.path.join(target_dir, tar_file_path)
                    if os.path.exists(candidate_path):
                        raise AzureMLException(
                            "File already exists. To overwrite, set exist_ok to True. {}".format(candidate_path))
            tar.extractall(path=target_dir)
            tar_paths = tar.getnames()
        file_paths = [os.path.join(target_dir, os.path.commonprefix(tar_paths))]
        if os.path.exists(tar_path):
            os.remove(tar_path)
        else:
            module_logger.warning("tar_path to unpack is already deleted: {}".format(tar_path))
        return file_paths

    def download(self, target_dir=".", exist_ok=False, exists_ok=None):
        """Download model to target_dir of local file system.

        :param target_dir: defaults to current working directory
        :type target_dir: str
        :param exist_ok: replace downloaded dir/files if exists
        :type exist_ok: bool
        :param exists_ok:
        :type exists_ok:
        :return: string path to file or folder of model
        :rtype: str
        """
        if exists_ok is not None:
            if exist_ok is not None:
                raise Exception("Both exists_ok and exist_ok are set. Please use exist_ok only.")
            module_logger.warning("exists_ok is deprecated. Please use exist_ok")
            exist_ok = exists_ok

        # use model to get asset
        asset = self._get_asset()

        # use asset.artifacts to get files to download
        sas_to_relative_download_path = self._get_sas_to_relative_download_path_map(asset)

        # download files using sas
        file_paths = self._download_model_files(sas_to_relative_download_path, target_dir, exist_ok)
        if len(file_paths) == 0:
            raise AzureMLException(
                "Illegal state. Unpack={}, Paths in target_dir is {}".format(self.unpack, file_paths))
        model_path = os.path.commonpath(file_paths)
        return model_path

    @staticmethod
    def _get_model_path_remote(model_name, version, workspace):
        """Retrieve the remote path to the Model.

        :param model_name:
        :type model_name: str
        :param version:
        :type version: int
        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :return:
        :rtype: str
        """
        if version is not None and not isinstance(version, int):
            raise AzureMLException("version should be an int")
        # model -> asset
        from azureml.core import Workspace
        assert isinstance(workspace, Workspace)

        try:
            model = Model(workspace=workspace, name=model_name, version=version)
        except WebserviceException as e:
            if 'ModelNotFound' in e.message:
                models = Model.list(workspace)
                model_infos = sorted(["{}/{}".format(model.name, model.version) for model in models])
                raise ModelNotFoundException(
                    "Model/Version {}/{} not found in workspace. {}".format(model_name, version, model_infos))
            else:
                raise e

        # downloading
        version = model.version
        module_logger.debug("Found model version {}".format(version))
        target_dir = os.path.join(MODELS_DIR, model_name, str(version))
        model_path = model.download(target_dir, exist_ok=True)
        if not os.path.exists(model_path):
            items = os.listdir(target_dir)
            raise ModelNotFoundException(
                "Expected model path does not exist: {}. Found items in dir: {}".format(model_path, str(items)))
        return model_path

    @staticmethod
    def _register_with_asset(workspace, model_name, asset_id, tags=None, properties=None,
                             description=None, unpack=False):
        """Register the asset as a Model.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param model_name:
        :type model_name: str
        :param asset_id:
        :type asset_id: str
        :param tags:
        :type tags: dict[str, str]
        :param properties:
        :type properties: dict[str, str]
        :param description:
        :type description: str
        :param unpack:
        :type unpack: bool
        :return:
        :rtype: azureml.core.model.Model
        """
        headers = {'Content-Type': 'application/json'}
        headers.update(workspace._auth.get_authentication_header())
        params = {'api-version': MMS_WORKSPACE_API_VERSION}
        mms_host = _get_mms_url(workspace)
        model_url = mms_host + '/models'

        json_payload = copy.deepcopy(model_payload_template)
        json_payload['name'] = model_name
        json_payload['url'] = 'aml://asset/{}'.format(asset_id)
        json_payload['unpack'] = unpack
        if tags:
            try:
                if not isinstance(tags, dict):
                    raise AzureMLException("Tags must be a dict")
                tags = json.loads(json.dumps(tags))
            except ValueError:
                raise ValueError('Error with JSON serialization for tags, be sure they are properly formatted.')
            json_payload['kvTags'] = tags
        if properties:
            try:
                if not isinstance(properties, dict):
                    raise AzureMLException("Properties must be a dict")
                properties = json.loads(json.dumps(properties))
            except ValueError:
                raise ValueError('Error with JSON serialization for properties, be sure they are properly formatted.')
            json_payload['properties'] = properties
        if description:
            json_payload['description'] = description

        try:
            resp = requests.post(model_url, params=params, headers=headers, json=json_payload)
            resp.raise_for_status()
        except requests.ConnectionError:
            raise Exception('Error connecting to {}.'.format(model_url))
        except requests.exceptions.HTTPError:
            raise Exception('Received bad response from Model Management Service:\n'
                            'Response Code: {}\n'
                            'Headers: {}\n'
                            'Content: {}'.format(resp.status_code, resp.headers, resp.content))

        content = resp.content
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        model_dict = json.loads(content)

        return Model.deserialize(workspace, model_dict)

    @staticmethod
    def _get_latest_version(versions):
        """Get the latest version of the provided model versions.

        :param versions:
        :type versions: :class:`list[int]`
        :return:
        :rtype: int
        """
        if not len(versions) > 0:
            raise AzureMLException("versions is empty")
        versions = [int(version) for version in versions]
        version = max(versions)
        return version

    @staticmethod
    def list(workspace, name=None, tags=None, properties=None):
        """Retrieve a list of all models associated with the provided workspace, with optional filters.

        :param workspace: The workspace object to retrieve models from
        :type workspace: azureml.core.workspace.Workspace
        :param name: If provided, will only return models with the specified name, if any
        :type name: str
        :param tags: Will filter based on the provided list, by either 'key' or '[key, value]'.
            Ex. ['key', ['key2', 'key2 value']]
        :type tags: :class:`list`
        :param properties: Will filter based on the provided list, by either 'key' or '[key, value]'.
            Ex. ['key', ['key2', 'key2 value']]
        :type properties: :class:`list`
        :return: A list of models, optionally filtered
        :rtype: :class:`list[azureml.core.model.Model]`
        :raises: WebserviceException
        """
        headers = workspace._auth.get_authentication_header()
        params = {'api-version': MMS_WORKSPACE_API_VERSION}
        base_url = _get_mms_url(workspace)
        mms_url = base_url + '/models'

        if name:
            params['name'] = name
        if tags:
            tags_query = ""
            for tag in tags:
                if type(tag) is list:
                    tags_query = tags_query + tag[0] + "=" + tag[1] + ","
                else:
                    tags_query = tags_query + tag + ","
            tags_query = tags_query[:-1]
            params['tags'] = tags_query
        if properties:
            properties_query = ""
            for prop in properties:
                if type(prop) is list:
                    properties_query = properties_query + prop[0] + "=" + prop[1] + ","
                else:
                    properties_query = properties_query + prop + ","
            properties_query = properties_query[:-1]
            params['properties'] = properties_query

        try:
            resp = requests.get(mms_url, headers=headers, params=params)
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content))

        content = resp.content
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        model_payload = json.loads(content)
        paginated_results = get_paginated_results(model_payload, headers)
        return [Model.deserialize(workspace, model_dict) for model_dict in paginated_results]

    def serialize(self):
        """Convert this Model into a json serialized dictionary.

        :return: The json representation of this Model
        :rtype: dict
        """
        created_time = self.created_time.isoformat() if self.created_time else None
        return {'createdTime': created_time, 'description': self.description, 'id': self.id,
                'mimeType': self.mime_type, 'name': self.name, 'tags': self.tags,
                'properties': self.properties, 'unpack': self.unpack, 'url': self.url, 'version': self.version}

    @staticmethod
    def deserialize(workspace, model_payload):
        """Convert a json object into a Model object.

        Will fail if the provided workspace is not the workspace the model is registered under.

        :param workspace: The workspace object the model is registered under
        :type workspace: azureml.core.workspace.Workspace
        :param model_payload: A json object to convert to a Model object
        :type model_payload: dict
        :return: The Model representation of the provided json object
        :rtype: Model
        """
        Model._validate_get_payload(model_payload)
        model = Model(None)
        model._initialize(workspace, model_payload)
        return model

    def update(self, tags):
        """Perform an inplace update of the model.

        :param tags: A dictionary of tags to update the model with. With replace what currently exists
        :type tags: dict[str, str]
        :raises: WebserviceException
        """
        headers = {'Content-Type': 'application/json-patch+json'}
        headers.update(self._auth.get_authentication_header())
        params = {'api-version': MMS_WORKSPACE_API_VERSION}

        patch_list = []
        self.tags = tags
        patch_list.append({'op': 'replace', 'path': '/kvTags', 'value': self.tags})

        resp = requests.patch(self._mms_endpoint, headers=headers, params=params, json=patch_list,
                              timeout=MMS_SYNC_TIMEOUT_SECONDS)

        if resp.status_code != 200:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content))

    def add_tags(self, tags):
        """Add key value pairs to this model's tags dictionary.

        :param tags: The dictionary of tags to add
        :type tags: dict[str, str]
        :raises: WebserviceException
        """
        headers = {'Content-Type': 'application/json-patch+json'}
        headers.update(self._auth.get_authentication_header())
        params = {'api-version': MMS_WORKSPACE_API_VERSION}

        patch_list = []
        if self.tags is None:
            self.tags = copy.deepcopy(tags)
        else:
            for key in tags:
                if key in self.tags:
                    print("Replacing tag {} -> {} with {} -> {}".format(key, self.tags[key], key, tags[key]))
                self.tags[key] = tags[key]

        patch_list.append({'op': 'replace', 'path': '/kvTags', 'value': self.tags})

        resp = requests.patch(self._mms_endpoint, headers=headers, params=params, json=patch_list,
                              timeout=MMS_SYNC_TIMEOUT_SECONDS)

        if resp.status_code != 200:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content))

        print('Model tag add operation complete.')

    def remove_tags(self, tags):
        """Remove the specified keys from this model's dictionary of tags.

        :param tags: The list of keys to remove
        :type tags: :class:`list[str]`
        """
        headers = {'Content-Type': 'application/json-patch+json'}
        headers.update(self._auth.get_authentication_header())
        params = {'api-version': MMS_WORKSPACE_API_VERSION}

        patch_list = []
        if self.tags is None:
            print('Model has no tags to remove.')
            return
        else:
            if type(tags) is not list:
                tags = [tags]
            for key in tags:
                if key in self.tags:
                    del self.tags[key]
                else:
                    print('Tag with key {} not found.'.format(key))

        patch_list.append({'op': 'replace', 'path': '/kvTags', 'value': self.tags})

        resp = requests.patch(self._mms_endpoint, headers=headers, params=params, json=patch_list,
                              timeout=MMS_SYNC_TIMEOUT_SECONDS)

        if resp.status_code != 200:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content))

        print('Model tag remove operation complete.')

    def add_properties(self, properties):
        """Add key value pairs to this model's properties dictionary.

        :param properties: The dictionary of properties to add
        :type properties: dict[str, str]
        """
        headers = {'Content-Type': 'application/json-patch+json'}
        headers.update(self._auth.get_authentication_header())
        params = {'api-version': MMS_WORKSPACE_API_VERSION}

        patch_list = []
        if self.properties is None:
            self.properties = copy.deepcopy(properties)
        else:
            for key in properties:
                if key in self.properties:
                    print("Replacing property {} -> {} with {} -> {}".format(key, self.properties[key],
                                                                             key, properties[key]))
                self.properties[key] = properties[key]

        patch_list.append({'op': 'add', 'path': '/properties', 'value': self.properties})

        resp = requests.patch(self._mms_endpoint, headers=headers, params=params, json=patch_list,
                              timeout=MMS_SYNC_TIMEOUT_SECONDS)

        if resp.status_code != 200:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content))

        print('Model properties add operation complete.')

    def delete(self):
        """Delete this model from its associated workspace.

        :raises: WebserviceException
        """
        headers = self._auth.get_authentication_header()
        params = {'api-version': MMS_WORKSPACE_API_VERSION}

        resp = requests.delete(self._mms_endpoint, headers=headers, params=params)

        if resp.status_code != 200:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content))

    @staticmethod
    def _validate_get_payload(payload):
        """Validate the returned model payload.

        :param payload:
        :type payload: dict
        :return:
        :rtype: None
        """
        for payload_key in Model._expected_payload_keys:
            if payload_key not in payload:
                raise WebserviceException('Invalid model payload, missing {} for model:\n'
                                          '{}'.format(payload_key, payload))
