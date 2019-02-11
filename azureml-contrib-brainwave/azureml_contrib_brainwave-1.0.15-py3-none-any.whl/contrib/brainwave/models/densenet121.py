# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Project brainwave version of Densenet."""
from azureml.contrib.brainwave.models.brainwave_model import BrainwaveModel


class AbstractDensenet121(BrainwaveModel):
    """Abstract base class for densenet.

    This model is in RGB format, and has a scaling factor of 0.017
    """

    _input_op = 'InputImage'
    _prefix = 'densenet_121/'
    _output_op = 'brainwave_densenet121_1_Version_0.1_output_1'
    _save_name = "densenet121"

    classifier_input = 'densenet121/final_block/global_avg_pool/Mean:0'.format(_prefix)
    classifier_output = 'densenet121/predictions/Softmax:0'.format(_prefix)
    classifier_uri = "https://go.microsoft.com/fwlink/?linkid=2025957"

    @property
    def output_dims(self):
        """Output dimensions of model."""
        return [None, 1, 1, 1024]

    @property
    def input_dims(self):
        """Input dimensions of model."""
        return [None, 244, 244, 3]


class Densenet121(AbstractDensenet121):
    """Float-32 Version of Densenet.

    This model is in RGB format, and has a scaling factor of 0.017
    """

    _modelname = "dn121"
    _modelver = "1.1.4"

    def __init__(self, model_base_path, is_frozen=False):
        """Create a Float-32 version of Densenet. This model is in RGB format.

        :param model_base_path: Path to download the model into. Used as a cache locally.
        """
        super().__init__(model_base_path, self._modelname, self._modelver,
                         "https://go.microsoft.com/fwlink/?linkid=2025085", self._save_name, is_frozen=is_frozen)


class QuantizedDensenet121(AbstractDensenet121):
    """Quantized version of Densenet.

    This model is in RGB format.
    """

    _modelname = "msfpdn121"
    _modelver = "1.1.4"

    def __init__(self, model_base_path, is_frozen=False, custom_weights_directory=None):
        """Create a version of Densenet quantized for Project Brainwave.

        This model is in RGB format.

        :param model_base_path: Path to download the model into. Used as a cache locally.
        :param is_frozen: Should the weights of the densenet be frozen when it is imported. Freezing the weights can
        lead to faster training time, but may cause your model to perform worse overall. Defaults to false.
        :param custom_weights_directory: Directory to load pretrained densenet weights from. Can load weights from
        either a float-32 version or a quantized version. If none, will load weights trained for accuracy on the
        Imagenet dataset.
        """
        super().__init__(model_base_path,
                         self._modelname,
                         self._modelver,
                         "https://go.microsoft.com/fwlink/?linkid=2025129",
                         self._save_name,
                         is_frozen=is_frozen,
                         weight_path=custom_weights_directory)
