# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the base explainer API to create explanations."""

from abc import ABCMeta, abstractmethod
from azureml._logging import ChainedIdentity


class BaseExplainer(ChainedIdentity):
    """The base class for explainers that create explanations."""

    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        """Initialize the BaseExplainer."""
        super(BaseExplainer, self).__init__(*args, **kwargs)
        self._logger.debug('Initializing BaseExplainer')
        self.create_scoring_model = False

    @abstractmethod
    def explain_global(self, *args, **kwargs):
        """Abstract method to globally explain the given model.

        Note evaluation examples can be optional on derived classes since some explainers,
        for example MimicExplainer, don't support it.

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

    def __str__(self):
        """Get string representation of the explainer.

        :return: A string containing explainer name.
        :rtype: str
        """
        return "{}".format(self.__class__.__name__)
