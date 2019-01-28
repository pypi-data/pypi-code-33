# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines a tabular explainer mixin for wrapping the evaluation examples dataset in a DatasetWrapper."""

from abc import abstractmethod

from .common.base_explainer import BaseExplainer
from .dataset.dataset_wrapper import DatasetWrapper


class TabularDatasetExplainer(BaseExplainer):
    """A mixin for wrapper the evaluation examples dataset in a DatasetWrapper."""

    def __init__(self, **kwargs):
        """Initialize the TabularDatasetExplainer."""
        super(TabularDatasetExplainer, self).__init__(**kwargs)
        self._logger.debug('Initializing TabularDatasetExplainer')

    def explain_global(self, evaluation_examples, **kwargs):
        """Explains the model globally.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        """
        if not isinstance(evaluation_examples, DatasetWrapper):
            self._logger.debug('Eval examples not wrapped, wrapping')
            evaluation_examples = DatasetWrapper(evaluation_examples)
        return self._explain_global(evaluation_examples, **kwargs)

    def explain_local(self, evaluation_examples, **kwargs):
        """Explains the model locally.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        """
        if not isinstance(evaluation_examples, DatasetWrapper):
            self._logger.debug('Eval examples not wrapped, wrapping')
            evaluation_examples = DatasetWrapper(evaluation_examples)
        return self._explain_local(evaluation_examples, **kwargs)

    @abstractmethod
    def _explain_global(self, evaluation_examples, **kwargs):
        """Protected method that returns the global model explanation, must be implemented by derived classes.

        :param evaluation_examples: A common DatasetWrapper containing the evaluation examples.
        :type evaluation_examples: DatasetWrapper
        """
        pass

    @abstractmethod
    def _explain_local(self, evaluation_examples, **kwargs):
        """Protected method that returns the local model explanation, must be implemented by derived classes.

        :param evaluation_examples: A common DatasetWrapper containing the evaluation examples.
        :type evaluation_examples: DatasetWrapper
        """
        pass
