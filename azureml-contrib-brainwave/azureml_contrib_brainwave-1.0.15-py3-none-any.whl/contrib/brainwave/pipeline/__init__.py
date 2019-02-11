# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Construct the execution pipeline for Project Brainwave webservices."""

from .brainwave_stage import BrainWaveStage
from .tensorflow_stage import TensorflowStage
from .keras_stage import KerasStage
from .model_definition import ModelDefinition
from azureml._base_sdk_common import __version__ as VERSION

__version__ = VERSION
__all__ = [
    "BrainWaveStage",
    "TensorflowStage",
    "KerasStage",
    "ModelDefinition"
]
