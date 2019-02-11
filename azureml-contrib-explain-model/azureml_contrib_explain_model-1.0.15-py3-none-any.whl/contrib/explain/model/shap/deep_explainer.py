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
from ..explanation.explanation import _create_local_explanation
from ..common.aggregate_explainer import AggregateExplainer
from ..dataset.decorator import tabular_decorator
from azureml.explain.model._internal.constants import ExplainParams, Attributes


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

    @tabular_decorator
    def explain_global(self, evaluation_examples, top_k=None, explain_subset=None, features=None,
                       classes=None, nclusters=10, sampling_policy=None, create_scoring_model=False):
        """Explain the model globally by aggregating local explanations to global.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param top_k: Number of important features stored in the explanation. If specified, only the
            names and values corresponding to the top K most important features will be returned/stored.
        :type top_k: int
        :param explain_subset: List of feature indices. If specified, only selects a subset of the
            features in the evaluation dataset for explanation. The subset can be the top-k features
            from the model summary.
        :type explain_subset: list[int]
        :param features: A list of feature names.
        :type features: list[str]
        :param classes: Class names as a list of strings. The order of the class names should match
            that of the model output.  Only required if explaining classifier.
        :type classes: list[str]
        :param sampling_policy: Optional policy for sampling the evaluation examples.  See documentation on
            SamplingPolicy for more information.
        :type sampling_policy: SamplingPolicy
        :param create_scoring_model: Creates a model that can be used for scoring to approximate the feature
            importance values.
        :type create_scoring_model: bool
        :return: A model explanation object containing the global explanation.
        :rtype: GlobalExplanation
        """
        kwargs = {ExplainParams.EXPLAIN_SUBSET: explain_subset,
                  ExplainParams.FEATURES: features,
                  ExplainParams.SAMPLING_POLICY: sampling_policy,
                  ExplainParams.CREATE_SCORING_MODEL: create_scoring_model,
                  ExplainParams.TOP_K: top_k, ExplainParams.NCLUSTERS: nclusters}
        if classes is not None:
            kwargs[ExplainParams.CLASSES] = classes
        return self._explain_global(evaluation_examples, **kwargs)

    @tabular_decorator
    def explain_local(self, evaluation_examples, explain_subset=None, features=None, classes=None, nclusters=10):
        """Explain the model by using shap's deep explainer.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param explain_subset: List of feature indices. If specified, only selects a subset of the
            features in the evaluation dataset for explanation, which will speed up the explanation
            process when number of features is large and the user already knows the set of interested
            features. The subset can be the top-k features from the model summary.
        :type explain_subset: list[int]
        :param features: A list of feature names.
        :type features: list[str]
        :param classes: Class names as a list of strings. The order of the class names should match
            that of the model output.  Only required if explaining classifier.
        :type classes: list[str]
        :return: A model explanation object containing the local explanation.
        :rtype: LocalExplanation
        """
        self.initialization_examples.compute_summary(nclusters=nclusters)

        if self.explainer is None and not self.is_valid():
            raise Exception('Model not supported by DeepExplainer')

        self._logger.debug('Explaining deep model')
        # sample the evaluation examples
        if self.sampling_policy is not None and self.sampling_policy.allow_eval_sampling:
            sampling_method = self.sampling_policy.sampling_method
            max_dim_clustering = self.sampling_policy.max_dim_clustering
            evaluation_examples.sample(max_dim_clustering, sampling_method=sampling_method)
        # TODO: The feature getting pattern needs to be improved here
        kwargs = {}
        if classes is not None:
            kwargs[ExplainParams.CLASSES] = classes
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
        return _create_local_explanation(local_importance_values=local_importance_values,
                                         expected_values=expected_values, classification=classification,
                                         scoring_model=scoring_model, **kwargs)
