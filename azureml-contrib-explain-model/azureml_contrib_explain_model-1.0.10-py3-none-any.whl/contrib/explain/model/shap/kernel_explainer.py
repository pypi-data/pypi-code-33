# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the KernelExplainer for computing explanations on black box models or pipeline functions."""

import numpy as np
import shap

from ..common.blackbox_explainer import AggregateBlackBoxExplainer
from ..common.explanation_utils import _convert_to_list
from ..scoring.scoring_model import KNNScoringModel
from ..explanation.explanation import create_local_explanation
from ..dataset.dataset_wrapper import DatasetWrapper
from azureml.explain.model._internal.constants import Defaults, Attributes, ExplainParams


class KernelExplainer(AggregateBlackBoxExplainer):
    """Defines the Kernel Explainer for explaining black box models or pipeline functions."""

    def __init__(self, model, initialization_examples, is_pipeline=False, **kwargs):
        """Initialize the KernelExplainer.

        :param model: The model to explain or pipeline if is_pipeline is True.
        :type model: model that implements predict or predict_proba or pipeline function that accepts a 2d ndarray
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        :param is_pipeline: Default set to false, set to True if passing pipeline instead of model.
        :type is_pipeline: bool
        """
        super(KernelExplainer, self).__init__(model, initialization_examples, is_pipeline=is_pipeline,
                                              **kwargs)
        self._logger.debug('Initializing KernelExplainer')

    def _is_pipeline_valid(self, pipeline, explain_subset=None, **kwargs):
        try:
            self._reset_evaluation_background(pipeline, explain_subset=explain_subset, **kwargs)
        except Exception as ex:
            self._logger.debug('Pipeline is invalid, failing with exception: {}'.format(ex))
            return False
        self._logger.debug('Pipeline is valid')
        return True

    def _reset_evaluation_background(self, pipeline, explain_subset=None, **kwargs):
        """Modify the explainer to use the new evalaution example for background data.

        Note that when calling is_valid an evaluation example is not available hence the initialization data is used.

        :param pipeline: Pipeline function.
        :type pipeline: Pipeline function that accepts a 2d ndarray
        :param explain_subset: List of feature indices. If specified, only selects a subset of the
            features in the evaluation dataset for explanation, which will speed up the explanation
            process when number of features is large and the user already knows the set of interested
            features. The subset can be the top-k features from the model summary.
        :type explain_subset: list[int]
        """
        pipeline, summary = self._prepare_pipeline_and_summary(pipeline, self.original_data_ref,
                                                               self.current_index_list,
                                                               explain_subset=explain_subset, **kwargs)
        self.explainer = shap.KernelExplainer(pipeline, summary)

    def _reset_wrapper(self):
            self.explainer = None
            self.current_index_list = [0]
            self.original_data_ref = [None]
            self.initialization_examples = DatasetWrapper(self.initialization_examples.original_dataset)

    def _explain_local(self, evaluation_examples, explain_subset=None, silent=True,
                       nsamples=Defaults.AUTO, features=None, **kwargs):
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
        if explain_subset:
            # Need to reset state before and after explaining a subset of data with wrapper function
            self._reset_wrapper()
        if self.explainer is None and not self._is_pipeline_valid(self.pipeline, explain_subset=explain_subset,
                                                                  **kwargs):
            raise Exception('Model not supported by KernelExplainer')

        # Compute subset info prior
        if explain_subset:
            evaluation_examples.take_subset(explain_subset)

        # sample the evaluation examples
        # Note: the sampled data is also used by KNN when scoring
        if self.allow_eval_sampling:
            evaluation_examples.sample(self.max_dim_clustering, sampling_method=self.sampling_method)
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
                self._reset_evaluation_background(self.pipeline, explain_subset=explain_subset, **kwargs)
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
        return create_local_explanation(local_importance_values=local_importance_values,
                                        expected_values=expected_values,
                                        classification=classification,
                                        scoring_model=scoring_model, **kwargs)
