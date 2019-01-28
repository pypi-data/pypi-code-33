# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the base explainer API to create explanations."""

from abc import abstractmethod

from .explainer import Explainer


class BaseExplainer(Explainer):
    """The base class for explainers that create explanations."""

    def __init__(self, **kwargs):
        """Initialize the BaseExplainer."""
        super(BaseExplainer, self).__init__(**kwargs)
        self._logger.debug('Initializing BaseExplainer')
        self.allow_eval_sampling = False
        self.max_dim_clustering = 50
        self.sampling_method = 'hdbscan'
        self.create_scoring_model = False

    @abstractmethod
    def explain_global(self, evaluation_examples, **kwargs):
        """Abstract method to globally explain the given model.

        TODO: remove evaluation_examples

        :param evaluation_examples: The evaluation examples
        :type evaluation_examples: object
        :return: A model explanation object containing the global explanation.
        :rtype: GlobalExplanation
        """
        pass

    @abstractmethod
    def explain_local(self, evaluation_examples, **kwargs):
        """Abstract method to explain local instances.

        :param evaluation_examples: The evaluation examples
        :type evaluation_examples: object
        :return: A model explanation object containing the local explanation.
        :rtype: LocalExplanation
        """
        pass

    @abstractmethod
    def is_valid(self, **kwargs):
        """Abstract method to determine if the given model is valid."""
        pass
