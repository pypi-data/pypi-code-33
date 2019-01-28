# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the aggregate explainer mixin for aggregating local explanations to global."""

from ..tabular_dataset_explainer import TabularDatasetExplainer
from ..explanation.explanation import aggregate_global_from_local_explanation
from azureml.explain.model._internal.constants import Defaults


class AggregateExplainer(TabularDatasetExplainer):
    """A mixin for aggregating local explanations to global."""

    def __init__(self, **kwargs):
        """Initialize the AggregateExplainer."""
        super(AggregateExplainer, self).__init__(**kwargs)
        self._logger.debug('Initializing AggregateExplainer')

    def _explain_global(self, evaluation_examples, explain_subset=None, allow_eval_sampling=False,
                        max_dim_clustering=Defaults.MAX_DIM, sampling_method=Defaults.HDBSCAN,
                        silent=True, nsamples=Defaults.AUTO, features=None,
                        create_scoring_model=False, top_k=None, **kwargs):
        """Explains the model by aggregating local explanations to global.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return: A model explanation object containing the local and global explanation.
        :rtype: BaseExplanation
        """
        self.allow_eval_sampling = allow_eval_sampling
        self.max_dim_clustering = max_dim_clustering
        self.sampling_method = sampling_method
        self.create_scoring_model = create_scoring_model
        # first get local explanation
        local_explanation = self._explain_local(evaluation_examples, explain_subset=explain_subset,
                                                silent=silent, nsamples=nsamples, features=features, **kwargs)
        # Aggregate local explanation to global
        return aggregate_global_from_local_explanation(local_explanation=local_explanation, top_k=top_k, **kwargs)
