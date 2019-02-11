# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the LIMEExplainer for computing explanations on black box models using LIME."""

from lime.lime_tabular import LimeTabularExplainer
from shap.common import DenseData

from ..common.blackbox_explainer import AggregateBlackBoxExplainer
from ..scoring.scoring_model import KNNScoringModel
from ..explanation.explanation import _create_local_explanation
from ..dataset.decorator import tabular_decorator
from azureml.explain.model._internal.constants import ExplanationParams, ExplainParams, ExplainType


class LIMEExplainer(AggregateBlackBoxExplainer):
    """Defines the LIME Explainer for explaining black box models or functions."""

    def __init__(self, model, initialization_examples, is_function=False, **kwargs):
        """Initialize the LIME Explainer.

        :param model: The model to explain or function if is_function is True.
        :type model: model that implements predict or predict_proba or function that accepts a 2d ndarray
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        :param is_function: Default set to false, set to True if passing function instead of model.
        :type is_function: bool
        """
        super(LIMEExplainer, self).__init__(model, initialization_examples, is_function=is_function, **kwargs)
        self._logger.debug('Initializing LIMEExplainer')
        self.is_classification = False

    def _is_function_valid(self, function, features=None, classes=None,
                           silent=True, categorical_features=[], **kwargs):
        try:
            function, summary = self._prepare_function_and_summary(function, self.original_data_ref,
                                                                   self.current_index_list, **kwargs)
            if isinstance(summary, DenseData):
                summary = summary.data
            result = function(summary[0].reshape((1, -1)))
            # If result is 2D array, this is classification scenario, otherwise regression
            if len(result.shape) == 2:
                self.is_classification = True
                mode = ExplainType.CLASSIFICATION
            elif len(result.shape) == 1:
                self.is_classification = False
                mode = ExplainType.REGRESSION
            else:
                raise Exception('Invalid function specified, does not conform to specifications on prediction')
            self.explainer = LimeTabularExplainer(summary, feature_names=features, class_names=classes,
                                                  categorical_features=categorical_features, verbose=not silent,
                                                  mode=mode, discretize_continuous=False)
            self.explainer.function = function
        except Exception as ex:
            self._logger.debug('Function is invalid, failing with exception: {}'.format(ex))
            return False
        self._logger.debug('Function is valid')
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
            features in the evaluation dataset for explanation, which will speed up the explanation
            process when number of features is large and the user already knows the set of interested
            features. The subset can be the top-k features from the model summary.
        :type explain_subset: list[int]
        :param features: A list of feature names.
        :type features: list[str]
        :param classes: Class names as a list of strings. The order of the class names should match
            that of the model output.  Only required if explaining classifier.
        :type classes: list[str]
        :param nclusters: Number of means to use for approximation. A dataset is summarized with nclusters mean
            samples weighted by the number of data points they each represent. When the number of initialization
            examples is larger than (10 x nclusters), those examples will be summarized with k-means where
            k = nclusters.
        :type nclusters: int
        :param sampling_policy: Optional policy for sampling the evaluation examples.  See documentation on
            SamplingPolicy for more information.
        :type sampling_policy: SamplingPolicy
        :param create_scoring_model: Creates a model that can be used for scoring to approximate the feature
            importance values of data faster than LimeTabularExplainer.
        :type create_scoring_model: bool
        :return: A model explanation object containing the global explanation.
        :rtype: GlobalExplanation
        """
        kwargs = {ExplainParams.EXPLAIN_SUBSET: explain_subset, ExplainParams.FEATURES: features,
                  ExplainParams.SAMPLING_POLICY: sampling_policy,
                  ExplainParams.CREATE_SCORING_MODEL: create_scoring_model,
                  ExplainParams.TOP_K: top_k, ExplainParams.NCLUSTERS: nclusters}
        if classes is not None:
            kwargs[ExplainParams.CLASSES] = classes
        return self._explain_global(evaluation_examples, **kwargs)

    @tabular_decorator
    def explain_local(self, evaluation_examples, explain_subset=None, features=None,
                      classes=None, nclusters=10):
        """Explain the function locally by using LIME.

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
        :param nclusters: Number of means to use for approximation. A dataset is summarized with nclusters mean
            samples weighted by the number of data points they each represent. When the number of initialization
            examples is larger than (10 x nclusters), those examples will be summarized with k-means where
            k = nclusters.
        :type nclusters: int
        :return: A model explanation object containing the local explanation.
        :rtype: LocalExplanation
        """
        if self.explainer is None and not self._is_function_valid(self.function, explain_subset=explain_subset,
                                                                  features=features, nclusters=nclusters):
            raise Exception('Model not supported by LIMEExplainer')

        if classes is None and self.is_classification:
            raise ValueError('LIME Explainer requires classes to be specified')
        if classes is not None and not self.is_classification:
            if self.model is None:
                error = 'Classes is specified but function was predict, not predict_proba.'
            else:
                error = 'Classes is specified but model does not define predict_proba, only predict.'
            raise ValueError(error)

        # Compute subset info prior
        if explain_subset:
            evaluation_examples.take_subset(explain_subset)

        # sample the evaluation examples
        # note: the sampled data is also used by KNN
        if self.sampling_policy is not None and self.sampling_policy.allow_eval_sampling:
            sampling_method = self.sampling_policy.sampling_method
            max_dim_clustering = self.sampling_policy.max_dim_clustering
            evaluation_examples.sample(max_dim_clustering, sampling_method=sampling_method)
        features = evaluation_examples.get_features(features=features)
        if explain_subset:
            features = features[explain_subset]
        kwargs = {}
        if classes is not None:
            kwargs[ExplainParams.CLASSES] = classes
        kwargs[ExplainParams.FEATURES] = features
        original_evaluation = evaluation_examples.original_dataset
        evaluation_examples = evaluation_examples.dataset

        self._logger.debug('Running LIMEExplainer')
        if self.is_classification:
            kwargs[ExplanationParams.CLASSES] = classes
            num_classes = len(classes)
            labels = list(range(num_classes))
        else:
            num_classes = 1
            labels = None
        lime_explanations = []
        if explain_subset:
            self.original_data_ref[0] = original_evaluation
            self.current_index_list.append(0)
            for ex_idx, example in enumerate(evaluation_examples):
                self.current_index_list[0] = ex_idx
                lime_explanations.append(self.explainer.explain_instance(example,
                                                                         self.explainer.function,
                                                                         labels=labels))
            self.current_index_list = [0]
        else:
            for ex_idx, example in enumerate(evaluation_examples):
                lime_explanations.append(self.explainer.explain_instance(example,
                                                                         self.explainer.function,
                                                                         labels=labels))
        self.explainer = None
        if self.is_classification:
            lime_values = [None] * num_classes
            for lime_explanation in lime_explanations:
                for label in labels:
                    map_values = dict(lime_explanation.as_list(label=label))
                    if lime_values[label - 1] is None:
                        lime_values[label - 1] = [[map_values.get(feature, 0.0) for feature in features]]
                    else:
                        lime_values[label - 1].append([map_values.get(feature, 0.0) for feature in features])
        else:
            lime_values = None
            for lime_explanation in lime_explanations:
                map_values = dict(lime_explanation.as_list())
                if lime_values is None:
                    lime_values = [[map_values.get(feature, 0.0) for feature in features]]
                else:
                    lime_values.append([map_values.get(feature, 0.0) for feature in features])
        expected_values = None
        scoring_model = None
        if self.create_scoring_model:
            scoring_model = KNNScoringModel(evaluation_examples, lime_values)
        return _create_local_explanation(local_importance_values=lime_values,
                                         expected_values=expected_values,
                                         classification=self.is_classification,
                                         scoring_model=scoring_model,
                                         **kwargs)
