# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the structured model based APIs for explainer used on specific types of models."""

from abc import abstractmethod

from .base_explainer import BaseExplainer
from ..dataset.dataset_wrapper import DatasetWrapper


class StructuredInitModelExplainer(BaseExplainer):
    """Defines the base StructuredInitModelExplainer API for explainers.

    Used on specific models that require initialization examples.
    """

    def __init__(self, model, initialization_examples, **kwargs):
        """Initialize the StructuredInitModelExplainer.

        :param model: The black box model to explain.
        :type model: model
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        """
        super(StructuredInitModelExplainer, self).__init__(**kwargs)
        self._logger.debug('Initializing StructuredInitModelExplainer')
        self.model = model
        self.initialization_examples = initialization_examples


class TabularStructuredInitModelExplainer(StructuredInitModelExplainer):
    """Defines the base TabularStructuredInitModelExplainer API for tabular explainers.

    Used on specific models that require initialization examples.
    """

    def __init__(self, model, initialization_examples, **kwargs):
        """Initialize the TabularStructuredInitModelExplainer.

        :param model: The black box model to explain.
        :type model: model
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        """
        super(TabularStructuredInitModelExplainer, self).__init__(model, initialization_examples, **kwargs)
        self._logger.debug('Initializing TabularStructuredInitModelExplainer')
        if not isinstance(initialization_examples, DatasetWrapper):
            self.initialization_examples = DatasetWrapper(initialization_examples)


class TextStructuredInitModelExplainer(StructuredInitModelExplainer):
    """Defines the base TextStructuredInitModelExplainer API for text explainers.

    Used on specific models that require initialization examples.
    """

    def __init__(self, model, initialization_examples, **kwargs):
        """Initialize the TextStructuredInitModelExplainer.

        :param model: The black box model to explain.
        :type model: model
        :param initialization_examples: A list of text documents.
        :type initialization_examples: list[str]
        """
        super(TextStructuredInitModelExplainer, self).__init__(model, initialization_examples, **kwargs)
        self._logger.debug('Initializing TextStructuredInitModelExplainer')

    @abstractmethod
    def train_model(self):
        """Trains the model globally on the initialization examples."""
        pass


class PureStructuredModelExplainer(BaseExplainer):
    """Defines the base PureStructuredModelExplainer API for explainers used on specific models."""

    def __init__(self, model, **kwargs):
        """Initialize the PureStructuredModelExplainer.

        :param model: The black box model to explain.
        :type model: model
        """
        super(PureStructuredModelExplainer, self).__init__(**kwargs)
        self._logger.debug('Initializing PureStructuredModelExplainer')
        self.model = model

    @abstractmethod
    def explain_local(self, evaluation_examples):
        """Explain the black box model.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return: A model explanation object containing the local and global explanation.
        :rtype: BaseExplanation
        """
        if not isinstance(evaluation_examples, DatasetWrapper):
            evaluation_examples = DatasetWrapper(evaluation_examples)
        return evaluation_examples
