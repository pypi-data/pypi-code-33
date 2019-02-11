# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Init file for azureml-contrib-explain-model/azureml/contrib/explain/model/scoring."""
from .scoring_model import KNNScoringModel, TreeScoringModel

__all__ = ["KNNScoringModel", "TreeScoringModel"]
