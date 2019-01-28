# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Create an model converter to convert a model to dlc model flavor."""

import json

from azureml.core.model import Model
from azureml._model_converters._model_convert_request import ModelConvertRequest
from azureml._model_converters._model_convert_client import ModelConvertClient
from azureml._model_converters.model_convert_operation import ModelConvertOperation


class SnpeConverter(object):
    """Class for converting models to dlc flavor using snpe."""

    @staticmethod
    def _get_model_id(workspace, source_model):
        """Get model id.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param source_model:
        :type source_model: azureml.core.model or model id str
        :return: model id str
        :rtype: str
        """
        # get the model id
        if type(source_model) is str:
            registered_model = Model(workspace, id=source_model)
            return registered_model.id

        if type(source_model) is Model:
            return source_model.id

        raise NotImplementedError('source_model must either be of type azureml.core.model.Model or a str of model id.')

    @staticmethod
    def _get_as_str(input_value):
        """Serialize and escape lists.

        :param input_value:
        :type input_value: str or List of str
        :return: serialized string
        :rtype: str
        """
        result = None
        if input_value:
            if type(input_value) == str:
                result = input_value
            elif type(input_value) == list:
                result = json.dumps(input_value)
            else:
                raise ValueError("Unexpected type [%s], str or list expected" % type(input_value))

        return result

    @staticmethod
    def convert_tf_model(workspace,
                         source_model,
                         input_node,
                         input_dims,
                         outputs_nodes,
                         allow_unconsumed_nodes=True,
                         mirror_content=False,
                         tool_version=None):
        """Use snpe-tensorflow-to-dlc to convert a TensorFlow model into an SNPE DLC file.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param source_model: Registered model to be converted
        :type source_model: azureml.core.model or model id str
        :param input_node: Name of the input layer
        :type input_node: str
        :param input_dims: List of dimensions for the input layer
        :type input_dims: int list
        :param outputs_nodes: List of graph's output nodes where each one will represent the output layer
            of the network
        :type outputs_nodes: str list
        :param allow_unconsumed_nodes: Uses a relaxed graph node to layer mapping algorithm which may not use
            all graph nodes
        :type allow_unconsumed_nodes: bool
        :param mirror_content: Copy registered model folder contents to the converted model folder
        :type mirror_content: bool
        :param tool_version: Optional tool version
        :type tool_version: str
        :return: Object to wait for conversion and get the converted model
        :rtype: ModelConvertOperation
        """
        # group the compile options used for conversion
        _target_model_flavor = "DLC"
        _input_node = "inputNode"
        _input_dims = "inputDims"
        _outputs_nodes = "outputNodes"
        _allow_unconsumed_nodes = 'allowUnconsumedNodes'
        _mirror_input_folder = 'mirrorInputFolder'
        _model_flavor_tf = 'TF'

        source_model_id = SnpeConverter._get_model_id(workspace, source_model)

        # create convert request object
        request = ModelConvertRequest(modelId=source_model_id, sourceModelFlavor=_model_flavor_tf,
                                      targetModelFalvor=_target_model_flavor,
                                      toolName="snpe",
                                      toolVersion=tool_version)
        request.compilation_options[_input_node] = input_node
        request.compilation_options[_allow_unconsumed_nodes] = allow_unconsumed_nodes
        request.compilation_options[_input_dims] = SnpeConverter._get_as_str(input_dims)
        request.compilation_options[_outputs_nodes] = SnpeConverter._get_as_str(outputs_nodes)
        request.compilation_options[_mirror_input_folder] = mirror_content

        # create model convert client and start model conversion
        client = ModelConvertClient(workspace)
        operation_id = client.convert_model(request)

        # create and return ModelConvert operation
        return ModelConvertOperation(workspace, operation_id)
