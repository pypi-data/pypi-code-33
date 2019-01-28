# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""data_transfer_step.py, module to transfer data between Azure Blob, Azure Data Lake store, and Azure SQL database."""
from azureml.core.compute import DataFactoryCompute
from azureml.data.data_reference import DataReference
from azureml.pipeline.core import PipelineData, PipelineStep
from azureml.pipeline.core.graph import ParamDef, InputPortBinding, OutputPortBinding, PortDataReference
from azureml.pipeline.core._module_builder import _InterfaceModuleBuilder

import json
import re


class DataTransferStep(PipelineStep):
    """Add a step to transfer data between Azure Blob, Azure Data Lake store, and Azure SQL database.

    :param name: Name of the step
    :type name: str
    :param source_data_reference: Input connection that serves as source of data transfer operation
    :type source_data_reference: list[azureml.pipeline.core.graph.InputPortBinding,
                  azureml.data.data_reference.DataReference, azureml.pipeline.core.PortDataReference,
                  azureml.pipeline.core.builder.PipelineData]
    :param destination_data_reference: Input connection that serves as destination of data transfer operation
    :type destination_data_reference: list[azureml.pipeline.core.graph.InputPortBinding,
                                           azureml.data.data_reference.DataReference]
    :param compute_target: Azure Data Factory to use for transferring data
    :type compute_target: DataFactoryCompute, str
    :param source_reference_type: An optional string specifying the type of source_data_reference.
                                  Possible values include: 'file', 'directory'. When not specified, we use the
                                  type of existing path or directory if it's a new path.
    :type source_reference_type: str
    :param destination_reference_type: An optional string specifying the type of destination_data_reference.
                                       Possible values include: 'file', 'directory'. When not specified, we use
                                       the type of existing path or directory if it's a new path.
    :type destination_reference_type: str
    :param allow_reuse: Whether the step should reuse results of previous DataTransferStep when run with same inputs.
                        Set as False to force data to be transferred again.
    :type allow_reuse: bool
    """

    def __init__(self, name, source_data_reference=None, destination_data_reference=None, compute_target=None,
                 source_reference_type=None, destination_reference_type=None, allow_reuse=True):
        """
        Initialize DataTransferStep.

        :param name: Name of the step
        :type name: str
        :param source_data_reference: Input connection that serves as source of data transfer operation
        :type source_data_reference: list[azureml.pipeline.core.graph.InputPortBinding,
                    azureml.data.data_reference.DataReference, azureml.pipeline.core.PortDataReference,
                    azureml.pipeline.core.builder.PipelineData]
        :param destination_data_reference: Input connection that serves as destination of data transfer operation
        :type destination_data_reference:
                    list[azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference]
        :param compute_target: Azure Data Factory to use for transferring data
        :type compute_target: DataFactoryCompute, str
        :param source_reference_type: An optional string specifying the type of source_data_reference.
        Possible values include: 'file', 'directory'. When not specified, we use the type of existing path or
        directory if it's a new path.
        :type source_reference_type: str
        :param destination_reference_type: An optional string specifying the type of destination_data_reference.
        Possible values include: 'file', 'directory'. When not specified, we use the type of existing path or
        directory if it's a new path.
        :type destination_reference_type: str
        :param allow_reuse: Whether the step should reuse results of previous DataTransferStep when run with same
        inputs. Set as False to force data to be transferred again.
        :type allow_reuse: bool
        """
        if name is None:
            raise ValueError('name is required')
        if not isinstance(name, str):
            raise ValueError('name must be a string')

        self._params = {}

        self._params['CopyOptions'] = DataTransferStep._get_copy_options_param(source_reference_type,
                                                                               destination_reference_type)

        self._allow_reuse = allow_reuse

        if compute_target is None:
            raise ValueError('compute_target is required')

        if not isinstance(destination_data_reference, InputPortBinding) and \
                not isinstance(destination_data_reference, DataReference):
            raise ValueError("Unexpected destination_data_reference type: %s" % type(destination_data_reference))

        if isinstance(destination_data_reference, InputPortBinding):
            bind_object = destination_data_reference.bind_object
            if isinstance(bind_object, DataReference):
                destination_data_reference = bind_object
            else:
                raise ValueError("destination_data_reference has unexpected bind_object type: %s" % type(bind_object))

        self._source_data_reference = source_data_reference
        self._destination_data_reference = destination_data_reference
        self._compute_target = compute_target

        source_input = DataTransferStep._create_input_port_binding(self._source_data_reference, 'SourceLocation')
        destination_input = DataTransferStep._create_input_port_binding(
            self._destination_data_reference, 'DestinationLocation')
        inputs = [source_input, destination_input]

        outputs = [OutputPortBinding(name='Output',
                                     datastore=self._destination_data_reference.datastore,
                                     bind_mode=self._destination_data_reference.mode,
                                     path_on_compute=self._destination_data_reference.path_on_compute,
                                     overwrite=self._destination_data_reference.overwrite)]

        super().__init__(name, inputs, outputs)

    def create_node(self, graph, default_datastore, context):
        """
        Create a node from this DataTransfer step and add to the given graph.

        :param graph: The graph object to add the node to.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: default datastore
        :type default_datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        :param context: The graph context.
        :type context: _GraphContext

        :return: The created node.
        :rtype: azureml.pipeline.core.graph.Node
        """
        data_factory_resource_id = self._get_data_factory_resource_id(context)
        data_factory_config = DataTransferStep._get_data_factory_config(data_factory_resource_id)

        self._params.update(data_factory_config)

        param_defs = [ParamDef('Command', 'DataCopy')]
        param_defs += [ParamDef(name, is_metadata_param=True) for name in self._params]

        module_def = self.create_module_def(execution_type="DataTransferCloud",
                                            input_bindings=self._inputs, output_bindings=self._outputs,
                                            param_defs=param_defs, create_sequencing_ports=False,
                                            allow_reuse=self._allow_reuse)

        module_builder = _InterfaceModuleBuilder(context=context, module_def=module_def)

        return graph.add_module_node(
            self.name,
            input_bindings=self._inputs,
            output_bindings=self._outputs,
            param_bindings=self._params,
            module_builder=module_builder)

    def get_output(self):
        """
        Get the output of the step.

        :return: The output of the step.
        :rtype: azureml.pipeline.core.builder.PipelineData
        """
        output = self._destination_data_reference
        if isinstance(output, DataReference):
            output = PipelineData(
                name='Output',
                datastore=output.datastore,
                output_mode=output.mode,
                output_path_on_compute=output.path_on_compute,
                output_overwrite=output.overwrite)
            output._set_producer(self)
            return output

        raise TypeError('destination_data_reference is not of correct type')

    @staticmethod
    def _get_copy_options_param(source_reference_type, destination_reference_type):
        possible_values = ['file', 'directory']

        copy_options = {}

        def get_valid_ref(ref_name, ref_type):
            possible_values_str = ', '.join(possible_values)

            if not isinstance(ref_type, str):
                raise ValueError('{name} must be a string. Possible values include: {values}.'
                                 .format(name=ref_name, values=possible_values_str))

            ref_type = ref_type.lower()

            if ref_type not in possible_values:
                raise ValueError('Unknown value provided for {name}. Possible values include: {values}.'
                                 .format(name=ref_name, values=possible_values_str))

            return ref_type

        if source_reference_type is not None:
            copy_options['source_reference_type'] = get_valid_ref('source_reference_type', source_reference_type)

        if destination_reference_type is not None:
            copy_options['destination_reference_type'] = get_valid_ref('destination_reference_type',
                                                                       destination_reference_type)

        return json.dumps(copy_options)

    def _get_data_factory_resource_id(self, context):
        """
        Get the data factory resource id.

        :param context: context
        :type context: _GraphContext

        :return: The id of the data factory.
        :rtype: str
        """
        compute_target = self._compute_target

        if isinstance(compute_target, DataFactoryCompute):
            return compute_target.cluster_resource_id

        if isinstance(compute_target, str):
            try:
                compute_target = DataFactoryCompute(context._workspace, compute_target)
                return compute_target.cluster_resource_id
            except Exception as e:
                raise ValueError('Error in getting data factory compute: {}'.format(e))

        raise ValueError('compute_target is not specified correctly')

    @staticmethod
    def _get_data_factory_config(data_factory_resource_id):
        """
        Get the data factory config.

        :param data_factory_resource_id: data factory resource id
        :type data_factory_resource_id: str

        :return: The data factory config.
        :rtype: dict
        """
        resource_id_regex = \
            r'\/subscriptions\/([^/]+)\/resourceGroups\/([^/]+)\/providers\/Microsoft\.DataFactory\/factories\/([^/]+)'

        match = re.search(resource_id_regex, data_factory_resource_id, re.IGNORECASE)

        if match is None:
            raise ValueError('Data Factory resource Id is not in correct format: {}'.format(data_factory_resource_id))

        return {
            'DataFactorySubscriptionId': match.group(1),
            'DataFactoryResourceGroup': match.group(2),
            'DataFactoryName': match.group(3),
        }

    @staticmethod
    def _create_input_port_binding(input_data_reference, input_port_name):
        """
        Create the input port binding.

        :param input_data_reference: input data reference object
        :type input_data_reference: data reference
        :param input_port_name: input port name
        :type input_port_name: str

        :return: The input port binding.
        :rtype: azureml.pipeline.core.graph.InputPortBinding
        """
        if isinstance(input_data_reference, InputPortBinding):
            return input_data_reference

        if isinstance(input_data_reference, PipelineData) or isinstance(input_data_reference, PortDataReference):
            return input_data_reference.create_input_binding(input_name=input_port_name)

        if isinstance(input_data_reference, DataReference):
            return InputPortBinding(
                name=input_port_name,
                bind_object=input_data_reference,
                bind_mode=input_data_reference.mode,
                path_on_compute=input_data_reference.path_on_compute,
                overwrite=input_data_reference.overwrite)

        raise TypeError('input_data_reference is not of correct type')
