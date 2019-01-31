# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""python_script_step.py, module for adding a Python script as a node."""
from azureml.core.runconfig import RunConfiguration
from azureml.pipeline.core import PipelineStep
from azureml.pipeline.core.graph import ParamDef
from azureml.pipeline.core._module_builder import _FolderModuleBuilder
from azureml.pipeline.core._module_parameter_provider import _ModuleParameterProvider
import json


class PythonScriptStep(PipelineStep):
    r"""Add a step to run a Python script in a Pipeline.

    :param script_name: name of a python script (relative to source_directory)
    :type script_name: str
    :param name: Name of the step.  If unspecified, script_name will be used
    :type name: str
    :param arguments: List of command-line arguments
    :type arguments: list
    :param compute_target: Compute target to use
    :type compute_target: azureml.core.compute.DsvmCompute, azureml.core.compute.AmlCompute,
        azureml.core.compute.RemoteTarget, azureml.core.compute.HDIClusterTarget, str
    :param runconfig: Runconfig to use
    :type runconfig: azureml.core.runconfig.RunConfiguration
    :param runconfig_pipeline_params: Override runconfig properties at runtime using key-value pairs each with
                                    name of the runconfig property and PipelineParameter for that property
    :type runconfig_pipeline_params: {str: PipelineParameter}
    :param inputs: List of input port bindings
    :type inputs: list[azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
        azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData]
    :param outputs: List of output port bindings
    :type outputs: list[azureml.pipeline.core.builder.PipelineData, azureml.pipeline.core.graph.OutputPortBinding]
    :param params: Dictionary of name-value pairs. Registered as environment variables with "AML_PARAMETER\_"
    :type params: dict
    :param source_directory: folder that contains the script, conda env etc.
    :type source_directory: str
    :param allow_reuse: Whether the step should reuse previous results when run with the same settings/inputs.
        If this is false, a new run will always be generated for this step during pipeline execution.
    :type allow_reuse: bool
    :param version: Optional version tag to denote a change in functionality for the step
    :type version: str
    :param hash_paths: list of paths to hash to detect a change (script file is always hashed)
    :type hash_paths: list
    """

    def __init__(self, script_name, name=None, arguments=None, compute_target=None, runconfig=None,
                 runconfig_pipeline_params=None, inputs=None, outputs=None, params=None, source_directory=None,
                 allow_reuse=True, version=None, hash_paths=None):
        """
        Add a step to run a Python script in a Pipeline.

        :param script_name: Name of a python script (relative to source_directory)
        :type script_name: str
        :param name: Name of the step.  If unspecified, script_name will be used
        :type name: str
        :param arguments: List of command-line arguments to pass to the python script
        :type arguments: [str]
        :param compute_target: Compute target to use.  This may be a compute target object or the string name
            of a compute target on the workspace
        :type compute_target: DsvmCompute, AmlCompute, RemoteTarget, HDIClusterTarget, str
        :param runconfig: Runconfig to use.  If unspecified, a default runconfig will be created
        :type runconfig: RunConfiguration
        :param runconfig_pipeline_params: Override runconfig properties at runtime using key-value pairs each with
                                        name of the runconfig property and PipelineParameter for that property
        :type runconfig_pipeline_params: {str: PipelineParameter}
        :param inputs: List of input port bindings
        :type inputs: list[azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                     azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData]
        :param outputs: List of output port bindings
        :type outputs: list[azureml.pipeline.core.builder.PipelineData, azureml.pipeline.core.graph.OutputPortBinding]
        :param params: Dictionary of name-value pairs. Registered as environment variables with "AML_PARAMETER_"
        :type params: {str: str}
        :param source_directory: folder that contains the script, conda env etc.
        :type source_directory: str
        :param allow_reuse: Whether the step should reuse previous results when run with the same settings/inputs
        :type allow_reuse: bool
        :param version: Optional version tag to denote a change in functionality for the step
        :type version: str
        :param hash_paths: list of paths to hash to detect a change (script file is always hashed)
        :type hash_paths: [str]
        """
        if params is None:
            params = {}
        if name is None:
            name = script_name
        if script_name is None:
            raise ValueError("script_name is required")
        if not isinstance(script_name, str):
            raise ValueError("script_name must be a string")

        PipelineStep._process_pipeline_io(arguments, inputs, outputs)

        self._source_directory = source_directory
        self._hash_paths = hash_paths
        self._script_name = script_name
        self._compute_target = compute_target
        self._params = params
        self._module_param_provider = _ModuleParameterProvider()
        self._runconfig = runconfig
        self._runconfig_pipeline_params = runconfig_pipeline_params
        self._allow_reuse = allow_reuse
        self._version = version
        # these pipeline params automatically added to param def
        self._pipeline_params_implicit = PipelineStep._get_pipeline_parameters_implicit(arguments=arguments)
        # these pipeline params are not added to param def because they are already mapped to step param
        self._pipeline_params_in_step_params = PipelineStep._get_pipeline_parameters_step_params(params)
        PipelineStep._validate_params(self._params, self._runconfig_pipeline_params)
        self._pipeline_params_runconfig = PipelineStep._get_pipeline_parameters_runconfig(runconfig_pipeline_params)

        self._update_param_bindings()
        self._amlcompute_params = {}

        if self._hash_paths is None:
            self._hash_paths = []
        self._hash_paths.append(self._script_name)

        super().__init__(name, inputs, outputs, arguments, fix_port_name_collisions=True)

    def create_node(self, graph, default_datastore, context):
        """
        Create a node for python script step.

        :param graph: graph object
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: default datastore
        :type default_datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        :param context: context
        :type context: _GraphContext

        :return: The created node
        :rtype: azureml.pipeline.core.graph.Node
        """
        source_directory, hash_paths = self.get_source_directory_and_hash_paths(
            context, self._source_directory, self._script_name, self._hash_paths)

        input_bindings, output_bindings = self.create_input_output_bindings(self._inputs, self._outputs,
                                                                            default_datastore)

        param_def_dict = {}
        # initialize all the parameters for the module
        for module_provider_param in self._module_param_provider.get_params_list():
            param_def_dict[module_provider_param.name] = module_provider_param

        # user-provided params will override module-provider's params
        # this is needed to set run config params based on user specified value
        for param_name in self._params:
            param_def_dict[param_name] = ParamDef(name=param_name, set_env_var=True,
                                                  default_value=self._params[param_name],
                                                  env_var_override=self._get_parameter_with_prefix(param_name))

        param_defs = param_def_dict.values()

        PipelineStep._validate_runconfig_pipeline_params(self._runconfig_pipeline_params, param_defs)

        module_def = self.create_module_def(execution_type="escloud", input_bindings=input_bindings,
                                            output_bindings=output_bindings, param_defs=param_defs,
                                            allow_reuse=self._allow_reuse, version=self._version)

        module_builder = _FolderModuleBuilder(
            content_root=source_directory,
            hash_paths=hash_paths,
            context=context,
            module_def=module_def)

        node = graph.add_module_node(self.name, input_bindings, output_bindings, self._params,
                                     module_builder=module_builder)

        # module parameters not set in self._params are set on the node
        self._set_compute_params(node, context, self._params)

        # set pipeline parameters on node and on graph
        PipelineStep.\
            _configure_pipeline_parameters(graph,
                                           node,
                                           pipeline_params_implicit=self._pipeline_params_implicit,
                                           pipeline_params_in_step_params=self._pipeline_params_in_step_params,
                                           pipeline_params_runconfig=self._pipeline_params_runconfig)

        return node

    # automatically add pipeline params to param binding
    def _update_param_bindings(self):
        for pipeline_param in self._pipeline_params_implicit.values():
            if pipeline_param.name not in self._params:
                self._params[pipeline_param.name] = pipeline_param
            else:
                # example: if the user specifies a non-pipeline param and a pipeline param with same name
                raise Exception('Parameter name {0} is already in use'.format(pipeline_param.name))

    def _set_compute_params(self, node, context, params):
        """Compute params.

        :param node: node object
        :type node: Node
        :param context: context
        :type context: _GraphContext
        """
        target = self._compute_target
        if target is None:
            raise ValueError("compute target is required")

        if isinstance(target, str):
            target = context.get_target(target)

        if self._runconfig is None:
            self._runconfig = self._generate_default_runconfig(target)
        runconfig_params = self._set_runconfig(self._runconfig)

        # remove items from runconfig_params if they are specified in parameter in PythonScriptStep, it should be
        # removed from runconfig_params because it would overwrite the value of 'NodeCount' specified by the user
        # in 'params' with the value in 'runconfig' parameter in PythonScriptStep
        if params is not None:
            for param_name, param_value in params.items():
                if param_name in runconfig_params:
                    runconfig_params.pop(param_name)

        arguments = super().resolve_input_arguments(self._arguments, self._inputs, self._outputs, self._params)
        self._module_param_provider.set_params(node, target, self._script_name, arguments, runconfig_params,
                                               self._amlcompute_params)

    def set_amlcompute_params(self, native_shared_directory=None):
        """
        Set AmlCompute native shared directory param.

        :param native_shared_directory: native shared directory
        :type native_shared_directory: str
        """
        self._amlcompute_params = {'NativeSharedDirectory': native_shared_directory}

    def _set_runconfig(self, run_config=None):
        """Set runconfig for python script step.

        :param run_config: run config object
        :type run_config: RunConfig

        :return: run config params
        :rtype: RunConfig
        """
        runconfig_params = {}
        if isinstance(run_config, RunConfiguration):
            spark_maven_packages = []
            for package in run_config.environment.spark.packages:
                package_dict = {'artifact': package.artifact, 'group': package.group, 'version': package.version}
                spark_maven_packages.append(package_dict)

            spark_configuration = self._get_string_from_dictionary(run_config.spark.configuration.items())

            environment_variables = self._get_string_from_dictionary(
                run_config.environment.environment_variables.items())

            from azureml._execution import _commands
            serialized = _commands._serialize_run_config_to_dict(run_config)

            conda_dependencies = serialized['environment']['python']['condaDependencies']

            docker_arguments = None
            if len(run_config.environment.docker.arguments) > 0:
                docker_arguments = ",".join([str(x) for x in run_config.environment.docker.arguments])

            runconfig_params = {'Framework': run_config.framework,
                                'Communicator': run_config.communicator,
                                'DockerEnabled': run_config.environment.docker.enabled,
                                'BaseDockerImage': run_config.environment.docker.base_image,
                                'SharedVolumes': run_config.environment.docker.shared_volumes,
                                'DockerArguments': docker_arguments,
                                'SparkRepositories': run_config.environment.spark.repositories,
                                'SparkMavenPackages': spark_maven_packages,
                                'SparkConfiguration': spark_configuration,
                                'InterpreterPath': run_config.environment.python.interpreter_path,
                                'UserManagedDependencies': run_config.environment.python.user_managed_dependencies,
                                'GpuSupport': run_config.environment.docker.gpu_support,
                                'MaxRunDurationSeconds': run_config.max_run_duration_seconds,
                                'EnvironmentVariables': environment_variables,
                                'PrecachePackages': run_config.environment.spark.precache_packages,
                                'HistoryOutputCollection': run_config.history.output_collection,
                                'NodeCount': run_config.node_count,
                                'YarnDeployMode': run_config.hdi.yarn_deploy_mode,
                                'CondaDependencies': json.dumps(conda_dependencies),
                                'MpiProcessCountPerNode': run_config.mpi.process_count_per_node,
                                'TensorflowWorkerCount': run_config.tensorflow.worker_count,
                                'TensorflowParameterServerCount': run_config.tensorflow.parameter_server_count,
                                'AMLComputeName': run_config.amlcompute._name,
                                'AMLComputeVmSize': run_config.amlcompute.vm_size,
                                'AMLComputeVmPriority': run_config.amlcompute.vm_priority,
                                # location is not exposed in run config, will default to workspace location
                                'AMLComputeLocation': None,
                                'AMLComputeRetainCluster': run_config.amlcompute._retain_cluster,
                                'AMLComputeNodeCount': run_config.amlcompute._cluster_max_node_count
                                }
        return runconfig_params

    @staticmethod
    def _generate_default_runconfig(target):
        """Generate default runconfig for python script step.

        :param target: target
        :type target: None, str

        :return: runConfig
        :rtype: RunConfig
        """
        # name and target should already be validated as non None since they were passed to this class directly
        runconfig = RunConfiguration()
        if target.type == "amlcompute" or target.type == "remote" or target.type == "AmlCompute" \
                or target.type == "VirtualMachine":
            runconfig.environment.docker.enabled = True
        return runconfig

    @staticmethod
    def _get_string_from_dictionary(dictionary_items):
        """_Get string from dictionary.

        :param dictionary_items: dictionary items
        :type dictionary_items: list

        :return: string of dictionary items
        :rtype: str
        """
        items_list = []
        for item in dictionary_items:
            items_list.append("{0}={1}".format(item[0], item[1]))
        return ";".join(items_list)

    @staticmethod
    def _get_parameter_with_prefix(param_name):
        """Get parameter with prefix.

        :param param_name: param name
        :type param_name: str

        :return: parameter with prefix
        :rtype: str
        """
        return "AML_PARAMETER_{0}".format(param_name)
