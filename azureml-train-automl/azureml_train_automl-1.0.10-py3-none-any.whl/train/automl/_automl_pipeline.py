# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wrapper class for AutoML pipeline objects."""
from typing import Any, Dict, Optional
from . import constants


class AutoMLPipeline(object):
    """Used to hold pipeline responses."""

    def __init__(self, pipeline_script: str, pipeline_id: str, training_size: Optional[float] = None) -> None:
        """
        Create an AutoMLPipeline object that wraps pipeline metadata.

        :param pipeline_script: a string representing the pipeline to be run
        :param pipeline_id: a hash string used to identify this pipeline
        :param training_size: a float in the range (0.0, 1.0] describing what portion of the data should be used
            during training
        """
        self.pipeline_id = pipeline_id              # type: str
        self.pipeline_script = pipeline_script      # type: str
        self.pipeline_output = constants.Defaults.INVALID_PIPELINE_VALIDATION_SCORES  # type: Dict[str, Any]
        self.training_size = training_size or 1     # type: float

        if self.training_size <= 0 or self.training_size > 1:
            raise ValueError('Training size must be in the range (0.0, 1.0].')

    def set_output(self, pipeline_output: Dict[str, Any]) -> None:
        """
        Store the execution output of this pipeline.

        Temporarily implemented as a method to make refactoring slightly easier instead of directly setting the
        property, due to a bug in PyCharm's type hinting:
        https://youtrack.jetbrains.com/issue/PY-24832

        :param pipeline_output: the output from pipeline execution.
        """
        self.pipeline_output = pipeline_output

    @property
    def fitted_pipeline(self) -> Optional[object]:
        """
        Return the fitted pipeline object from pipeline execution.

        :return: the fitted pipeline
        """
        return self.pipeline_output.get('fitted_pipeline')

    def get_score(self, metric: str) -> float:
        """
        Return the score for the given metric from pipeline execution.

        :param metric: the name of the metric to retrieve
        :return: the score for the provided metric
        """
        return float(self.pipeline_output.get(metric))

    @property
    def is_ensemble_pipeline(self) -> bool:
        """
        Check whether this pipeline is an ensemble pipeline.

        :return: True if this pipeline is an ensemble pipeline, false otherwise
        """
        return self.pipeline_id == constants.ENSEMBLE_PIPELINE_ID

    @property
    def training_percent(self) -> float:
        """
        Return the percentage of data that will be used during training.

        :return: a percentage value from 0 to 100 inclusive
        """
        return self.training_size * 100
