# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module with the renset-50 model."""
from azureml.contrib.brainwave.models.brainwave_model import BrainwaveModel


class AbstractResnet50(BrainwaveModel):
    """Abstract baseclass for resnet-50."""

    _input_op = 'InputImage'
    _prefix = 'resnet_v1_50/'
    _output_op = '{0}pool5'.format(_prefix)
    _save_name = "resnet50"

    classifier_input = _output_op + ":0"
    classifier_output = '{0}predictions/Softmax:0'.format(_prefix)
    classifier_uri = "https://go.microsoft.com/fwlink/?linkid=2026011"

    @property
    def output_dims(self):
        """Get output dimensions."""
        return [None, 1, 1, 2048]

    @property
    def input_dims(self):
        """Get input dimensions."""
        return [None, 244, 244, 3]


class Resnet50(AbstractResnet50):
    """Float-32 Version of Resnet-50."""

    _modelname = "rn50"
    _modelver = "1.1.3"

    def __init__(self, model_base_path, is_frozen=False):
        """Create a Float-32 version of resnet 50.

        :param model_base_path: Path to download the model into. Used as a cache locally.
        """
        super().__init__(model_base_path, self._modelname, self._modelver,
                         "https://go.microsoft.com/fwlink/?linkid=2025071", self._save_name, is_frozen=is_frozen)


class QuantizedResnet50(AbstractResnet50):
    """Quantized version of Renset-50."""

    _modelname = "msfprn50"
    _modelver = "1.1.2"

    def __init__(self, model_base_path, is_frozen=False, custom_weights_directory=None):
        """Create a version of resnet 50 quantized for Project Brainwave.

        :param model_base_path: Path to download the model into. Used as a cache locally.
        :param is_frozen: Should the weights of the resnet-50 be frozen when it is imported. Freezing the weights can
        lead to faster training time, but may cause your model to perform worse overall. Defaults to false.
        :param custom_weights_directory: Directory to load pretrained resnet-50 weights from. Can load weights from
        either a float-32 version or a quantized version. If none, will load weights trained for accuracy on the
        Imagenet dataset.
        """
        super().__init__(model_base_path,
                         self._modelname,
                         self._modelver,
                         "https://go.microsoft.com/fwlink/?linkid=2025081",
                         self._save_name,
                         is_frozen=is_frozen,
                         weight_path=custom_weights_directory)
