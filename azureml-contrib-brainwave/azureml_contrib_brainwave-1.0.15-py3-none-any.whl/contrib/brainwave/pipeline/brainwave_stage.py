# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Stage for Brainwave model."""
import uuid

from azureml.contrib.brainwave.pipeline.abstract_stage import AbstractStage
import os


class BrainWaveStage(AbstractStage):
    """Stage for Brainwave model."""

    def __init__(self, sess, model, name=None):
        """Create brainwave stage.

        :param sess: Tensorflow session to take weights from.
        :type sess: Tensorflow.Session
        :param model: Brainwave model to write to file.
        :type model: azureml.contrib.realtimeai.models.model.RealtimeAIModel
        :param name:  Name to give the stage.
        """
        super().__init__()

        self.type = "brainwave"
        self.model_ref = model.model_ref
        self.properties = {"model_ref": model.model_ref, "model_version": model.model_version}
        self.input_dims = model.input_dims
        self.output_dims = model.output_dims
        self.name = name
        self.sess = sess
        self._model = model
        self.file_name = self.name if self.name is not None else str(uuid.uuid4())

    def json_dict(self):
        """Content to write to manifest."""
        output = {"type": self.type,
                  "output_tensor_dims": self.output_dims, "name": self.name, "model_path": self.file_name,
                  "input_tensor_dims": self.input_dims,
                  "properties": self.properties}
        return output

    def _write_data(self, base_path: str):
        """Write model checkpoint to specific path.

        :param base_path: Path to write the checkpoint to.
        """
        model_path = os.path.join(base_path, self.file_name)
        os.makedirs(model_path, exist_ok=True)
        self._model._write_to_tempdir(self.sess, model_path)
