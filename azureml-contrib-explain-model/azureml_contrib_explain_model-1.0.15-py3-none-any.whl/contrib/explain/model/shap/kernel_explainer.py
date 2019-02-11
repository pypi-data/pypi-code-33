# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the KernelExplainer for computing explanations on black box models or functions."""

import numpy as np
import shap

from ..common.blackbox_explainer import AggregateBlackBoxExplainer
from ..common.explanation_utils import _convert_to_list
from ..scoring.scoring_model import KNNScoringModel
from ..explanation.explanation import _create_local_explanation
from ..dataset.dataset_wrapper import DatasetWrapper
from ..dataset.decorator import tabular_decorator
from azureml.explain.model._internal.constants import Defaults, Attributes, ExplainParams


class KernelExplainer(AggregateBlackBoxExplainer):
    """Defines the Kernel Explainer for explaining black box models or functions."""

    def __init__(self, model, initialization_examples, is_function=False, **kwargs):
        """Initialize the KernelExplainer.

        :param model: The model to explain or function if is_function is True.
        :type model: model that implements predict or predict_proba or function that accepts a 2d ndarray
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        :param is_function: Default set to false, set to True if passing function instead of model.
        :type is_function: bool
        """
        super(KernelExplainer, self).__init__(model, initialization_examples, is_function=is_function,
                                              **kwargs)
        self._logger.debug('Initializing KernelExplainer')

    def _is_function_valid(self, function, explain_subset=None, **kwargs):
        try:
            self._reset_evaluation_background(function, explain_subset=explain_subset, **kwargs)
        except Exception as ex:
            self._logger.debug('Function is invalid, failing with exception: {}'.format(ex))
            return False
        self._logger.debug('Function is valid')
        return True

    def _reset_evaluation_background(self, function, explain_subset=None, **kwargs):
        """Modify the explainer to use the new evalaution example for background data.

        Note that when calling is_valid an evaluation example is not available hence the initialization data is used.

        :param function: Function.
        :type function: Function that accepts a 2d ndarray
        :param explain_subset: List of feature indices. If specified, only selects a subset of the
            features in the evaluation dataset for explanation, which will speed up the explanation
            process when number of features is large and the user already knows the set of interested
            features. The subset can be the top-k features from the model summary.
        :type explain_subset: list[int]
        """
        function, summary = self._prepare_function_and_summary(function, self.original_data_ref,
                                                               self.current_index_list,
                                                               explain_subset=explain_subset, **kwargs)
        self.explainer = shap.KernelExplainer(function, summary)

    def _reset_wrapper(self):
            self.explainer = None
            self.current_index_list = [0]
            self.original_data_ref = [None]
            self.initialization_examples = DatasetWrapper(self.initialization_examples.original_dataset)

    @tabular_decorator
    def explain_global(self, evaluation_examples, top_k=None, explain_subset=None, silent=True,
                       nsamples=Defaults.AUTO, features=None, classes=None, nclusters=10,
                       sampling_policy=None, create_scoring_model=False):
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
            importance values of data faster than shap's KernelExplainer.
        :type create_scoring_model: bool
        :return: A model explanation object containing the global explanation.
        :rtype: GlobalExplanation
        """
        kwargs = {ExplainParams.EXPLAIN_SUBSET: explain_subset, ExplainParams.SILENT: silent,
                  ExplainParams.NSAMPLES: nsamples, ExplainParams.FEATURES: features,
                  ExplainParams.SAMPLING_POLICY: sampling_policy,
                  ExplainParams.CREATE_SCORING_MODEL: create_scoring_model,
                  ExplainParams.TOP_K: top_k, ExplainParams.NCLUSTERS: nclusters}
        if classes is not None:
            kwargs[ExplainParams.CLASSES] = classes
        return self._explain_global(evaluation_examples, **kwargs)

    @tabular_decorator
    def explain_local(self, evaluation_examples, explain_subset=None, silent=True,
                      nsamples=Defaults.AUTO, features=None, classes=None, nclusters=10):
        """Explain the function locally by using SHAP's KernelExplainer.

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
        if explain_subset:
            # Need to reset state before and after explaining a subset of data with wrapper function
            self._reset_wrapper()
        if self.explainer is None and not self._is_function_valid(self.function, explain_subset=explain_subset,
                                                                  nclusters=nclusters):
            raise Exception('Model not supported by KernelExplainer')

        # Compute subset info prior
        if explain_subset:
            evaluation_examples.take_subset(explain_subset)

        # sample the evaluation examples
        # Note: the sampled data is also used by KNN when scoring
        if self.sampling_policy is not None and self.sampling_policy.allow_eval_sampling:
            sampling_method = self.sampling_policy.sampling_method
            max_dim_clustering = self.sampling_policy.max_dim_clustering
            evaluation_examples.sample(max_dim_clustering, sampling_method=sampling_method)
        kwargs = {}
        if classes is not None:
            kwargs[ExplainParams.CLASSES] = classes
        kwargs[ExplainParams.FEATURES] = evaluation_examples.get_features(features=features,
                                                                          explain_subset=explain_subset)
        original_evaluation = evaluation_examples.original_dataset
        evaluation_examples = evaluation_examples.dataset

        self._logger.debug('Running KernelExplainer')

        if explain_subset:
            self.original_data_ref[0] = original_evaluation
            self.current_index_list.append(0)
            output_shap_values = None
            for ex_idx, example in enumerate(evaluation_examples):
                # Note: when subsetting with KernelExplainer, for correct results we need to
                # set the background to be the evaluation data for columns not specified in subset
                self._reset_evaluation_background(self.function, explain_subset=explain_subset, nclusters=nclusters)
                self.current_index_list[0] = ex_idx
                tmp_shap_values = self.explainer.shap_values(example, silent=silent, nsamples=nsamples)
                classification = isinstance(tmp_shap_values, list)
                if classification:
                    if output_shap_values is None:
                        output_shap_values = tmp_shap_values
                        for i in range(len(output_shap_values)):
                            cols_dim = len(output_shap_values[i].shape)
                            concat_cols = output_shap_values[i].shape[cols_dim - 1]
                            output_shap_values[i] = output_shap_values[i].reshape(1, concat_cols)
                    else:
                        for i in range(len(output_shap_values)):
                            cols_dim = len(tmp_shap_values[i].shape)
                            # col_dim can only be 1 or 2 here, depending on data passed to shap
                            if cols_dim != 2:
                                out_cols_dim = len(output_shap_values[i].shape)
                                output_size = output_shap_values[i].shape[out_cols_dim - 1]
                                tmp_shap_values_2d = tmp_shap_values[i].reshape(1, output_size)
                            else:
                                tmp_shap_values_2d = tmp_shap_values[i]
                            # Append rows
                            output_shap_values[i] = np.append(output_shap_values[i],
                                                              tmp_shap_values_2d, axis=0)
                else:
                    if output_shap_values is None:
                        output_shap_values = tmp_shap_values
                    else:
                        output_shap_values = np.append(output_shap_values, tmp_shap_values, axis=0)
            # Need to reset state before and after explaining a subset of data with wrapper function
            self._reset_wrapper()
            shap_values = output_shap_values
        else:
            shap_values = self.explainer.shap_values(evaluation_examples, silent=silent, nsamples=nsamples)

        classification = isinstance(shap_values, list)
        expected_values = None
        if hasattr(self.explainer, Attributes.EXPECTED_VALUE):
            expected_values = self.explainer.expected_value
            if isinstance(expected_values, np.ndarray):
                expected_values = expected_values.tolist()
        local_importance_values = _convert_to_list(shap_values)
        scoring_model = None
        if self.create_scoring_model:
            scoring_model = KNNScoringModel(evaluation_examples, local_importance_values)
        return _create_local_explanation(local_importance_values=local_importance_values,
                                         expected_values=expected_values,
                                         classification=classification,
                                         scoring_model=scoring_model, **kwargs)
