# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Init file for azureml-contrib-explain-model/azureml/contrib/explain/model/mimic/models."""
from .explainable_model import BaseExplainableModel
from .lightgbm_model import LGBMExplainableModel

__all__ = ["BaseExplainableModel", "LGBMExplainableModel"]
