# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wrapper class for AutoML pipeline objects."""
from typing import Optional
from . import constants


class AutoMLPipeline(object):
    """Used to hold pipeline responses."""

    def __init__(self,
                 run_id: str,
                 pipeline_script: str,
                 pipeline_id: str,
                 training_size: Optional[float] = None,
                 predicted_time: Optional[float] = None) -> None:
        """
        Create an AutoMLPipeline object that wraps pipeline metadata.

        :param run_id: a string representing the id for the run executing the pipeline
        :param pipeline_script: a string representing the pipeline to be run
        :param pipeline_id: a hash string used to identify this pipeline
        :param training_size: a float in the range (0.0, 1.0] describing what portion of the data should be used
            during training
        """
        self.run_id = run_id                        # type: str
        self.pipeline_id = pipeline_id              # type: str
        self.pipeline_script = pipeline_script      # type: str
        self.training_size = training_size or 1     # type: float
        self.predicted_time = predicted_time or 0   # type: float

        if self.training_size <= 0 or self.training_size > 1:
            raise ValueError('Training size must be in the range (0.0, 1.0].')

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
