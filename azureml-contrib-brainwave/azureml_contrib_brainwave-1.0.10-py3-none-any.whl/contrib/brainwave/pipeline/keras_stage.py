# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Stage for Keras Sequential model."""
import sys
from io import StringIO

try:
    sys.stderr = StringIO()
    import keras
finally:
    sys.stderr = sys.__stderr__

from azureml.contrib.brainwave.pipeline import TensorflowStage


class KerasStage(TensorflowStage):
    """Stage for Keras Sequential model."""

    def __init__(self, model: keras.models.Sequential, name=None):
        """
        Create Keras stage.

        :param model: Keras model
        :type model: keras.models.Sequential
        :param name: Stage name to use for debugging. - should encode to string when JSON encode is called.
        """
        super().__init__(keras.backend.get_session(), model.inputs[0], model.outputs[0], name)
