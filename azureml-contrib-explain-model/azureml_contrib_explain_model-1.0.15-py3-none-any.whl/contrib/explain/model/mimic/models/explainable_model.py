# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the base API for explainable models."""

from abc import ABCMeta, abstractmethod
from azureml._logging import ChainedIdentity


class BaseExplainableModel(ChainedIdentity):
    """The base class for models that can be explained."""

    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        """Initialize the Explainable Model."""
        super(BaseExplainableModel, self).__init__(**kwargs)
        self._logger.debug('Initializing BaseExplainableModel')

    @abstractmethod
    def fit(self, **kwargs):
        """Abstract method to fit the explainable model."""
        pass

    @abstractmethod
    def predict(self, dataset, **kwargs):
        """Abstract method to predict labels using the explainable model."""
        pass

    @abstractmethod
    def predict_proba(self, dataset, **kwargs):
        """Abstract method to predict probabilities using the explainable model."""
        pass

    @abstractmethod
    def explain_global(self, **kwargs):
        """Abstract method to get the global feature importances from the trained explainable model."""
        pass

    @abstractmethod
    def explain_local(self, evaluation_examples, **kwargs):
        """Abstract method to get the local feature importances from the trained explainable model."""
        pass

    @property
    @abstractmethod
    def model(self):
        """Abstract method to get the underlying model."""
        pass
