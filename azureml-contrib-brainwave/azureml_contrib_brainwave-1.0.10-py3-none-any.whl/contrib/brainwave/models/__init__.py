# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Python representation of models accelerated with project brainwave."""
from .resnet50 import Resnet50, QuantizedResnet50
from .resnet152 import Resnet152, QuantizedResnet152
from .vgg16 import Vgg16, QuantizedVgg16
from .utils import preprocess_array
from .densenet121 import Densenet121, QuantizedDensenet121

from azureml._base_sdk_common import __version__ as VERSION


__version__ = VERSION
__all__ = ["Resnet50", "QuantizedResnet50", "preprocess_array", "Resnet152", "QuantizedResnet152", "Vgg16",
           "QuantizedVgg16", "Densenet121", "QuantizedDensenet121"]
