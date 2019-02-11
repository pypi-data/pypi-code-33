# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the aggregate explainer mixin for aggregating local explanations to global."""

from .base_explainer import BaseExplainer
from ..explanation.explanation import _aggregate_global_from_local_explanation
from azureml.explain.model._internal.constants import ExplainParams


class AggregateExplainer(BaseExplainer):
    """A mixin for aggregating local explanations to global."""

    def __init__(self, **kwargs):
        """Initialize the AggregateExplainer."""
        super(AggregateExplainer, self).__init__(**kwargs)
        self._logger.debug('Initializing AggregateExplainer')
        self.sampling_policy = None

    def _explain_global(self, evaluation_examples, explain_subset=None, sampling_policy=None,
                        silent=None, nsamples=None, features=None, nclusters=None,
                        create_scoring_model=False, top_k=None, **kwargs):
        """Explains the model by aggregating local explanations to global.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return: A model explanation object containing the local and global explanation.
        :rtype: BaseExplanation
        """
        self.sampling_policy = sampling_policy
        self.create_scoring_model = create_scoring_model
        local_args = dict(kwargs)
        local_args[ExplainParams.EXPLAIN_SUBSET] = explain_subset
        local_args[ExplainParams.FEATURES] = features
        if silent is not None:
            local_args[ExplainParams.SILENT] = silent
        if nsamples is not None:
            local_args[ExplainParams.NSAMPLES] = nsamples
        if nclusters is not None:
            local_args[ExplainParams.NCLUSTERS] = nclusters
        # first get local explanation
        local_explanation = self.explain_local(evaluation_examples, **local_args)
        # Aggregate local explanation to global
        return _aggregate_global_from_local_explanation(local_explanation=local_explanation, top_k=top_k, **kwargs)
