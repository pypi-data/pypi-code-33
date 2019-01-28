# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines an explainer for DNN models."""

import shap
import numpy as np
import sys

from ..common.structured_model_explainer import TabularStructuredInitModelExplainer
from ..common.explanation_utils import _get_dense_examples, _convert_to_list
from ..scoring.scoring_model import KNNScoringModel
from ..explanation.explanation import create_local_explanation
from ..common.aggregate_explainer import AggregateExplainer
from azureml.explain.model._internal.constants import Defaults, ExplainParams, Attributes


class logger_redirector(object):
    """A redirector for system error output to logger."""

    def __init__(self, module_logger):
        """Initialize the logger_redirector.

        :param module_logger: The logger to use for redirection.
        :type module_logger: logger
        """
        self.logger = module_logger

    def __enter__(self):
        """Start the redirection for logging."""
        self.logger.debug("Redirecting user output to logger")
        self.original_stderr = sys.stderr
        sys.stderr = self

    def write(self, data):
        """Write the given data to logger.

        :param data: The data to write to logger.
        :type data: str
        """
        self.logger.debug(data)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Finishes the redirection for logging."""
        try:
            if exc_val:
                # The default traceback.print_exc() expects a file-like object which
                # OutputCollector is not. Instead manually print the exception details
                # to the wrapped sys.stderr by using an intermediate string.
                # trace = traceback.format_tb(exc_tb)
                import traceback
                trace = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
                print(trace, file=sys.stderr)
        finally:
            sys.stderr = self.original_stderr
            self.logger.debug("User scope execution complete.")


class DeepExplainer(TabularStructuredInitModelExplainer, AggregateExplainer):
    """An explainer for DNN models, implemented using shap's DeepExplainer, supports tensorflow and pytorch."""

    def __init__(self, model, initialization_examples, **kwargs):
        """Initialize the DeepExplainer.

        :param model: The DNN model to explain.
        :type model: pytorch or tensorflow model
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        """
        super(DeepExplainer, self).__init__(model, initialization_examples, **kwargs)
        self._logger.debug('Initializing DeepExplainer')
        self.explainer = None

    def is_valid(self, **kwargs):
        """Determine whether the given DNN model can be explained.

        :return: True if the model can be explained, False otherwise.
        :rtype: bool
        """
        try:
            self.initialization_examples.compute_summary(**kwargs)
            summary = self.initialization_examples.dataset
            # Suppress warning message from Keras
            with logger_redirector(self._logger):
                self.explainer = shap.DeepExplainer(self.model, summary.data)
        except Exception:
            self._logger.debug('Model is not a valid deep model')
            return False
        self._logger.debug('Model is a valid deep model')
        return True

    def _explain_local(self, evaluation_examples, explain_subset=None, silent=True, nsamples=Defaults.AUTO,
                       features=None, **kwargs):
        """Explains the model by using shap's deep explainer.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return: A model explanation object containing the local and global explanation.
        :rtype: BaseExplanation
        """
        self.initialization_examples.compute_summary(**kwargs)

        if self.explainer is None and not self.is_valid():
            raise Exception('Model not supported by DeepExplainer')

        self._logger.debug('Explaining deep model')
        # sample the evaluation examples
        if self.allow_eval_sampling:
            evaluation_examples.sample(self.max_dim_clustering, sampling_method=self.sampling_method)
        # TODO: The feature getting pattern needs to be improved here
        kwargs[ExplainParams.FEATURES] = evaluation_examples.get_features(features=features)
        evaluation_examples = evaluation_examples.dataset
        # for now convert evaluation examples to dense format if they are sparse
        # until DeepExplainer sparse support is added
        shap_values = self.explainer.shap_values(_get_dense_examples(evaluation_examples))
        classification = isinstance(shap_values, list)
        if explain_subset:
            if classification:
                self._logger.debug('Classification explanation')
                for i in range(shap_values.shape[0]):
                    shap_values[i] = shap_values[i][:, explain_subset]
            else:
                self._logger.debug('Regression explanation')
                shap_values = shap_values[:, explain_subset]

        expected_values = None
        if hasattr(self.explainer, Attributes.EXPECTED_VALUE):
            self._logger.debug('reporting expected values')
            expected_values = self.explainer.expected_value
            if isinstance(expected_values, np.ndarray):
                expected_values = expected_values.tolist()
        local_importance_values = _convert_to_list(shap_values)
        scoring_model = None
        if self.create_scoring_model:
            scoring_model = KNNScoringModel(evaluation_examples, local_importance_values)
        return create_local_explanation(local_importance_values=local_importance_values,
                                        expected_values=expected_values, classification=classification,
                                        scoring_model=scoring_model, **kwargs)
