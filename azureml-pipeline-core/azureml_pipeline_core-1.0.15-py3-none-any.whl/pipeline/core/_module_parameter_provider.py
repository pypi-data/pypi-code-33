# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import ABC, abstractmethod
from azureml.pipeline.core.graph import ParamDef
from azureml.core.compute_target import _BatchAITarget
from azureml.core.compute import RemoteCompute, HDInsightCompute
from azureml.core.compute import DsvmCompute, AmlCompute


class _ComputeTargetPropertyMapper(ABC):
    """
    Maps compute target property
    """
    @abstractmethod
    def get_params_list(self):
        pass

    @abstractmethod
    def set_target_params(self, node, target, runconfig_params, compute_params):
        pass

    @staticmethod
    def set_common_target_params(node, target):
        node.get_param('Target').set_value(target.name)
        node.get_param('TargetType').set_value(target.type)

    @staticmethod
    def merge_compute_params(node, default_params, compute_params):
        for param in default_params.keys():
            if param in compute_params and compute_params[param] is not None:
                node.get_param(param).set_value(compute_params[param])
            else:
                node.get_param(param).set_value(default_params[param])

    @staticmethod
    def set_runconfig_params(node, runconfig_params):
        for param in runconfig_params.keys():
            if runconfig_params[param] is not None:
                node.get_param(param).set_value(runconfig_params[param])


class _MlcComputeTargetPropertyMapper(_ComputeTargetPropertyMapper):
    """
    Maps Mlc compute target property
    """
    def get_params_list(self):
        return []

    def set_target_params(self, node, target, runconfig_params=None, compute_params=None):
        self.merge_compute_params(node, self.get_default_values(), {})
        self.set_runconfig_params(node, runconfig_params)
        node.get_param('Target').set_value(target.name)
        node.get_param('TargetType').set_value("mlc")
        if isinstance(target, AmlCompute):
            node.get_param('MLCComputeType').set_value("AmlCompute")
        elif isinstance(target, DsvmCompute):
            node.get_param('MLCComputeType').set_value("DSVM")
        elif isinstance(target, HDInsightCompute):
            node.get_param('MLCComputeType').set_value("Hdi")
        elif isinstance(target, RemoteCompute):
            node.get_param('MLCComputeType').set_value("RemoteCompute")

    @staticmethod
    def get_default_values():
        params = {'Framework': 'Python',
                  'DockerEnabled': 'true',
                  'BaseDockerImage': 'continuumio/miniconda3:4.4.10',
                  }
        return params


class _LegacyBatchAiComputeTargetPropertyMapper(_ComputeTargetPropertyMapper):
    """
    Maps legacy BatchAI compute target property
    """
    def get_params_list(self):
        param_defs = [ParamDef('BatchAiSubscriptionId', None, is_optional=True),
                      ParamDef('BatchAiResourceGroup', None, is_optional=True),
                      ParamDef('BatchAiWorkspaceName', None, is_optional=True),
                      ParamDef('ClusterName', None, is_optional=True),
                      ParamDef('NodeCount', None, is_optional=True),
                      ParamDef('NativeSharedDirectory', None, is_optional=True)]

        return param_defs

    def set_target_params(self, node, target, runconfig_params, compute_params):
        self.set_common_target_params(node, target)
        self.merge_compute_params(node, self.get_default_values(), compute_params)
        self.set_runconfig_params(node, runconfig_params)
        node.get_param('BatchAiSubscriptionId').set_value(target.subscription_id)
        node.get_param('BatchAiResourceGroup').set_value(target.resource_group_name)
        node.get_param('BatchAiWorkspaceName').set_value(target._batchai_workspace_name)
        node.get_param('ClusterName').set_value(target.cluster_name)

    @staticmethod
    def get_default_values():
        params = {'Framework': 'Python',
                  'DockerEnabled': 'true',
                  'BaseDockerImage': 'continuumio/miniconda3:4.4.10',
                  }
        return params


class _LocalComputeTargetPropertyMapper(_ComputeTargetPropertyMapper):
    """
    Maps local compute target property
    """
    def get_params_list(self):
        return []

    def set_target_params(self, node, target, runconfig_params, compute_params):
        return


class _ModuleParameterProvider(object):
    """Provides module parameter."""
    def __init__(self):
        self.mlc_mapper = _MlcComputeTargetPropertyMapper()
        self.legacy_batchai_mapper = _LegacyBatchAiComputeTargetPropertyMapper()
        self.local_mapper = _LocalComputeTargetPropertyMapper()
        self.mappers = [self.mlc_mapper, self.legacy_batchai_mapper, self.local_mapper]

    def get_params_list(self):
        param_defs = self._get_common_params_list()

        for mapper in self.mappers:
            param_defs.extend(mapper.get_params_list())

        return self._remove_duplicate_params(param_defs)

    def set_params(self, node, target, script_name, arguments, runconfig_params, batchai_params):
        self._set_common_params(node, script_name, arguments)
        if isinstance(target, AmlCompute) or isinstance(target, DsvmCompute)\
                or isinstance(target, RemoteCompute) or isinstance(target, HDInsightCompute):
            self.mlc_mapper.set_target_params(node, target, runconfig_params)
        elif isinstance(target, _BatchAITarget):
            self.legacy_batchai_mapper.set_target_params(node, target, runconfig_params, batchai_params)
        elif target.type is 'local':
            self.local_mapper.set_target_params(node, target, None, None)

    def _get_common_params_list(self):
        param_defs = [ParamDef('Target', None, is_optional=False),
                      ParamDef('TargetType', None, is_metadata_param=True, is_optional=False),
                      ParamDef('AutoPrepareEnvironment', 'true'),
                      ParamDef('MLCComputeType', None, is_optional=True)]

        param_defs.extend(self._get_runconfig_params_list())

        return param_defs

    @staticmethod
    def _get_parameterizable_runconfig_properties():
        # Target to be added later after dynamic compute story is finalized
        return ['NodeCount', 'MpiProcessCountPerNode', 'TensorflowWorkerCount', 'TensorflowParameterServerCount']

    @staticmethod
    def _get_runconfig_params_list():
        param_defs = [ParamDef('Target', None, is_optional=False),
                      ParamDef('Framework', None, is_optional=True),
                      ParamDef('Communicator', None, is_optional=True),
                      ParamDef('Script', None, is_optional=True),
                      ParamDef('Arguments', None, is_optional=True),
                      ParamDef('AutoPrepareEnvironment', 'true'),
                      ParamDef('PrepareEnvironment', 'true'),
                      ParamDef('BaseDockerImage', None, is_optional=True),
                      ParamDef('DockerEnabled', None, is_optional=True),
                      ParamDef('DockerArguments', None, is_optional=True),
                      ParamDef('RunConfiguration', None, is_optional=True),
                      ParamDef('JobName', None, is_optional=True),
                      ParamDef('MaxRunDurationSeconds', None, is_optional=True),
                      ParamDef('EnvironmentVariables', None, is_optional=True),
                      ParamDef('InterpreterPath', None, is_optional=True),
                      ParamDef('SharedVolumes', None, is_optional=True),
                      ParamDef('GpuSupport', None, is_optional=True),
                      ParamDef('BaseImageryRegistryAddress', None, is_optional=True),
                      ParamDef('BaseImageryRegistryUsername', None, is_optional=True),
                      ParamDef('BaseImageryRegistryPassword', None, is_optional=True),
                      ParamDef('SparkRepositories', None, is_optional=True),
                      ParamDef('SparkMavenPackages', None, is_optional=True),
                      ParamDef('SparkConfiguration', None, is_optional=True),
                      ParamDef('PrecachePackages', None, is_optional=True),
                      ParamDef('HistoryOutputCollection', None, is_optional=True),
                      ParamDef('ExposedPorts', None, is_optional=True),
                      ParamDef('ContainerInstanceRegion', None, is_optional=True),
                      ParamDef('ContainerInstanceCpuCores', None, is_optional=True),
                      ParamDef('ContainerInstanceMemoryGb', None, is_optional=True),
                      ParamDef('UserManagedDependencies', None, is_optional=True),
                      ParamDef('CondaDependencies', None, is_optional=True),
                      ParamDef('NodeCount', None, is_optional=True),
                      ParamDef('YarnDeployMode', None, is_optional=True),
                      ParamDef('MpiProcessCountPerNode', None, is_optional=True),
                      ParamDef('TensorflowWorkerCount', None, is_optional=True),
                      ParamDef('TensorflowParameterServerCount', None, is_optional=True),
                      ParamDef('AMLComputeName', None, is_optional=True),
                      ParamDef('AMLComputeVmSize', None, is_optional=True),
                      ParamDef('AMLComputeVmPriority', None, is_optional=True),
                      ParamDef('AMLComputeLocation', None, is_optional=True),
                      ParamDef('AMLComputeRetainCluster', None, is_optional=True),
                      ParamDef('AMLComputeNodeCount', None, is_optional=True)]

        return param_defs

    @staticmethod
    def _set_common_params(node, script_name, arguments):
        node.get_param('Script').set_value(script_name)
        if arguments is not None and len(arguments) > 0:
            node.get_param('Arguments').set_value(",".join([str(x) for x in arguments]))

    @staticmethod
    def _remove_duplicate_params(param_defs):
        unique_param_defs = []
        param_names = set()

        for param_def in param_defs:
            if param_def.name.lower() not in param_names:
                param_names.add(param_def.name.lower())
                unique_param_defs.append(param_def)

        return unique_param_defs
