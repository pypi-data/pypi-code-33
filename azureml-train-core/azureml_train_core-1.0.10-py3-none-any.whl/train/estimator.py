# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Definition for the generic Estimator classes.

Estimators are the building block for training.  An estimator encapsulates the training code and parameters,
the compute resources and runtime environment for a particular training scenario.
"""

from os import path

from azureml.core._experiment_method import experiment_method
from azureml.core.runconfig import DEFAULT_GPU_IMAGE, DEFAULT_CPU_IMAGE, MPI_GPU_IMAGE, MPI_CPU_IMAGE, RunConfiguration
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.compute_target import _BatchAITarget
from azureml.core.compute import AmlCompute, HDInsightCompute
from azureml.core.experiment import Experiment
from azureml.core.script_run_config import ScriptRunConfig
from azureml.exceptions import ComputeTargetException, UserErrorException, TrainingException, \
    AzureMLException
from azureml._base_sdk_common.utils import convert_dict_to_list, merge_dict, merge_list, \
    list_remove_empty_items
from azureml._base_sdk_common import _ClientSessionId
from azureml.data.data_reference import DataReference
from azureml.data.azure_storage_datastore import AbstractAzureStorageDatastore
from azureml.train._telemetry_logger import _TelemetryLogger

import copy
import uuid
import json
from abc import ABC


class MMLBaseEstimator(ABC):
    """Abstract base class for all estimators."""

    # these instance variables are added here to enable the use of mock objects in testing
    _estimator_config = None
    run_config = None
    _compute_target = None

    def __init__(self, source_directory, *, compute_target, estimator_config=None):
        """Initialize properties common to all estimators.

        :param source_directory: The directory containing code or configuration for the estimator.
        :type source_directory: str
        :param compute_target: The ComputeTarget where training will happen. This can either be an object or the
            string "local".
        :type compute_target: azureml.core.compute_target.AbstractComputeTarget or str
        :param estimator_config: The run-time configuration used by the estimator.
        :type estimator_config: azureml.train.estimator.MMLBaseEstimatorRunConfig
        """
        self._source_directory = source_directory
        self._compute_target = compute_target
        self._estimator_config = estimator_config
        self._logger = _TelemetryLogger.get_telemetry_logger(__name__)

    @staticmethod
    def _validate_compute_target(compute_target):
        """Validate whether the compute_target object is a supported compute target.

        :param compute_target: The compute target where training will happen.
        :type compute_target: azureml.core.compute_target.AbstractComputeTarget
        """
        if compute_target and isinstance(compute_target, HDInsightCompute):
            raise ComputeTargetException("Unsupported compute target type. Type={}".format(type(compute_target)))

    @property
    def source_directory(self):
        """Return the path to the source directory.

        :return: The source directory path.
        :rtype: str
        """
        return self._source_directory

    @property
    def run_config(self):
        """Return `RunConfiguration` object for this estimator.

        :return: The run configuration.
        :rtype: azureml.train.estimator.MMLBaseEstimatorRunConfig
        """
        return self._estimator_config

    @property
    def conda_dependencies(self):
        """Return `conda_dependencies` object for this estimator.

        :return: The conda dependencies.
        :rtype: azureml.core.conda_dependencies.CondaDependencies
        """
        return self.run_config.environment.python.conda_dependencies

    @staticmethod
    def _merge_pip_packages_and_requirements(pip_requirements_file_path=None, pip_packages=None):
        if not pip_requirements_file_path:
            return pip_packages

        if not path.exists(pip_requirements_file_path):
            raise UserErrorException("Could not find the file {}.".format(pip_requirements_file_path))

        if not path.isfile(pip_requirements_file_path):
            raise UserErrorException("{} is not a valid file.".format(pip_requirements_file_path))

        requirements_list = []
        with open(pip_requirements_file_path) as in_file:
            requirements_list = in_file.read().splitlines()

        return CondaDependencies.merge_requirements(merge_list(requirements_list, pip_packages, True))

    def _submit(self, workspace, experiment_name, telemetry_values):
        # For flag based script arguments with store_action attr,
        # the expected input to estimator script_params is {"--v": ""}
        # The script_params gets translated into list as ["--v", ""].
        # Remove the empty entry from the list before submitting the experiment.
        with _TelemetryLogger.log_activity(self._logger,
                                           "train.estimator.submit",
                                           custom_dimensions=telemetry_values) as activity_logger:
            try:
                activity_logger.info("Submitting experiment through estimator...")
                experiment = Experiment(workspace, experiment_name)
                script_run_config = ScriptRunConfig(source_directory=self.source_directory,
                                                    script=self.run_config.script, arguments=self.run_config.arguments,
                                                    run_config=self.run_config, _telemetry_values=telemetry_values)
                experiment_run = experiment.submit(script_run_config)
                activity_logger.info("Experiment was submitted. RunId=%s", experiment_run.id)

                return experiment_run
            except AzureMLException as e:
                raise TrainingException(e.message, inner_exception=e) from None

    def _fit(self, workspace, experiment_name):
        telemetry_values = self._get_telemetry_values(self._fit)
        self._last_submitted_runconfig = self.run_config

        return self._submit(workspace, experiment_name, telemetry_values)

    def _override_params(self, script_params=None, inputs=None, source_directory_data_store=None):
        data_inputs = []
        if script_params:
            merged_script_params = merge_dict(self._estimator_config._script_params, script_params)
            # update estimator_config._script_params. This will be used to dedupe in hyperdrive
            self._estimator_config._script_params = merged_script_params
            self._estimator_config.arguments = MMLBaseEstimatorRunConfig._get_arguments(merged_script_params)
            data_inputs = MMLBaseEstimatorRunConfig._get_data_inputs(script_params)

        data_references = MMLBaseEstimatorRunConfig._get_data_references(inputs, data_inputs,
                                                                         source_directory_data_store)
        self._estimator_config.data_references = merge_dict(self._estimator_config.data_references,
                                                            data_references)
        if source_directory_data_store:
            self._estimator_config.source_directory_data_store = source_directory_data_store.name

    def _get_telemetry_values(self, func):
        telemetry_values = {}

        # client common...
        telemetry_values['amlClientType'] = 'azureml-sdk-train'
        telemetry_values['amlClientFunction'] = func.__name__
        telemetry_values['amlClientModule'] = self.__class__.__module__
        telemetry_values['amlClientClass'] = self.__class__.__name__
        telemetry_values['amlClientRequestId'] = str(uuid.uuid4())
        telemetry_values['amlClientSessionId'] = _ClientSessionId

        # estimator related...
        telemetry_values['scriptName'] = self.run_config.script
        telemetry_values['scriptArguments'] = ' '.join(str(arg) for arg in self.run_config.arguments)
        telemetry_values['useGpu'] = self.run_config.environment.docker.gpu_support
        telemetry_values['useDocker'] = self.run_config.environment.docker.enabled
        telemetry_values['useCustomDockerImage'] = \
            self.run_config.environment.docker.base_image not in [DEFAULT_CPU_IMAGE, DEFAULT_GPU_IMAGE,
                                                                  MPI_GPU_IMAGE, MPI_CPU_IMAGE]

        addCondaOrPipPackage = False
        if self.conda_dependencies:
            default_number_of_conda_packages, default_number_of_pip_packages = self.conda_dependencies. \
                get_default_number_of_packages()
            if (sum(1 for _ in self.conda_dependencies.conda_packages) > default_number_of_conda_packages) or \
                    (sum(1 for _ in self.conda_dependencies.pip_packages) > default_number_of_pip_packages):
                addCondaOrPipPackage = True
        telemetry_values['addCondaOrPipPackage'] = addCondaOrPipPackage

        # data references related...
        data_references = self.run_config.data_references
        count_value = {}
        count_value['total'] = len(data_references)
        for key, value in data_references.items():
            if value.mode not in count_value:
                count_value[value.mode] = 0
            count_value[value.mode] += 1
        telemetry_values['amlDataReferences'] = json.dumps(count_value)
        telemetry_values['amlDataReferencesEnabled'] = len(data_references) > 0

        # distributed training related...
        telemetry_values['nodeCount'] = self._estimator_config.node_count
        telemetry_values['processCountPerNode'] = self._estimator_config.mpi.process_count_per_node
        telemetry_values['distributed_backend'] = self._estimator_config._distributed_backend
        telemetry_values['computeTarget'] = self._compute_target if isinstance(self._compute_target, str) else \
            self._compute_target.type if self._compute_target else "amlcompute"
        telemetry_values['vmSize'] = self._estimator_config.amlcompute.vm_size if self._estimator_config.amlcompute \
            else None

        return telemetry_values

    @staticmethod
    def _clone_conda_dependencies(conda_dependencies_ref):
        conda_dependencies = CondaDependencies()

        for conda_channel in conda_dependencies.conda_channels:
            conda_dependencies.add_channel(conda_channel)

        for conda_pkg in conda_dependencies_ref.conda_packages:
            conda_dependencies.add_conda_package(conda_pkg)

        for pip_pkg in conda_dependencies_ref.pip_packages:
            conda_dependencies.add_pip_package(pip_pkg)

        return conda_dependencies

    @staticmethod
    def _update_conda_dependencies(conda_dependencies, conda_packages, pip_packages):
        if pip_packages:
            for pip_package in pip_packages:
                conda_dependencies.add_pip_package(pip_package)

        if conda_packages:
            for conda_dependency in conda_packages:
                conda_dependencies.add_conda_package(conda_dependency)

    @staticmethod
    def _update_docker_config(run_config,
                              custom_docker_base_image,
                              use_gpu,
                              framework,
                              communicator):
        # To set 'user_managed_dependencies = True' user should rely on environment_definition param
        run_config.environment.python.user_managed_dependencies = False
        if custom_docker_base_image:
            run_config.environment.docker.base_image = custom_docker_base_image
        else:
            if use_gpu:
                if framework == "Python" and communicator == "IntelMpi":
                    run_config.environment.docker.base_image = MPI_GPU_IMAGE
                else:
                    run_config.environment.docker.base_image = DEFAULT_GPU_IMAGE
            else:
                if framework == "Python" and communicator == "IntelMpi":
                    run_config.environment.docker.base_image = MPI_CPU_IMAGE
                else:
                    run_config.environment.docker.base_image = DEFAULT_CPU_IMAGE

        if use_gpu:
            run_config.environment.docker.gpu_support = True
            # this environment configuration is required to run a
            # distributed job with GPU support
            run_config.environment.environment_variables['NCCL_SOCKET_IFNAME'] = '^docker0'
        else:
            run_config.environment.docker.gpu_support = False

    @staticmethod
    def _update_environment_definition(conda_packages, custom_docker_base_image, environment_definition,
                                       pip_packages, run_config, use_gpu):
        run_config.environment = environment_definition
        is_user_manged_environment = MMLBaseEstimator._is_user_managed_environment(environment_definition)
        # check to fail early on conflicting params
        if is_user_manged_environment and pip_packages:
            raise TrainingException('If environment_definition parameter is specified with user managed '
                                    'python dependencies set to True, pip_packages parameter cannot '
                                    'be specified')
        if is_user_manged_environment and conda_packages:
            raise TrainingException('If environment_definition parameter is specified with user managed '
                                    'python dependencies set to True, conda_packages parameter cannot be specified')
        if custom_docker_base_image:
            raise TrainingException(
                'If environment_definition parameter is specified custom_docker_base_image parameter '
                'cannot be specified')
        if use_gpu:
            raise TrainingException('If environment_definition parameter is specified use_gpu '
                                    'parameter cannot be specified')

        # For user managed dependencies, set prepare environment to false and cached packages to false
        # Setting these two flags to false will help bypass image build and use the user provided custom docker.
        if environment_definition.python.user_managed_dependencies:
            run_config.environment.spark.precache_packages = False

        # Overriding run_config.environment_definition will set conda_dependencies to None.
        # Revert that change for user managed environments.
        if environment_definition.python.conda_dependencies is None:
            run_config.environment.python.conda_dependencies = CondaDependencies()

    @staticmethod
    def _is_user_managed_environment(environment_definition):
        if environment_definition and environment_definition.python is not None:
            return environment_definition.python.user_managed_dependencies

        return False


class MMLBaseEstimatorRunConfig(RunConfiguration):
    """
    Abstract base class for all Estimator run configs.

    :param compute_target: The ComputeTarget where training will happen. This can either be an object or the
        string "local".
    :type compute_target: azureml.core.compute_target.AbstractComputeTarget or str
    :param vm_size: The VM size of the compute target that will be created for the training.
        Supported values: Any Azure VM size. The list of available VM sizes are listed here.
        https://docs.microsoft.com/en-us/azure/cloud-services/cloud-services-sizes-specs
    :type vm_size: str
    :param vm_priority: The VM priority of the compute target that will be created for the training. If not
    specified, it will be defaulted to 'dedicated'.
        Supported values: 'dedicated' and 'lowpriority'.
        This takes effect only when the vm_size param is specified in the input.
    :type vm_priority: str
    :param entry_script: A string representing the relative path to the file used to start training.
    :type entry_script: str
    :param script_params: A dictionary containing parameters that will be passed as arguments to the entry_script.
    :type script_params: dict
    :param node_count: Number of nodes in the compute target used for training. Only BatchAI compute target
        is supported for distributed training (node_count > 1).
    :type node_count: int
    :param process_count_per_node: When using MPI as an execution backend, the number of processes per node.
    :type process_count_per_node: int
    :param distributed_backend: Communication backend for distributed training.
        Supported values: 'mpi' and 'ps'.
        'mpi': MPI/Horovod
        'ps': parameter server
        This parameter is required when any of node_count, process_count_per_node, worker_count, or
        parameter_server_count > 1.
        When node_count == 1 and process_count_per_node == 1, no backend will be used unless the backend
        is explicitly set. Only BatchAI compute target is supported for distributed training.
    :type distributed_backend: str
    :param use_gpu: A bool value indicating if the environment to run the experiment should support GPUs.
        If set to true, gpu-based default docker image will be used in the environment. If set to false, CPU based
        image will be used. Default docker images (CPU or GPU) will be used only if custom_docker_base_image
        parameter is not set. This setting is used only in docker enabled compute targets.
    :type use_gpu: bool
    :param use_docker: A bool value indicating if the environment to run the experiment should be docker-based.
    :type use_docker: bool
    :param custom_docker_base_image: The name of the docker image from which the image to use for training
        will be built. If not set, a default CPU based image will be used as the base image. Use this setting only
        for images available in public docker repositories. To use an image from a private docker repository,
        use environment_definition parameter instead.
    :type custom_docker_base_image: str
    :param conda_packages: List of strings representing conda packages to be added to the Python environment
        for the experiment.
    :type conda_packages: list
    :param pip_packages: List of strings representing pip packages to be added to the Python environment
        for the experiment.
    :type pip_packages: list
    :param environment_definition: The EnvironmentDefinition for the experiment. It includes
        PythonEnvironment and DockerEnvironment and environment variables. Any environment option not directly
        exposed through other parameters to the Estimator construction can be set using environment_definition
        parameter. If this parameter is specified, it will take precedence over other environment related
        parameters like use_gpu, custom_docker_base_image, conda_packages or pip_packages and errors will be
        reported on these invalid combinations.
    :type environment_definition: azureml.core.runconfig.EnvironmentDefinition
    :param inputs: Data references as input.
    :type inputs: list
    :param framework: The framework. Allowed values: "Python", "PySpark", "CNTK", "TensorFlow", "PyTorch",
        and "Chainer".
    :type framework: str
    :param source_directory_data_store: The backing data store for the project share.
    :type source_directory_data_store: str
    """

    # This instance variable is added here to enable the use of mock objects in testing.
    _script_params = None

    def __init__(self, compute_target, vm_size=None, vm_priority=None,
                 entry_script=None, script_params=None, node_count=None,
                 process_count_per_node=None, distributed_backend=None, use_gpu=None, use_docker=None,
                 custom_docker_base_image=None, conda_packages=None, pip_packages=None,
                 environment_definition=None, inputs=None, framework=None, source_directory_data_store=None):
        """
        Initialize the MMLBaseEstimatorRunConfig.

        :param compute_target: The ComputeTarget where training will happen. This can either be an object or the
            string "local".
        :type compute_target: azureml.core.compute_target.AbstractComputeTarget or str
        :param vm_size: The VM size of the compute target that will be created for the training.
            Supported values: Any Azure VM size. The list of available VM sizes are listed here.
            https://docs.microsoft.com/en-us/azure/cloud-services/cloud-services-sizes-specs
        :type vm_size: str
        :param vm_priority: The VM priority of the compute target that will be created for the training. If not
        specified, it will be defaulted to 'dedicated'.
         Supported values: 'dedicated' and 'lowpriority'.
         This takes effect only when the vm_size param is specified in the input.
        :type vm_priority: str
        :param entry_script: A string representing the relative path to the file used to start training.
        :type entry_script: str
        :param script_params: A dict containing parameters to the entry_script.
        :type script_params: dict
        :param node_count: Number of nodes in the compute target used for training. Only BatchAI compute target
            is supported for distributed training (node_count > 1).
        :type node_count: int
        :param process_count_per_node: When using MPI, number of processes per node.
        :type process_count_per_node: int
        :param distributed_backend: Communication backend for distributed training.
            Supported values: 'mpi' and 'ps'.
            'mpi': MPI/Horovod
            'ps': parameter server
            This parameter is required when any of node_count, process_count_per_node, worker_count, or
            parameter_server_count > 1.
            When node_count == 1 and process_count_per_node == 1, no backend will be used unless the backend
            is explicitly set. Only BatchAI compute target is supported for distributed training.
        :type distributed_backend: str
        :param use_gpu: A bool value indicating if the environment to run the experiment should support GPUs.
            If set to true, gpu-based default docker image will be used in the environment. If set to false, CPU based
            image will be used. Default docker images (CPU or GPU) will be used only if custom_docker_base_image
            parameter is not set. This setting is used only in docker enabled compute targets.
        :type use_gpu: bool
        :param use_docker: A bool value indicating if the environment to run the experiment should be docker-based.
        :type use_docker: bool
        :param custom_docker_base_image: The name of the docker image from which the image to use for training
            will be built. If not set, a default CPU based image will be used as the base image. Use this setting only
            for images available in public docker repositories. To use an image from a private docker repository,
            use environment_definition parameter instead.
        :type custom_docker_base_image: str
        :param conda_packages: List of strings representing conda packages to be added to the Python environment
            for the experiment.
        :type conda_packages: list
        :param pip_packages: List of strings representing pip packages to be added to the Python environment
            for the experiment.
        :type pip_packages: list
        :param environment_definition: The EnvironmentDefinition for the experiment. It includes
            PythonEnvironment and DockerEnvironment and environment variables. Any environment option not directly
            exposed through other parameters to the Estimator construction can be set using environment_definition
            parameter. If this parameter is specified, it will take precedence over other environment related
            parameters like use_gpu, custom_docker_base_image, conda_packages or pip_packages and errors will be
            reported on these invalid combinations.
        :type environment_definition: azureml.core.runconfig.EnvironmentDefinition
        :param inputs: Data references as input.
        :type inputs: list
        :param framework: The framework. Allowed values: "Python", "PySpark", "CNTK", "TensorFlow", "PyTorch",
        and "Chainer".
        :type framework: str
        :param source_directory_data_store: The backing data store for the project share.
        :type source_directory_data_store: Datastore
        """
        # normal initialization (i.e., not called due to override in fit)
        arguments = MMLBaseEstimatorRunConfig._get_arguments(script_params)
        data_inputs = MMLBaseEstimatorRunConfig._get_data_inputs(script_params)
        data_references = MMLBaseEstimatorRunConfig._get_data_references(inputs, data_inputs,
                                                                         source_directory_data_store)

        self._custom_docker_image = custom_docker_base_image
        self._distributed_backend = distributed_backend
        self._script_params = script_params

        if vm_size is None and compute_target is None:
            raise TrainingException("Either compute target or VM size should be specified.")

        if node_count > 1 and compute_target and \
                not (compute_target.type.lower() == _BatchAITarget._BATCH_AI_TYPE.lower() or
                     compute_target.type.lower() == AmlCompute._compute_type.lower()):
            raise TrainingException("Compute target should be Batch AI for distributed training (node_count > 1).")

        if node_count < 1:
            raise TrainingException("Node count should be at least 1.")
        if process_count_per_node < 1:
            raise TrainingException("Process count per node should be at least 1.")

        communicator = None
        if distributed_backend:
            # supported values: 'mpi' and 'ps'.
            if distributed_backend.lower() == "mpi":
                communicator = "IntelMpi"
            if distributed_backend.lower() == "ps":
                communicator = "ParameterServer"

        if communicator is None or communicator == "IntelMpi":
            framework = "Python"
        elif communicator == "ParameterServer":
            framework = "TensorFlow"
        else:
            # This is not the user input validation, since we've already validated the backend value
            # in each estimator. The purpose of this error is to quickly catch future regression bugs.
            raise TrainingException("Could not determine framework based on the backend value "
                                    "passed: {}.".format(communicator))

        super(MMLBaseEstimatorRunConfig, self).__init__(
            script=entry_script,
            arguments=arguments)

        # Super constructor overrides source_directory_data_store to None, so overriding it back here.
        # Now that we've added the datastore to the reference list, we only want the name
        if source_directory_data_store:
            self.source_directory_data_store = source_directory_data_store.name
        else:
            self.source_directory_data_store = None

        self.node_count = node_count
        self.amlcompute.vm_size = vm_size
        self.amlcompute.vm_priority = vm_priority
        # For a single run, aml compute will have the same node count as batchai.
        self.amlcompute._cluster_max_node_count = node_count
        self.mpi.process_count_per_node = process_count_per_node
        self.auto_prepare_environment = True
        self.environment.docker.enabled = use_docker
        self.target = compute_target if compute_target else "amlcompute"
        self.data_references = data_references
        self.framework = framework
        self.communicator = communicator
        # if environment_definition is specified, it will take precedence

        if environment_definition:
            MMLBaseEstimator._update_environment_definition(conda_packages, custom_docker_base_image,
                                                            environment_definition, pip_packages,
                                                            self, use_gpu)
        else:
            # Override scenario -- config being created for JIT estimator due to override in fit
            if use_docker is False and custom_docker_base_image:
                raise TrainingException('If use_docker parameter is set to false, custom_docker_base_image '
                                        'parameter is not allowed')
            MMLBaseEstimator._update_docker_config(run_config=self,
                                                   custom_docker_base_image=custom_docker_base_image,
                                                   use_gpu=use_gpu,
                                                   framework=framework,
                                                   communicator=communicator)

    @staticmethod
    def _get_data_references(inputs, data_inputs, source_directory_data_store):
        merged_inputs = merge_list(inputs, data_inputs, True)
        if source_directory_data_store:
            merged_inputs.append(source_directory_data_store)
        data_references = {}
        for item in merged_inputs:
            if isinstance(item, AbstractAzureStorageDatastore):
                item_ref = item._get_data_reference()
                data_references[item_ref.data_reference_name] = item_ref.to_config()
            elif isinstance(item, DataReference):
                data_references[item.data_reference_name] = item.to_config()
            else:
                raise UserErrorException("Type {0} is not supported for inputs.".format(type(item)))
        return data_references

    @staticmethod
    def _get_data_inputs(script_params):
        from azureml.data.azure_storage_datastore import AbstractAzureStorageDatastore
        data_inputs = []
        if script_params:
            for key in script_params:
                if isinstance(script_params[key], DataReference) \
                        or isinstance(script_params[key], AbstractAzureStorageDatastore):
                    data_inputs.append(script_params[key])
        return data_inputs

    @staticmethod
    def _get_arguments(script_params):
        from azureml.data.azure_storage_datastore import AbstractAzureStorageDatastore
        script_params_copy = copy.deepcopy(script_params)
        if script_params_copy:
            for key in script_params_copy:
                if isinstance(script_params_copy[key], DataReference):
                    script_params_copy[key] = str(script_params_copy[key])
                elif isinstance(script_params_copy[key], AbstractAzureStorageDatastore):
                    script_params_copy[key] = str(script_params_copy[key]._get_data_reference())
        return list_remove_empty_items(convert_dict_to_list(script_params_copy))

    def _get_conda_dependencies(self):
        return self.environment.python.conda_dependencies


def _estimator_submit_method(estimator, workspace, experiment_name, **kwargs):
    """
    Submit an experiment using a generic estimator.

    :param estimator: The estimator object.
    :type estimator: azureml.train.estimator.Estimator
    :param workspace: The workspace object.
    :type workspace: azureml.core.workspace.Workspace
    :param experiment_name: The name of the experiment.
    :type experiment_name: str
    :param kwargs: Additional parameters used to override estimator properties.
    :return: A ScriptRun object which can be queried for status, output path, model path, etc.
    :rtype: azureml.core.script_run.ScriptRun
    """
    override_params = False
    if kwargs:
        override_params = True

    script_params = kwargs.get("script_params", None)
    inputs = kwargs.get("inputs", None)
    source_directory_data_store = kwargs.get("source_directory_data_store", None)
    # TODO: Throw error if unexpected param?

    if override_params:
        estimator._original_config = copy.deepcopy(estimator._estimator_config)
        estimator._override_params(
            script_params=script_params,
            inputs=inputs,
            source_directory_data_store=source_directory_data_store)

    experiment_run = estimator._fit(workspace, experiment_name)

    if override_params:
        estimator._estimator_config = estimator._original_config

    return experiment_run


class Estimator(MMLBaseEstimator):
    """An Estimator is an algorithm which can be fit to data to produce a model.

    This simple estimator supports single-node as well as multi-node execution. Execution of the estimator will result
    in a model being produced which should be placed in the ScriptParams.OUTPUT_PATH folder.

    :param source_directory: A local directory containing experiment configuration files.
    :type source_directory: str
    :param compute_target:  The ComputeTarget where training will happen. This can either be an object or the
        string "local".
    :type compute_target: azureml.core.compute_target.AbstractComputeTarget or str
    :param vm_size: The VM size of the compute target that will be created for the training.
            Supported values: Any Azure VM size. The list of available VM sizes are listed here.
            https://docs.microsoft.com/en-us/azure/cloud-services/cloud-services-sizes-specs
    :type vm_size: str
    :param vm_priority: The VM priority of the compute target that will be created for the training. If not
    specified, it will be defaulted to 'dedicated'.
     Supported values: 'dedicated' and 'lowpriority'.
     This takes effect only when the vm_size param is specified in the input.
    :type vm_priority: str
    :param entry_script: A string representing the relative path to the file used to start training.
    :type entry_script: str
    :param script_params: A dictionary containing parameters to the entry_script.
    :type script_params: dict
    :param node_count: Number of nodes in the compute target used for training. If greater than 1, mpi
         distributed job will be run. Only BatchAI compute target is supported for distributed jobs.
    :type node_count: int
    :param process_count_per_node: Number of processes per node. If greater than 1, mpi
         distributed job will be run. Only BatchAI compute target is supported for distributed jobs.
    :type process_count_per_node: int
    :param distributed_backend: Communication backend for distributed training.
        Supported value: 'mpi'.
        'mpi': MPI/Horovod
        This parameter is required when node_count > 1 and/or process_count_per_node > 1.
        When node_count == 1 and process_count_per_node == 1, no backend will be used unless the backend
        is explicitly set. Only BatchAI compute target is supported for distributed training.
    :type distributed_backend: str
    :param use_gpu: A bool value indicating if the environment to run the experiment should support GPUs.
        If set to true, gpu-based default docker image will be used in the environment. If set to false, CPU based
        image will be used. Default docker images (CPU or GPU) will be used only if custom_docker_base_image
        parameter is not set. This setting is used only in docker enabled compute targets.
    :type use_gpu: bool
    :param use_docker: A bool value indicating if the environment to run the experiment should be docker-based.
    :type use_docker: bool
    :param custom_docker_base_image: The name of the docker image from which the image to use for training
        will be built. If not set, a default CPU based image will be used as the base image. Use this setting only
        for images available in public docker repositories. To use an image from a private docker repository,
        use environment_definition parameter instead.
    :type custom_docker_base_image: str
    :param conda_packages: List of strings representing conda packages to be added to the Python environment
        for the experiment.
    :type conda_packages: list
    :param pip_packages: List of strings representing pip packages to be added to the Python environment
        for the experiment.
    :type pip_packages: list
    :param pip_requirements_file_path: A string representing the full path to the pip requirements file. This
        can be provided in combination with the pip_packages parameter.
    :type pip_requirements_file_path: str
    :param environment_definition: The EnvironmentDefinition for the experiment. It includes
        PythonEnvironment and DockerEnvironment and environment variables. Any environment option not directly
        exposed through other parameters to the Estimator construction can be set using environment_definition
        parameter. If this parameter is specified, it will take precedence over other environment related
        parameters like use_gpu, custom_docker_base_image, conda_packages or pip_packages and errors will be
        reported on these invalid combinations.
    :type environment_definition: azureml.core.runconfig.EnvironmentDefinition
    :param inputs: Data references as input.
    :type inputs: list
    :param source_directory_data_store: The backing data store for the project share.
    :type source_directory_data_store: str
    """

    @experiment_method(submit_function=_estimator_submit_method)
    def __init__(self,
                 source_directory,
                 *,
                 compute_target=None,
                 vm_size=None,
                 vm_priority=None,
                 entry_script=None,
                 script_params=None,
                 node_count=1,
                 process_count_per_node=1,
                 distributed_backend=None,
                 use_gpu=False,
                 use_docker=True,
                 custom_docker_base_image=None,
                 conda_packages=None,
                 pip_packages=None,
                 pip_requirements_file_path=None,
                 environment_definition=None,
                 inputs=None,
                 source_directory_data_store=None):
        """Initialize the estimator.

        :param source_directory: A local directory containing experiment configuration files.
        :type source_directory: str
        :param compute_target:  The ComputeTarget where training will happen. This can either be an object or the
            string "local".
        :type compute_target: azureml.core.compute_target.AbstractComputeTarget or str
        :param vm_size: The VM size of the compute target that will be created for the training.
                Supported values: Any Azure VM size. The list of available VM sizes are listed here.
                https://docs.microsoft.com/en-us/azure/cloud-services/cloud-services-sizes-specs
        :type vm_size: str
        :param vm_priority: The VM priority of the compute target that will be created for the training. If not
        specified, it will be defaulted to 'dedicated'.
         Supported values: 'dedicated' and 'lowpriority'.
         This takes effect only when the vm_size param is specified in the input.
        :type vm_priority: str
        :param entry_script: A string representing the relative path to the file used to start training.
        :type entry_script: str
        :param script_params: A dictionary containing parameters to the entry_script.
        :type script_params: dict
        :param node_count: Number of nodes in the compute target used for training. If greater than 1, mpi
             distributed job will be run. Only BatchAI compute target is supported for distributed jobs.
        :type node_count: int
        :param process_count_per_node: Number of processes per node. If greater than 1, mpi
             distributed job will be run. Only BatchAI compute target is supported for distributed jobs.
        :type process_count_per_node: int
        :param distributed_backend: Communication backend for distributed training.
            Supported value: 'mpi'.
            'mpi': MPI/Horovod
            This parameter is required when node_count > 1 and/or process_count_per_node > 1.
            When node_count == 1 and process_count_per_node == 1, no backend will be used unless the backend
            is explicitly set. Only BatchAI compute target is supported for distributed training.
        :type distributed_backend: str
        :param use_gpu: A bool value indicating if the environment to run the experiment should support GPUs.
            If set to true, gpu-based default docker image will be used in the environment. If set to false, CPU based
            image will be used. Default docker images (CPU or GPU) will be used only if custom_docker_base_image
            parameter is not set. This setting is used only in docker enabled compute targets.
        :type use_gpu: bool
        :param use_docker: A bool value indicating if the environment to run the experiment should be docker-based.
            custom_docker_base_image (str): The name of the docker image from which the image to use for training
            will be built. If not set, a default CPU based image will be used as the base image. Use this setting only
            for images available in public docker repositories. To use an image from a private docker repository,
            use environment_definition parameter instead.
        :type use_docker: bool
        :param custom_docker_base_image: The name of the docker image from which the image to use for training
        will be built. If not set, a default CPU based image will be used as the base image. Use this setting only
        for images available in public docker repositories. To use an image from a private docker repository,
        use environment_definition parameter instead.
        :type custom_docker_base_image: str
        :param conda_packages: List of strings representing conda packages to be added to the Python environment
            for the experiment.
        :type conda_packages: list
        :param pip_packages: List of strings representing pip packages to be added to the Python environment
            for the experiment.
        :type pip_packages: list
        :param pip_requirements_file_path: A string representing the full path to the pip requirements file. This
            can be provided in combination with the pip_packages parameter.
        :type pip_requirements_file_path: str
        :param environment_definition: The EnvironmentDefinition for the experiment. It includes
            PythonEnvironment and DockerEnvironment and environment variables. Any environment option not directly
            exposed through other parameters to the Estimator construction can be set using environment_definition
            parameter. If this parameter is specified, it will take precedence over other environment related
            parameters like use_gpu, custom_docker_base_image, conda_packages or pip_packages and errors will be
            reported on these invalid combinations.
        :type environment_definition: azureml.core.runconfig.EnvironmentDefinition
        :param inputs: Data references as input.
        :type inputs: list
        :param source_directory_data_store: The backing data store for the project share.
        :type source_directory_data_store: Datastore
        """
        self._validate_compute_target(compute_target)
        if not source_directory:
            source_directory = "."

        if not distributed_backend and (node_count > 1 or process_count_per_node > 1):
            raise TrainingException("Distributed backend must be specified when node_count > 1 "
                                    "or process_count_per_node > 1.")

        if distributed_backend and distributed_backend.lower() != "mpi":
            raise TrainingException("Unsupported distributed backend value:" +
                                    "{}. Supported backends: mpi.".format(distributed_backend))

        if pip_requirements_file_path:
            pip_packages = MMLBaseEstimator._merge_pip_packages_and_requirements(pip_requirements_file_path,
                                                                                 pip_packages)
        estimator_config = MMLBaseEstimatorRunConfig(
            compute_target=compute_target,
            vm_size=vm_size,
            vm_priority=vm_priority,
            entry_script=entry_script,
            script_params=script_params,
            node_count=node_count,
            process_count_per_node=process_count_per_node,
            distributed_backend=distributed_backend,
            use_gpu=use_gpu,
            use_docker=use_docker,
            custom_docker_base_image=custom_docker_base_image,
            conda_packages=conda_packages,
            pip_packages=pip_packages,
            environment_definition=environment_definition,
            inputs=inputs,
            source_directory_data_store=source_directory_data_store)

        if not MMLBaseEstimator._is_user_managed_environment(environment_definition):
            MMLBaseEstimator._update_conda_dependencies(estimator_config._get_conda_dependencies(),
                                                        conda_packages,
                                                        pip_packages)

        super(self.__class__, self).__init__(source_directory, compute_target=compute_target,
                                             estimator_config=estimator_config)
