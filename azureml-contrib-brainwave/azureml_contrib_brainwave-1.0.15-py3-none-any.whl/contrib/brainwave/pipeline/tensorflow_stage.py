# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Stage for tensorflow models."""
from azureml.contrib.brainwave.pipeline.abstract_stage import AbstractStage
from azureml.contrib.brainwave.external.tensorflow.graph_util_impl import convert_variables_to_constants
import tensorflow as tf
import os
import uuid

try:
    tf_version = str.split(tf.VERSION, '.')
    tf_version_ints = [int(x) for x in tf_version]
    assert tf_version_ints[0] == 1
    assert 6 <= tf_version_ints[1] <= 10
except AssertionError as e:
    raise ImportError("azureml-contrib-brainwave requires tensorflow version >= 1.6 and <= 1.10 and you have {}"
                      .format(tf.VERSION))


class TensorflowStage(AbstractStage):
    """Stage for tensorflow model."""

    def __init__(self, session, input_tensor=None, output_tensor=None, name=None):
        """Create Tensorflow stage.

        :param session: Session to store values from
        :type session: tf.Session
        :param input_tensor:  Name of the input tensor to the stage.
        :param output_tensor: Name of the output tensor to the stage.
        :param name: Name of the stage.
        """
        super().__init__()

        self.type = "tensorflow"
        self.input_tensor = input_tensor
        self.output_tensor = output_tensor
        self.name = name
        self.input_tensor_name = self.input_tensor.name
        self.output_tensor_name = self.output_tensor.name
        try:
            self.input_tensor_shape = self.input_tensor.get_shape().as_list()
        except ValueError:
            self.input_tensor_shape = None
        try:
            self.output_tensor_shape = self.output_tensor.get_shape().as_list()
        except ValueError:
            self.output_tensor_shape = None
        self.file_name = self.name if self.name is not None else str(uuid.uuid4())
        self.session = session

    def json_dict(self):
        """Encode information about the pipeline.

        :return: json_dict for encoding to manifest file.
        """
        return {"type": self.type, "input_tensor": self.input_tensor_name, "output_tensor": self.output_tensor_name,
                "model_path": self.file_name, "name": self.name,
                "input_tensor_dims": self.input_tensor_shape,
                "output_tensor_dims": self.output_tensor.get_shape().as_list()}

    def _write_data(self, base_path: str):
        model_path = os.path.join(base_path, self.file_name)

        frozen_graph_def = convert_variables_to_constants(
            self.session,
            self.session.graph_def,
            [self.input_tensor.op.name],
            [self.output_tensor.op.name]
        )

        with tf.gfile.GFile(model_path, "wb") as f:
            f.write(frozen_graph_def.SerializeToString())
