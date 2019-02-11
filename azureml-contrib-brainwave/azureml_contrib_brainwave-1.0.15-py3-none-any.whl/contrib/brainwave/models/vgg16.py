# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module with the vgg-16 model."""
from azureml.contrib.brainwave.models.brainwave_model import BrainwaveModel


class AbstractVgg16(BrainwaveModel):
    """Abstract baseclass for Vgg-16."""

    _input_op = 'InputImage'
    _prefix = 'vgg_16/'
    _output_op = '{0}fc7/Relu'.format(_prefix)
    _save_name = "vgg16"

    classifier_input = _output_op + ":0"
    classifier_output = '{0}fc8/squeezed:0'.format(_prefix)
    classifier_uri = "https://go.microsoft.com/fwlink/?linkid=2026013"

    @property
    def output_dims(self):
        """Output dimensions of model."""
        return [None, 1, 1, 4096]

    @property
    def input_dims(self):
        """Input dimensions of model."""
        return [None, 244, 244, 3]


class Vgg16(AbstractVgg16):
    """Float-32 Version of VGG-16.

    This model is in RGB format.
    """

    _modelname = "vgg16"
    _modelver = "1.1.3"

    def __init__(self, model_base_path, is_frozen=False):
        """Create a Float-32 version of VGG 16.

        :param model_base_path: Path to download the model into. Used as a cache locally.
        """
        super().__init__(model_base_path, self._modelname, self._modelver,
                         "https://go.microsoft.com/fwlink/?linkid=2020212", self._save_name, is_frozen=is_frozen)


class QuantizedVgg16(AbstractVgg16):
    """Quantized version of VGG-16.

    This model is in RGB format.
    """

    _modelname = "msfpvgg16"
    _modelver = "1.1.2"

    def __init__(self, model_base_path, is_frozen=False, custom_weights_directory=None):
        """Create a version of VGG 16 quantized for Project Brainwave.

        This model is in RGB format.

        :param model_base_path: Path to download the model into. Used as a cache locally.
        :param is_frozen: Should the weights of the vgg-16 be frozen when it is imported. Freezing the weights can
        lead to faster training time, but may cause your model to perform worse overall. Defaults to false.
        :param custom_weights_directory: Directory to load pretrained vgg-16 weights from. Can load weights from
        either a float-32 version or a quantized version. If none, will load weights trained for accuracy on the
        Imagenet dataset.
        """
        super().__init__(model_base_path,
                         self._modelname,
                         self._modelver,
                         "https://go.microsoft.com/fwlink/?linkid=2020300",
                         self._save_name,
                         is_frozen=is_frozen,
                         weight_path=custom_weights_directory)
