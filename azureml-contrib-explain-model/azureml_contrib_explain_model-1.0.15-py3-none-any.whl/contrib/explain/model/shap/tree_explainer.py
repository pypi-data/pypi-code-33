# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the TreeExplainer for returning explanations for tree-based models."""

import shap
import numpy as np

from ..common.structured_model_explainer import PureStructuredModelExplainer
from ..common.explanation_utils import _get_dense_examples, _convert_to_list
from ..common.aggregate_explainer import AggregateExplainer
from ..dataset.decorator import tabular_decorator
from ..scoring.scoring_model import KNNScoringModel
from ..explanation.explanation import _create_local_explanation
from azureml.explain.model._internal.constants import ExplainParams, Attributes


class TreeExplainer(PureStructuredModelExplainer, AggregateExplainer):
    """Defines the TreeExplainer for returning explanations for tree-based models."""

    def __init__(self, model, **kwargs):
        """Initialize the TreeExplainer.

        :param model: The tree model to explain.
        :type model: lightgbm, xgboost or scikit-learn tree model
        """
        super(TreeExplainer, self).__init__(model, **kwargs)
        self._logger.debug('Initializing TreeExplainer')
        self.explainer = None

    def is_valid(self, **kwargs):
        """Determine whether the given tree model can be explained.

        :return: True if the model can be explained, False otherwise.
        :rtype: bool
        """
        try:
            self.explainer = shap.TreeExplainer(self.model)
        except Exception:
            return False
        return True

    @tabular_decorator
    def explain_global(self, evaluation_examples, top_k=None, explain_subset=None, features=None,
                       classes=None, sampling_policy=None, create_scoring_model=False):
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
                  ExplainParams.TOP_K: top_k}
        if classes is not None:
            kwargs[ExplainParams.CLASSES] = classes
        return self._explain_global(evaluation_examples, **kwargs)

    @tabular_decorator
    def explain_local(self, evaluation_examples, explain_subset=None, features=None, classes=None):
        """Explain the model by using shap's tree explainer.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: DatasetWrapper
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
        # is_valid has not been called
        if self.explainer is None and not self.is_valid():
            raise Exception('Model not supported by TreeExplainer')

        self._logger.debug('Explaining tree model')
        kwargs = {}
        if classes is not None:
            kwargs[ExplainParams.CLASSES] = classes
        kwargs[ExplainParams.FEATURES] = evaluation_examples.get_features(features=features)
        evaluation_examples = evaluation_examples.dataset

        # for now convert evaluation examples to dense format if they are sparse
        # until TreeExplainer sparse support is added
        shap_values = self.explainer.shap_values(_get_dense_examples(evaluation_examples))
        classification = isinstance(shap_values, list)
        # Reformat shap values result if explain_subset specified
        if explain_subset:
            self._logger.debug('Getting subset of shap_values')
            if classification:
                for i in range(shap_values.shape[0]):
                    shap_values[i] = shap_values[i][:, explain_subset]
            else:
                shap_values = shap_values[:, explain_subset]
        expected_values = None
        if hasattr(self.explainer, Attributes.EXPECTED_VALUE):
            self._logger.debug('Expected values available on explainer')
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
