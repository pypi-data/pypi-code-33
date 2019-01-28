# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Estimators typically used in DNN training."""

from azureml.core._experiment_method import experiment_method
from azureml.core.conda_dependencies import CPU, GPU, HOROVOD_DEFAULT_VERSION, PYTORCH_PACKAGE_PREFIX,\
    TORCHVISION_PACKAGE_PREFIX, TORCHVISION_DEFAULT_VERSION, PYTORCH_DEFAULT_VERSION, CHAINER_PACKAGE_PREFIX,\
    DEFAULT_CHAINER_VERSION, CUPY_DEFAULT_VERSION
from azureml.exceptions import TrainingException

from .estimator import MMLBaseEstimator, MMLBaseEstimatorRunConfig, _estimator_submit_method


class _TensorFlowRunConfiguration(MMLBaseEstimatorRunConfig):
    """Extension of RunConfiguration specific to TensorFlow Estimators."""

    def __init__(self, compute_target=None, vm_size=None, vm_priority=None,
                 entry_script=None, script_params=None, node_count=None,
                 process_count_per_node=None, worker_count=None, parameter_server_count=None, distributed_backend=None,
                 use_gpu=None, use_docker=None, custom_docker_base_image=None, conda_packages=None, pip_packages=None,
                 environment_definition=None, inputs=None, source_directory_data_store=None):
        super(_TensorFlowRunConfiguration, self).__init__(
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

        self.tensorflow.worker_count = worker_count
        self.tensorflow.parameter_server_count = parameter_server_count


class TensorFlow(MMLBaseEstimator):
    """A TensorFlow Estimator is used to train a TensorFlow-based model.

    This estimator ensures that the TensorFlow framework is installed and configured correctly.

    :param source_directory: A local directory containing experiment configuration files.
    :type source_directory: str
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
    :param node_count: Number of nodes in the compute target used for training. Only AmlCompute compute target
        is supported for distributed training (node_count > 1).
    :type node_count: int
    :param process_count_per_node: When using MPI, number of processes per node.
    :type process_count_per_node: int
    :param worker_count: When using Parameter Server, the number of worker nodes.
    :type worker_count: int
    :param parameter_server_count: When using Parameter Server, the number of parameter server nodes.
    :type parameter_server_count: int
    :param distributed_backend: Communication backend for distributed training.
        Supported values: 'mpi' and 'ps'.
        'mpi': MPI/Horovod
        'ps': parameter server
        This parameter is required when any of node_count, process_count_per_node, worker_count, or
        parameter_server_count > 1.
        When node_count == 1 and process_count_per_node == 1, no backend will be used unless the backend
        is explicitly set. Only AmlCompute compute target is supported for distributed training.
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
    :param source_directory_data_store: Backing datastore for project share.
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
                 worker_count=1,
                 parameter_server_count=1,
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
        """Initialize a TensorFlow estimator.

        :param source_directory: A local directory containing experiment configuration files.
        :type source_directory: str
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
        :param node_count: Number of nodes in the compute target used for training. Only AmlCompute compute target
            is supported for distributed training (node_count > 1).
        :type node_count: int
        :param process_count_per_node: When using MPI, number of processes per node.
        :type process_count_per_node: int
        :param worker_count: When using Parameter Server, the number of worker nodes.
        :type worker_count: int
        :param parameter_server_count: When using Parameter Server, the number of parameter server nodes.
        :type parameter_server_count: int
        :param distributed_backend: Communication backend for distributed training.
            Supported values: 'mpi' and 'ps'.
            'mpi': MPI/Horovod
            'ps': parameter server
            This parameter is required when any of node_count, process_count_per_node, worker_count, or
            parameter_server_count > 1.
            When node_count == 1 and process_count_per_node == 1, no backend will be used unless the backend
            is explicitly set. Only AmlCompute compute target is supported for distributed training.
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
        :param source_directory_data_store: Backing datastore for project share.
        :type source_directory_data_store: str
        """
        self._validate_compute_target(compute_target)
        if not source_directory:
            source_directory = "."

        if not distributed_backend and (node_count > 1 or process_count_per_node > 1 or
                                        worker_count > 1 or parameter_server_count > 1):
            raise TrainingException("Distributed backend must be specified when node_count > 1 "
                                    "or process_count_per_node > 1 or worker_count > 1 or parameter_server_count > 1.")

        if distributed_backend and distributed_backend.lower() != "mpi" and distributed_backend.lower() != "ps":
            raise TrainingException("Unsupported distributed backend value: "
                                    "{}. Supported backends: mpi, ps.".format(distributed_backend))

        if pip_requirements_file_path:
            pip_packages = MMLBaseEstimator._merge_pip_packages_and_requirements(pip_requirements_file_path,
                                                                                 pip_packages)
        estimator_config = _TensorFlowRunConfiguration(compute_target, vm_size, vm_priority,
                                                       entry_script, script_params,
                                                       node_count, process_count_per_node, worker_count,
                                                       parameter_server_count, distributed_backend, use_gpu,
                                                       use_docker, custom_docker_base_image, conda_packages,
                                                       pip_packages, environment_definition, inputs,
                                                       source_directory_data_store)

        if not MMLBaseEstimator._is_user_managed_environment(environment_definition):
            self._add_conda_dependencies(conda_dependencies=estimator_config._get_conda_dependencies(),
                                         framework=estimator_config.framework,
                                         communicator=estimator_config.communicator,
                                         use_gpu=use_gpu)
            MMLBaseEstimator._update_conda_dependencies(estimator_config._get_conda_dependencies(),
                                                        conda_packages, pip_packages)

        super(self.__class__, self).__init__(source_directory, compute_target=compute_target,
                                             estimator_config=estimator_config)

    @staticmethod
    def _add_conda_dependencies(conda_dependencies, framework, communicator, use_gpu):
        conda_dependencies.add_tensorflow_pip_package(core_type=GPU if use_gpu else CPU)
        if framework == "Python" and (communicator == "OpenMpi" or communicator == "IntelMpi"):
            conda_dependencies.add_pip_package('horovod==' + HOROVOD_DEFAULT_VERSION)

    def _get_telemetry_values(self, func):
        telemetry_values = super(self.__class__, self)._get_telemetry_values(func)
        telemetry_values['numOfWorkers'] = self._estimator_config.tensorflow.worker_count
        telemetry_values['numOfPSNodes'] = self._estimator_config.tensorflow.parameter_server_count
        return telemetry_values


class _PyTorchRunConfiguration(MMLBaseEstimatorRunConfig):
    """Extension of RunConfiguration specific to PyTorch Estimators."""

    def __init__(self, compute_target=None, vm_size=None, vm_priority=None,
                 entry_script=None, script_params=None, node_count=None,
                 process_count_per_node=None, distributed_backend=None, use_gpu=None, use_docker=None,
                 custom_docker_base_image=None, conda_packages=None, pip_packages=None,
                 environment_definition=None, inputs=None, source_directory_data_store=None):

        super(_PyTorchRunConfiguration, self).__init__(
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


class PyTorch(MMLBaseEstimator):
    """A PyTorch Estimator is used to train a PyTorch specific experiment.

    :param source_directory: A local directory containing experiment configuration files.
    :type source_directory: str
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
    :param node_count: Number of nodes in the compute target used for training. If greater than 1, mpi
         distributed job will be run. Only AmlCompute compute target is supported for distributed jobs.
    :type node_count: int
    :param process_count_per_node: Number of processes per node. If greater than 1, mpi
         distributed job will be run. Only AmlCompute compute target is supported for distributed jobs.
    :type process_count_per_node: int
    :param distributed_backend: Communication backend for distributed training.
        Supported value: 'mpi'.
        'mpi': MPI/Horovod
        This parameter is required when node_count > 1 and/or process_count_per_node > 1.
        When node_count == 1 and process_count_per_node == 1, no backend will be used unless the backend
        is explicitly set. Only AmlCompute compute target is supported for distributed training.
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
    :param source_directory_data_store: Backing datastore for project share.
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
        """Initialize a PyTorch estimator.

        :param source_directory: A local directory containing experiment configuration files.
        :type source_directory: str
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
        :param node_count: Number of nodes in the compute target used for training. If greater than 1, mpi
             distributed job will be run. Only AmlCompute compute target is supported for distributed jobs.
        :type node_count: int
        :param process_count_per_node: Number of processes per node. If greater than 1, mpi
             distributed job will be run. Only AmlCompute compute target is supported for distributed jobs.
        :type process_count_per_node: int
        :param distributed_backend: Communication backend for distributed training.
            Supported value: 'mpi'.
            'mpi': MPI/Horovod
            This parameter is required when node_count > 1 and/or process_count_per_node > 1.
            When node_count == 1 and process_count_per_node == 1, no backend will be used unless the backend
            is explicitly set. Only AmlCompute compute target is supported for distributed training.
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
        :param source_directory_data_store: Backing datastore for project share.
        :type source_directory_data_store: Datastore
        """
        self._validate_compute_target(compute_target)

        if not distributed_backend and (node_count > 1 or process_count_per_node > 1):
            raise TrainingException("Distributed backend must be specified when node_count > 1 "
                                    "or process_count_per_node > 1.")

        if distributed_backend and distributed_backend.lower() != "mpi":
            raise TrainingException("Unsupported distributed backend value: "
                                    "{}. Supported backends: mpi.".format(distributed_backend))

        if pip_requirements_file_path:
            pip_packages = MMLBaseEstimator._merge_pip_packages_and_requirements(pip_requirements_file_path,
                                                                                 pip_packages)

        estimator_config = _PyTorchRunConfiguration(compute_target, vm_size, vm_priority,
                                                    entry_script, script_params,
                                                    node_count, process_count_per_node, distributed_backend, use_gpu,
                                                    use_docker, custom_docker_base_image, conda_packages,
                                                    pip_packages, environment_definition, inputs,
                                                    source_directory_data_store)
        if not MMLBaseEstimator._is_user_managed_environment(environment_definition):
            self._add_conda_dependencies(conda_dependencies=estimator_config._get_conda_dependencies(),
                                         framework=estimator_config.framework,
                                         communicator=estimator_config.communicator)
            MMLBaseEstimator._update_conda_dependencies(estimator_config._get_conda_dependencies(),
                                                        conda_packages, pip_packages)

        super(self.__class__, self).__init__(source_directory, compute_target=compute_target,
                                             estimator_config=estimator_config)

    @staticmethod
    def _add_conda_dependencies(conda_dependencies, framework, communicator):
        conda_dependencies.add_pip_package(PYTORCH_PACKAGE_PREFIX + "==" + PYTORCH_DEFAULT_VERSION)
        conda_dependencies.add_pip_package(TORCHVISION_PACKAGE_PREFIX + "==" + TORCHVISION_DEFAULT_VERSION)
        if framework == "Python" and (communicator == "OpenMpi" or communicator == "IntelMpi"):
            conda_dependencies.add_pip_package('horovod==' + HOROVOD_DEFAULT_VERSION)


class _ChainerRunConfiguration(MMLBaseEstimatorRunConfig):
    """Extension of RunConfiguration specific to Chainer Estimators."""

    def __init__(self, compute_target=None, vm_size=None, vm_priority=None,
                 entry_script=None, script_params=None, node_count=None,
                 process_count_per_node=None, distributed_backend=None, use_gpu=None, use_docker=None,
                 custom_docker_base_image=None, conda_packages=None, pip_packages=None,
                 environment_definition=None, inputs=None, source_directory_data_store=None):

        super(_ChainerRunConfiguration, self).__init__(
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


class Chainer(MMLBaseEstimator):
    """A Chainer Estimator is used to train a Chainer specific experiment.

    :param source_directory: A local directory containing experiment configuration files.
    :type source_directory: str
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
    :param node_count: Number of nodes in the compute target used for training. If greater than 1, mpi
         distributed job will be run. Only AmlCompute compute target is supported for distributed jobs.
    :type node_count: int
    :param process_count_per_node: Number of processes per node. If greater than 1, mpi
         distributed job will be run. Only AmlCompute compute target is supported for distributed jobs.
    :type process_count_per_node: int
    :param distributed_backend: Communication backend for distributed training.
        Supported value: 'mpi'.
        'mpi': MPI/Horovod
        This parameter is required when node_count > 1 and/or process_count_per_node > 1.
        When node_count == 1 and process_count_per_node == 1, no backend will be used unless the backend
        is explicitly set. Only AmlCompute compute target is supported for distributed training.
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
    :param source_directory_data_store: Backing datastore for project share.
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
        """Initialize a Chainer estimator.

        :param source_directory: A local directory containing experiment configuration files.
        :type source_directory: str
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
        :param node_count: Number of nodes in the compute target used for training. If greater than 1, mpi
             distributed job will be run. Only AmlCompute compute target is supported for distributed jobs.
        :type node_count: int
        :param process_count_per_node: Number of processes per node. If greater than 1, mpi
             distributed job will be run. Only AmlCompute compute target is supported for distributed jobs.
        :type process_count_per_node: int
        :param distributed_backend: Communication backend for distributed training.
            Supported value: 'mpi'.
            'mpi': MPI/Horovod
            This parameter is required when node_count > 1 and/or process_count_per_node > 1.
            When node_count == 1 and process_count_per_node == 1, no backend will be used unless the backend
            is explicitly set. Only AmlCompute compute target is supported for distributed training.
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
        :param source_directory_data_store: Backing datastore for project share.
        :type source_directory_data_store: Datastore
        """
        self._validate_compute_target(compute_target)

        if not distributed_backend and (node_count > 1 or process_count_per_node > 1):
            raise TrainingException("Distributed backend must be specified when node_count > 1 "
                                    "or process_count_per_node > 1.")

        if distributed_backend and distributed_backend.lower() != "mpi":
            raise TrainingException("Unsupported distributed backend value: "
                                    "{}. Supported backends: mpi.".format(distributed_backend))

        if pip_requirements_file_path:
            pip_packages = MMLBaseEstimator._merge_pip_packages_and_requirements(pip_requirements_file_path,
                                                                                 pip_packages)

        estimator_config = _ChainerRunConfiguration(compute_target, vm_size, vm_priority,
                                                    entry_script, script_params,
                                                    node_count, process_count_per_node, distributed_backend, use_gpu,
                                                    use_docker, custom_docker_base_image, conda_packages,
                                                    pip_packages, environment_definition, inputs,
                                                    source_directory_data_store)

        if not MMLBaseEstimator._is_user_managed_environment(environment_definition):
            self._add_conda_dependencies(conda_dependencies=estimator_config._get_conda_dependencies(),
                                         framework=estimator_config.framework,
                                         communicator=estimator_config.communicator)
            MMLBaseEstimator._update_conda_dependencies(estimator_config._get_conda_dependencies(),
                                                        conda_packages, pip_packages)

        super(self.__class__, self).__init__(source_directory, compute_target=compute_target,
                                             estimator_config=estimator_config)

    @staticmethod
    def _add_conda_dependencies(conda_dependencies, framework, communicator):
        conda_dependencies.add_pip_package(CHAINER_PACKAGE_PREFIX + "==" + DEFAULT_CHAINER_VERSION)
        if framework == "Python" and (communicator == "OpenMpi" or communicator == "IntelMpi"):
            conda_dependencies.add_pip_package(CUPY_DEFAULT_VERSION)  # Chainer uses CuPy as its GPU backend
