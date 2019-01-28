# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import os

import jsonpickle
from azureml.core.model import Model, MODELS_DIR

from azureml._restclient.constants import RUN_ORIGIN
from azureml._restclient.artifacts_client import ArtifactsClient
from azureml._restclient.assets_client import AssetsClient
from azureml._restclient.models import BatchArtifactContentInformationDto
from azureml.contrib.run.persistence import modeldata_handlers_store, model_handlers_store
from azureml.contrib.run.persistence.base_persistence import check_has_path, AML_MODELDATA_EXTENSION

module_logger = logging.getLogger(__name__)


class SaveResult:
    def __init__(self):
        """
        model_dir: directory that contains model and modeldata
        model_path: file or dir of model depending on model implementation
        modeldata: metadata for model
        modeldata_path: file path to modeldata
        """
        self.model_dir = None
        self.model_path = None
        self.modeldata = None
        self.modeldata_path = None


DEFAULT_ORIGIN = RUN_ORIGIN


def save_model_with_run_history(run_history, origin, container, model, model_name):
    """
    :return: SaveResult
    """
    save_result = save_model_to_local(container, model, model_name)

    workspace = run_history.workspace_object
    artifacts_client = ArtifactsClient.create(workspace)
    assets_client = AssetsClient.create(workspace)

    # upload files to artifact service
    upload_results = artifacts_client.upload_dir(save_result.model_dir, origin, container,
                                                 path_to_name_fn=_path_to_name)
    artifact_map, common_artifact_id_prefix = _get_artifact_info(
        upload_results)

    # Create asset
    artifacts_value = [
        {
            "prefix": common_artifact_id_prefix
        }
    ]
    # artifacts_value = []
    # for artifact in artifact_map.values():
    #     artifacts_value.append({"id": artifact.artifact_id})
    metadata_dict = {
        "azureml.modeldata": artifact_map[_path_to_name(save_result.modeldata_path)].artifact_id
    }
    project_id = run_history.name
    assets_client.create_asset(model_name,
                               artifacts_value,
                               metadata_dict=metadata_dict,
                               project_id=project_id,
                               run_id=container)

    return save_result


def _path_to_name(path):
    # removes MODELS_DIR/<container_id>
    return os.sep.join(path.split(os.sep)[2:])


def save_model_to_local(container, model, model_name):
    """
    :type container: name of dir to use in MODELS_DIR/<container>/<model_name>/<model files>
    :return: SaveResult
    """
    model_dir = os.path.join(MODELS_DIR, container, model_name)
    os.makedirs(model_dir, exist_ok=True)

    # Process modeldata
    modeldata_handler = modeldata_handlers_store.find_handler_by_model(model)
    if modeldata_handler is None:
        raise Exception("Modeldata handler not found")
    modeldata, modeldata_path = modeldata_handler.save(
        model, os.path.join(model_dir, model_name))
    save_result = SaveResult()
    save_result.modeldata = modeldata
    save_result.modeldata_path = modeldata_path
    save_result.model_dir = model_dir
    module_logger.info("Saved modeldata")

    # Process model
    model_handler = model_handlers_store.find_handler_by_model(model)
    if model_handler is not None:
        saved_model_path = model_handler.save(
            model, os.path.join(model_dir, model_name))
        save_result.model_path = saved_model_path
        module_logger.info("Saved model")

    return save_result


def _get_artifact_info(upload_results):
    artifact_map = {}
    for upload_result in upload_results:
        assert isinstance(upload_result, BatchArtifactContentInformationDto)
        for artifact_path, artifact in upload_result.artifacts.items():
            artifact_map[artifact_path] = artifact

    module_logger.debug("artifact map is: {}".format(artifact_map))
    artifact_ids = [artifact.artifact_id for artifact in artifact_map.values()]
    # common_artifact_id_prefix = os.path.commonprefix(artifact_ids)
    common_artifact_id_prefix = os.path.commonpath(artifact_ids)
    common_artifact_id_prefix = common_artifact_id_prefix.replace(
        os.path.sep, "/")
    return artifact_map, common_artifact_id_prefix


def load_model_from_local(model_name):
    # get aml dir
    model_dir = Model._get_model_path_local(model_name)
    model_dir = os.path.normpath(model_dir)
    modeldata_path = os.path.join(model_dir, "{}{}".format(
        model_name, AML_MODELDATA_EXTENSION))
    check_has_path(modeldata_path,
                   description="modeldata_path",
                   additional_description="Directory contains: {}".format(str(os.listdir(model_dir))))
    with open(modeldata_path, "rt") as modeldata_fp:
        json = jsonpickle.decode(modeldata_fp.read())
        modeldata = json
        assert (isinstance(modeldata, dict))

    # get model
    model_path = os.path.join(model_dir, model_name)
    check_has_path(model_path, description="model_path")
    model, modeldata = _load_model_with_metadata(model_path, modeldata)
    return model


def load_model(model_name, version=None, workspace=None):
    """
    :param model_name:
    :param version:
    :param workspace:
    :return: In memory model
    """
    model_path = Model.get_model_path(
        model_name, version, _workspace=workspace)
    module_logger.debug("Model path is {}".format(model_path))
    model = load_model_from_local(model_name)
    return model


def _list_local_model_versions(model_name):
    versions = os.listdir(os.path.join(MODELS_DIR, model_name))
    versions = sorted(versions)
    return versions


def _load_model_with_metadata(model_path, modeldata):
    name = modeldata["handler_name"]
    handler = model_handlers_store.find_handler_by_name(name)
    if handler is None:
        raise Exception("Load handler not found for metadata: {}".format(
            modeldata.handler_name))
    model = handler.load(model_path)
    return model, modeldata


def get_model_path(model_name, version=None, use_relative_path=False, _workspace=None):
    module_logger.warning(
        "Deprecated. persistence.get_model_path is moved to Model.get_model_path. Please update import.")
    return Model.get_model_path(model_name, version, _workspace)
