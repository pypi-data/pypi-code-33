# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the Mimic Explainer for computing explanations on black box models or functions.

The mimic explainer trains an explainable model to reproduce the output of the given black box model.
The explainable model is called a surrogate model and the black box model is called a teacher model.
Once trained to reproduce the output of the teacher model, the surrogate model's explanation can
be used to explain the teacher model.
"""

import numpy as np
from shap.common import DenseData

from azureml.explain.model._internal.common import _order_imp

from ..common.blackbox_explainer import BlackBoxExplainer
from ..common.explanation_utils import _convert_to_list, _generate_augmented_data
from ..scoring.scoring_model import TreeScoringModel

from .model_distill import model_distill
from ..explanation.explanation import _create_local_explanation, _create_global_explanation, \
    _aggregate_global_from_local_explanation
from ..dataset.decorator import tabular_decorator
from ..dataset.dataset_wrapper import DatasetWrapper
from azureml.explain.model._internal.constants import ExplainParams


class MimicExplainer(BlackBoxExplainer):
    """Defines the Mimic Explainer for explaining black box models or functions."""

    def __init__(self, model, initialization_examples, explainable_model, is_function=False, augment_data=True,
                 max_num_of_augmentations=1000, **kwargs):
        """Initialize the MimicExplainer.

        :param model: The model or function (if is_function is True) to be explained.
        :type model: model that implements predict or predict_proba or function that accepts a 2d ndarray
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        :param is_function: Default set to false, set to True if passing function instead of model.
        :type is_function: bool
        :param max_num_of_augmentations: max number of times we can increase the input data size.
        :type max_num_of_augmentations: int
        """
        super(MimicExplainer, self).__init__(model, initialization_examples, is_function=is_function,
                                             **kwargs)
        self._logger.debug('Initializing MimicExplainer')
        # Train the mimic model on the given model
        try:
            training_data = self.initialization_examples.dataset
            if isinstance(training_data, DenseData):
                training_data = training_data.data

            # augment the data if necessary
            if augment_data:
                training_data = _generate_augmented_data(training_data,
                                                         max_num_of_augmentations=max_num_of_augmentations)
            self.surrogate_model = model_distill(self.function, explainable_model, training_data)
        except Exception as ex:
            self._logger.debug('Pipeline is invalid, failing with exception: {}'.format(ex))
            self.invalid_function = True

    def _is_function_valid(self, function, **kwargs):
        return not self.invalid_function

    def explain_global(self, evaluation_examples=None, top_k=None, explain_subset=None,
                       create_scoring_model=False, features=None, classes=None):
        """Globally explains the blackbox model using the surrogate model.

        If evaluation_examples are unspecified, retrieves global feature importances from explainable
        surrogate model.  Note this will not include per class feature importances.  If evaluation_examples
        are specified, aggregates local explanations to global from the given evaluation_examples - which
        computes both global and per class feature importances.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which to
            explain the model's output.  If specified, computes feature importances through aggregation.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param top_k: Number of important features stored in the explanation. If specified, only the
            names and values corresponding to the top K most important features will be returned/stored.
        :type top_k: int
        :param explain_subset: List of feature indices. If specified, only selects a subset of the
            features in the evaluation dataset for explanation. Note for mimic explainer this will
            not affect the execution time of getting the global explanation.
        :type explain_subset: list[int]
        :param create_scoring_model: Creates a TreeExplainer that can be operationalized for
            local model explanations.
        :type create_scoring_model: bool
        :param features: A list of feature names.
        :type features: list[str]
        :param classes: Class names as a list of strings. The order of the class names should match
            that of the model output.  Only required if explaining classifier.
        :type classes: list[str]
        :return: Global explanation of given evaluation examples.
        :rtype: GlobalExplanation
        """
        self.create_scoring_model = create_scoring_model
        is_classification = self.predict_proba_flag
        kwargs = {}
        if is_classification:
            kwargs[ExplainParams.CLASSES] = classes
        if evaluation_examples is not None:
            if not isinstance(evaluation_examples, DatasetWrapper):
                self._logger.debug('Eval examples not wrapped, wrapping')
                evaluation_examples = DatasetWrapper(evaluation_examples)
            # first get local explanation
            local_explanation = self.explain_local(evaluation_examples, explain_subset=explain_subset,
                                                   features=features)
            # Aggregate local explanation to global
            return _aggregate_global_from_local_explanation(local_explanation=local_explanation,
                                                            top_k=top_k, **kwargs)
        global_importance_values = self.surrogate_model.explain_global()
        order = _order_imp(global_importance_values)
        if top_k is not None:
            order = order[0:top_k]
        global_importance_values = global_importance_values[order]
        classification = self.predict_proba_flag
        scoring_model = None
        if self.create_scoring_model:
            scoring_model = TreeScoringModel(self.surrogate_model.model)
        return _create_global_explanation(expected_values=None, classification=classification,
                                          scoring_model=scoring_model,
                                          global_importance_values=global_importance_values,
                                          global_importance_rank=order, features=features,
                                          **kwargs)

    @tabular_decorator
    def explain_local(self, evaluation_examples, features=None, explain_subset=None, classes=None):
        """Locally explains the blackbox model using the surrogate model.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param features: A list of feature names.
        :type features: list[str]
        :param explain_subset: List of feature indices. If specified, only selects a subset of the
            features in the evaluation dataset for explanation.  Note for mimic explainer this will
            not affect the execution time of getting the local explanation.
        :type explain_subset: list[int]
        :param classes: Class names as a list of strings. The order of the class names should match
            that of the model output.
        :type classes: list[str]
        :return: Explanation of given evaluation examples.
        :rtype: LocalExplanation
        """
        local_importance_values = self.surrogate_model.explain_local(evaluation_examples.dataset)
        expected_values = None
        is_classification = self.predict_proba_flag
        is_binary = isinstance(local_importance_values, np.ndarray)
        # If binary case, we need to reformat the data to have importances per class
        if is_classification and is_binary:
            local_importance_values = [-local_importance_values, local_importance_values]
        scoring_model = None
        if self.create_scoring_model:
            scoring_model = TreeScoringModel(self.surrogate_model.model)
        kwargs = {ExplainParams.FEATURES: features}
        if is_classification:
            kwargs[ExplainParams.CLASSES] = classes
        # Reformat local_importance_values result if explain_subset specified
        if explain_subset:
            self._logger.debug('Getting subset of local_importance_values')
            if is_classification:
                for i in range(len(local_importance_values)):
                    local_importance_values[i] = local_importance_values[i][:, explain_subset]
            else:
                local_importance_values = local_importance_values[:, explain_subset]
        local_importance_values = _convert_to_list(local_importance_values)
        return _create_local_explanation(local_importance_values=local_importance_values,
                                         expected_values=expected_values,
                                         classification=is_classification,
                                         scoring_model=scoring_model, **kwargs)
