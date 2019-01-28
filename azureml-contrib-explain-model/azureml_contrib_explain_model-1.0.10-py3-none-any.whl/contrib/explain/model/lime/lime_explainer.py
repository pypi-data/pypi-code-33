# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the LIMEExplainer for computing explanations on black box models using LIME."""

from lime.lime_tabular import LimeTabularExplainer
from shap.common import DenseData

from ..common.blackbox_explainer import AggregateBlackBoxExplainer
from ..scoring.scoring_model import KNNScoringModel
from ..explanation.explanation import create_local_explanation
from azureml.explain.model._internal.constants import Defaults, ExplanationParams, ExplainParams, ExplainType


class LIMEExplainer(AggregateBlackBoxExplainer):
    """Defines the LIME Explainer for explaining black box models or pipeline functions."""

    def __init__(self, model, initialization_examples, is_pipeline=False, **kwargs):
        """Initialize the LIME Explainer.

        :param model: The model to explain or pipeline if is_pipeline is True.
        :type model: model that implements predict or predict_proba or pipeline function that accepts a 2d ndarray
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        :param is_pipeline: Default set to false, set to True if passing pipeline instead of model.
        :type is_pipeline: bool
        """
        super(LIMEExplainer, self).__init__(model, initialization_examples, is_pipeline=is_pipeline, **kwargs)
        self._logger.debug('Initializing LIMEExplainer')
        self.is_classification = False

    def _is_pipeline_valid(self, pipeline, features=None, classes=None,
                           silent=True, categorical_features=[], **kwargs):
        try:
            pipeline, summary = self._prepare_pipeline_and_summary(pipeline, self.original_data_ref,
                                                                   self.current_index_list, **kwargs)
            if isinstance(summary, DenseData):
                summary = summary.data
            result = pipeline(summary[0].reshape((1, -1)))
            # If result is 2D array, this is classification scenario, otherwise regression
            if len(result.shape) == 2:
                self.is_classification = True
                mode = ExplainType.CLASSIFICATION
            elif len(result.shape) == 1:
                self.is_classification = False
                mode = ExplainType.REGRESSION
            else:
                raise Exception('Invalid pipeline specified, does not conform to specifications on prediction')
            self.explainer = LimeTabularExplainer(summary, feature_names=features, class_names=classes,
                                                  categorical_features=categorical_features, verbose=not silent,
                                                  mode=mode, discretize_continuous=False)
            self.explainer.pipeline = pipeline
        except Exception as ex:
            self._logger.debug('Pipeline is invalid, failing with exception: {}'.format(ex))
            return False
        self._logger.debug('Pipeline is valid')
        return True

    def _explain_local(self, evaluation_examples, explain_subset=None, silent=True,
                       nsamples=Defaults.AUTO, features=None, classes=None, **kwargs):
        """Explains the pipeline function.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: DatasetWrapper
        :param explain_subset: List of feature indices. If specified, only selects a subset of the
            features in the evaluation dataset for explanation, which will speed up the explanation
            process when number of features is large and the user already knows the set of interested
            features. The subset can be the top-k features from the model summary.
        :type explain_subset: list[int]
        :param nsamples: Default to 'auto'. Number of times to re-evaluate the model when
            explaining each prediction. More samples lead to lower variance estimates of the
            feature importance values, but incur more computation cost. When "auto" is provided,
            the number of samples is computed according to a heuristic rule.
        :type nsamples: "auto" or int
        :param silent: Default to 'False'.  Determines whether to display the explanation status bar
            when using shap_values from the KernelExplainer.
        :type silent: bool
        :param features: A list of feature names.
        :type features: list[str]
        :return: A model explanation object containing the local explanation.
        :rtype: LocalExplanation
        """
        if self.explainer is None and not self._is_pipeline_valid(self.pipeline, explain_subset=explain_subset,
                                                                  features=features, **kwargs):
            raise Exception('Model not supported by LIMEExplainer')

        if classes is None and self.is_classification:
            raise Exception('LIME Explainer requires classes to be specified')

        # Compute subset info prior
        if explain_subset:
            evaluation_examples.take_subset(explain_subset)

        # sample the evaluation examples
        # note: the sampled data is also used by KNN
        if self.allow_eval_sampling:
            evaluation_examples.sample(self.max_dim_clustering, sampling_method=self.sampling_method)
        features = evaluation_examples.get_features(features=features)
        if explain_subset:
            features = features[explain_subset]
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
                                                                         self.explainer.pipeline,
                                                                         labels=labels))
            self.current_index_list = [0]
        else:
            for ex_idx, example in enumerate(evaluation_examples):
                lime_explanations.append(self.explainer.explain_instance(example,
                                                                         self.explainer.pipeline,
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
        return create_local_explanation(local_importance_values=lime_values,
                                        expected_values=expected_values,
                                        classification=self.is_classification,
                                        scoring_model=scoring_model,
                                        **kwargs)
