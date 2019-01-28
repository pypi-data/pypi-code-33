# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the tabular explainer meta-api for returning the best explanation result based on the given model."""

from .common.explainer import Explainer
from .shap.tree_explainer import TreeExplainer
from .shap.deep_explainer import DeepExplainer
from .shap.kernel_explainer import KernelExplainer
from .dataset.dataset_wrapper import DatasetWrapper


class TabularExplainer(Explainer):
    """Defines the tabular explainer meta-api for returning the best explanation result based on the given model."""

    def __init__(self, model, initialization_examples, **kwargs):
        """Initialize the TabularExplainer.

        :param model: The model or pipeline to explain.
        :type model: model that implements predict or predict_proba or pipeline function that accepts a 2d ndarray
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        """
        super(TabularExplainer, self).__init__(**kwargs)
        self._logger.debug('Initializing TabularExplainer')
        self.model = model
        if not isinstance(initialization_examples, DatasetWrapper):
            self._logger.debug('Wrapping init examples with DatasetWrapper')
            self.initialization_examples = DatasetWrapper(initialization_examples)
        else:
            self.initialization_examples = initialization_examples

    def _explain_internal(self, evaluation_examples, explain_global=False, **kwargs):
        """Globally explains the black box model or function.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return: A model explanation object containing the local and global explanation.
        :rtype: BaseExplanation
        """
        self._logger.debug('Explaining tabular data')
        if not isinstance(evaluation_examples, DatasetWrapper):
            evaluation_examples = DatasetWrapper(evaluation_examples)
        initialized_explainers = [
            TreeExplainer(self.model),
            DeepExplainer(self.model, self.initialization_examples),
            KernelExplainer(self.model, self.initialization_examples)
        ]
        for explainer in initialized_explainers:
            if explainer.is_valid(**kwargs):
                self._logger.debug("Valid {} initialized".format(explainer))
                if explain_global:
                    return explainer.explain_global(evaluation_examples, **kwargs)
                else:
                    return explainer.explain_local(evaluation_examples, **kwargs)
        errMsg = 'Could not find valid explainer to explain model'
        self._logger.info(errMsg)
        raise Exception(errMsg)

    def explain_global(self, evaluation_examples, **kwargs):
        """Globally explains the black box model or function.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return: A model explanation object containing the global explanation.
        :rtype: GlobalExplanation
        """
        return self._explain_internal(evaluation_examples, explain_global=True, **kwargs)

    def explain_local(self, evaluation_examples, **kwargs):
        """Locally explains the black box model or function.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return: A model explanation object containing the local explanation.
        :rtype: LocalExplanation
        """
        return self._explain_internal(evaluation_examples, explain_global=False, **kwargs)
