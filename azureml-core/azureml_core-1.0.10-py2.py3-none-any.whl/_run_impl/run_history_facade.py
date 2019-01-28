# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# Start Temp request solution
import io
import os
import uuid
import logging
import imghdr
import json

from azureml.exceptions import AzureMLException, UserErrorException

from azureml._async.worker_pool import WorkerPool
from azureml._logging.chained_identity import ChainedIdentity
from azureml._restclient.models.create_run_dto import CreateRunDto
from azureml._restclient.assets_client import AssetsClient
from azureml._restclient.artifacts_client import ArtifactsClient
from azureml._restclient.metrics_client import MetricsClient
from azureml._restclient.run_client import RunClient
from azureml._restclient.experiment_client import ExperimentClient
from azureml._restclient.service_context import ServiceContext

from azureml.core.model import Model

STATUS_KEY = "status"
RUN_NAME_DELIM = ">"

module_logger = logging.getLogger(__name__)


class RunHistoryFacade(ChainedIdentity):
    _worker_pool = None

    def __init__(self, experiment, run_id, origin,
                 user_agent=None, worker_pool=None, _batch_upload_metrics=True, **kwargs):
        """
        :param experiment: The experiment object.
        :type experiment: azureml.core.exepriment.Experiment
        :param run_id:
        :type run_id: str
        :param origin:
        :type origin: str
        :param worker_pool:
        :type worker_pool: azureml._async.worker_pool.WorkerPool
        :param user_agent:
        :type user_agent: str
        :param data_container_id:
        :type data_container_id: str
        """
        super(RunHistoryFacade, self).__init__(**kwargs)
        self._experiment = experiment
        self._origin = origin
        self._run_id = run_id
        self._data_container_id = None

        self.worker_pool = worker_pool if worker_pool is not None else RunHistoryFacade._get_worker_pool()
        base_kwargs = {"user_agent": user_agent, "worker_pool": worker_pool, "_parent_logger": self._logger}

        workspace_id = None
        try:
            workspace_id = experiment.workspace._workspace_id
        except Exception as e:
            self._logger.debug("Failed to load workspace id with auth {}".format(
                experiment.workspace._auth_object))

        service_context = ServiceContext(experiment.workspace.subscription_id,
                                         experiment.workspace.resource_group,
                                         experiment.workspace.name,
                                         workspace_id,
                                         experiment.workspace._auth_object)

        self.run = RunClient(service_context, self._experiment.name, self._run_id, **base_kwargs)

        self.assets = AssetsClient(service_context, **base_kwargs)

        self.artifacts = ArtifactsClient(service_context, **base_kwargs)

        self.metrics = MetricsClient(service_context, self._experiment.name, self._run_id,
                                     use_batch=_batch_upload_metrics, **base_kwargs)

    @classmethod
    def _get_worker_pool(cls):
        if cls._worker_pool is None:
            cls._worker_pool = WorkerPool(_parent_logger=module_logger)
            module_logger.debug("Created a static thread pool for {} class".format(cls.__name__))
        else:
            module_logger.debug("Access an existing static threadpool for {} class".format(cls.__name__))
        return cls._worker_pool

    @staticmethod
    def target_name():
        return "sdk"

    @staticmethod
    def create_run(experiment, name=None, run_id=None):
        """

        :param experiment:
        :type experiment: azureml.core.experiment.Experiment
        :param name:
        :param run_id:
        :return:
        """
        run_id = RunHistoryFacade.create_run_id(run_id)
        client = RunClient.create(experiment.workspace,
                                  experiment.name,
                                  run_id)
        if name is None:
            name = "run_{}".format(run_id)
        # TODO what should target be set to?
        # Can target be used to differentiate Run from ExperimentRun
        run_dto = client.create_run(run_id=run_id,
                                    target=RunHistoryFacade.target_name(),
                                    run_name=name)
        return run_dto

    @staticmethod
    def create_run_id(run_id=None):
        return run_id if run_id else str(uuid.uuid4())

    @classmethod
    def chain_names(cls, name, child_name):
        name = name if name else ""
        child_name = child_name if child_name else ""
        return "{}{}{}".format(name, RUN_NAME_DELIM, child_name)

    def get_run(self):
        dto = self.run.get_run()
        return dto

    def get_runstatus(self):
        return self.run.get_runstatus()

    def get_status(self):
        run_dto = self.run.get_run()
        return run_dto.status

    def set_tags(self, tags):
        sanitized_tags = self._sanitize_tags(tags)
        create_run_dto = CreateRunDto(run_id=self._run_id, tags=sanitized_tags)
        self.run.patch_run(create_run_dto)

    def set_tag(self, key, value):
        tags = {key: value}
        return self.set_tags(tags)

    def get_tags(self):
        run_dto = self.get_run()
        return run_dto.tags

    def add_properties(self, properties):
        sanitized_props = self._sanitize_tags(properties)
        create_run_dto = CreateRunDto(run_id=self._run_id, properties=sanitized_props)
        self.run.patch_run(create_run_dto)

    def get_properties(self):
        run_dto = self.get_run()
        return run_dto.properties

    def log_scalar(self, name, value, description=""):
        """Log scalar number as a metric score"""
        self.metrics.log_scalar(name, value, description=description)

    def log_list(self, name, value, description=""):
        """Log list of scalar numbers as a metric score"""
        self.metrics.log_list(name, value, description=description)

    def log_row(self, name, value, description=""):
        """Log single row of a table as a metric score"""
        self.metrics.log_row(name, value, description=description)

    def log_table(self, name, value, description=""):
        """Log table as a metric score"""
        self.metrics.log_table(name, value, description=description)

    def log_confusion_matrix(self, name, value, description=""):
        """Log confusion matrix as a metric score"""
        self.log_to_artifact(name, value)

        uri = self._build_artifact_uri(name)
        self.metrics.log_confusion_matrix(name, data_location=uri, description=description)

    def log_accuracy_table(self, name, value, description=""):
        """Log accuracy table as a metric score"""
        self.log_to_artifact(name, value)

        uri = self._build_artifact_uri(name)
        self.metrics.log_accuracy_table(name, data_location=uri, description=description)

    def log_residuals(self, name, value, description=""):
        """Log accuracy table as a metric score"""
        self.log_to_artifact(name, value)

        uri = self._build_artifact_uri(name)
        self.metrics.log_residuals(name, data_location=uri, description=description)

    def log_predictions(self, name, value, description=""):
        """Log accuracy table as a metric score"""
        self.log_to_artifact(name, value)

        uri = self._build_artifact_uri(name)
        self.metrics.log_predictions(name, data_location=uri, description=description)

    def log_to_artifact(self, name, value):
        metric_json = json.dumps(value)
        stream = io.BytesIO(metric_json.encode('utf-8'))
        self.artifacts.upload_artifact(stream, self._origin, self._data_container_id, name)

    def _build_artifact_uri(self, name):
        return 'aml://artifactId/{}/{}/outputs/{}'.format(self._origin, self._data_container_id, name)

    def _save_mpl_plot(self, name, plot):
        ext = "png"
        artifact_path = "{}.{}".format(name, ext)
        stream = io.BytesIO()
        try:
            plot.savefig(stream, format=ext)
            stream.seek(0)
            self._upload_image(artifact_path, stream, ext)
        except AttributeError as attribute_error:
            raise AzureMLException("Invalid plot, must be matplotlib.pyplot", inner_exception=attribute_error)
        finally:
            stream.close()
        return artifact_path

    def _save_img_path(self, path):
        image_type = imghdr.what(path)
        if image_type is not None:
            self._upload_image(path, path, image_type)
        else:
            raise AzureMLException("The path provided points to a malformed image file")
        return path

    def _upload_image(self, path, artifact, ext):
        return self.artifacts.upload_artifact(artifact, self._origin, self._data_container_id, path,
                                              content_type="image/{}".format(ext))

    def log_image(self, name, path=None, plot=None):
        if path is not None and plot is not None:
            raise AzureMLException("Invalid parameters, path and plot were both"
                                   "provided, only one at a time is supported")
        elif path is None and plot is None:
            raise AzureMLException("Invalid parameters, one of path and plot "
                                   "is required as input")
        else:
            artifact_path = (self._save_img_path(path)
                             if path is not None
                             else self._save_mpl_plot(name, plot))
            aml_artifact_uri = "aml://artifactId/{0}".format(artifact_path)
            return self.metrics._log_image(name, aml_artifact_uri)

    @staticmethod
    def get_runs(experiment, **kwargs):
        """
        :param experiment:
        :type experiment: azureml.core.experiment.Experiment
        :return:
        """
        client = ExperimentClient.create(experiment.workspace,
                                         experiment.name)
        return client.get_runs(**kwargs)

    def get_descendants(self, root_run_id, recursive, **kwargs):
        # Adapter for generator until get_child_runs natively returns a generator of the appropriate
        # subtree
        children = self.run.get_child_runs(root_run_id, recursive=recursive, **kwargs)
        for child in children:
            yield child

    def register_model(self, model_name, model_path=None, tags=None, properties=None, asset_id=None):
        """
        Register a model with AML
        :param model_name: model name
        :type model_name: str
        :param model_path: relative cloud path to model from outputs/ dir. When model_path is None, model_name is path.
        :type model_path: str
        :param tags: Dictionary of key value tags to give the model
        :type tags: dict[str, str]
        :param properties: Dictionary of key value properties to give the model. These properties cannot
            be changed after model creation, however new key value pairs can be added
        :type properties: dict[str, str]
        :param asset_id: id of existing asset
        :type asset_id: str
        :rtype: azureml.core.model.Model
        """
        if model_path is None:
            model_path = model_name
        model_path = os.path.normpath(model_path)
        model_path = model_path.replace(os.sep, '/')

        if self._data_container_id is None:
            raise UserErrorException("Data Container ID cannot be null for run with ID {0}".format(self._run_id))

        artifacts = [{"prefix": "ExperimentRun/{}/{}".format(self._data_container_id, model_path)}]

        metadata_dict = None
        if asset_id is None:
            res = self.assets.create_asset(model_name,
                                           artifacts,
                                           metadata_dict=metadata_dict,
                                           run_id=self._run_id)
            asset_id = res.json()["id"]
        else:
            # merge asset tags and properties with those from model
            asset = self.assets.get_asset_by_id(asset_id)
            properties = self._merge_dict(tags, asset.tags)
            properties = self._merge_dict(properties, asset.properties)
        model = self.register_asset(model_name, asset_id, tags=tags, properties=properties)
        return model

    @staticmethod
    def _merge_dict(dict_aa, dict_bb):
        """
            Returns merged dict that contains dict_aa and any item in dict_bb not in dict_aa
        :param dict_aa:
        :param dict_bb:
        """
        if dict_aa is None:
            return dict_bb.copy()
        elif dict_bb is None:
            return dict_aa.copy()
        else:
            result = dict_aa.copy()
            result.update(dict_bb)
            return result

    def register_asset(self, model_name, asset_id, tags=None, properties=None):
        return Model._register_with_asset(self._experiment.workspace, model_name, asset_id,
                                          tags=tags,
                                          properties=properties)

    def create_child_run(self, name, target, child_name=None, run_id=None):
        """
        Creates a child run
        :param name: Name of the current run
        :type name: str:
        :param child_name: Optional name to set for the child run object
        :type child_name: str:
        :param run_id: Optional run_id to set for run, otherwise defaults
        :type run_id: str:
        """
        child_run_id = run_id if run_id else RunHistoryFacade.create_run_id(run_id)
        child_name = RunHistoryFacade.chain_names(name, child_name)
        child = self.run.create_child_run(child_run_id, target=target, run_name=child_name)
        return child

    def start(self):
        """
        Changes the state of the current run to started
        """
        self.run.post_event_start()

    def complete(self):
        """
        Changes the state of the current run to completed
        """
        self.flush()
        self.run.post_event_completed()

    def fail(self):
        """
        Changes the state of the current run to failed
        """
        self.flush()
        self.run.post_event_failed()

    def flush(self, timeout_seconds=300):
        self.metrics.flush(timeout_seconds=timeout_seconds)

    def _sanitize_tags(self, tag_or_prop_dict):
        # type: (...) -> {str}
        ret_tags = {}
        # dict comprehension would be nice but logging suffers without more functions
        for key, val in tag_or_prop_dict.items():
            if not isinstance(val, (str, type(None))):  # should be six.str/basestring or something
                self._logger.warn('Converting non-string tag to string: (%s: %s)', key, val)
                ret_tags[key] = str(val)
            else:
                ret_tags[key] = val
        return ret_tags
