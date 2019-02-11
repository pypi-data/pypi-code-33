# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the tabular explainer meta-api for returning the best explanation result based on the given model."""

from .common.base_explainer import BaseExplainer
from .common.structured_model_explainer import PureStructuredModelExplainer
from .shap.tree_explainer import TreeExplainer
from .shap.deep_explainer import DeepExplainer
from .shap.kernel_explainer import KernelExplainer
from .dataset.dataset_wrapper import DatasetWrapper
from .dataset.decorator import tabular_decorator
from azureml.explain.model._internal.constants import ExplainParams

InvalidExplainerErr = 'Could not find valid explainer to explain model'


def _tabular_explainer_decorator(explain_func):
    """Decorate an explanation function to validate the model prior to calling the function.

    :param explain_func: An explanation function where the first argument is a dataset.
    :type explain_func: explanation function
    """
    def explain_func_wrapper(self, evaluation_examples, **kwargs):
        self._logger.debug('Explaining tabular data')
        if self.is_valid(**kwargs):
            self._logger.debug("Validated explainer {} with args {}".format(self.explainer, kwargs))
            return explain_func(self, evaluation_examples, **kwargs)
        self._logger.info(InvalidExplainerErr)
        raise ValueError(InvalidExplainerErr)
    return explain_func_wrapper


class TabularExplainer(BaseExplainer):
    """Defines the tabular explainer meta-api for returning the best explanation result based on the given model."""

    def __init__(self, model, initialization_examples, **kwargs):
        """Initialize the TabularExplainer.

        :param model: The model or pipeline to explain.
        :type model: model that implements predict or predict_proba or pipeline function that accepts a 2d ndarray
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        """
        super(TabularExplainer, self).__init__(**kwargs)
        self._logger.debug('Initializing TabularExplainer')
        self.model = model
        if not isinstance(initialization_examples, DatasetWrapper):
            self._logger.debug('Wrapping init examples with DatasetWrapper')
            self.initialization_examples = DatasetWrapper(initialization_examples)
        else:
            self.initialization_examples = initialization_examples
        uninitialized_explainers = [TreeExplainer, DeepExplainer, KernelExplainer]
        _is_valid = False
        for uninitialized_explainer in uninitialized_explainers:
            if issubclass(uninitialized_explainer, PureStructuredModelExplainer):
                self.explainer = uninitialized_explainer(self.model)
            else:
                self.explainer = uninitialized_explainer(self.model, self.initialization_examples)
            if self.explainer.is_valid(**kwargs):
                _is_valid = True
                self._logger.info('Initialized valid explainer {} with args {}'.format(self.explainer, kwargs))
                break
        if not _is_valid:
            self._logger.info(InvalidExplainerErr)
            raise ValueError(InvalidExplainerErr)

    @tabular_decorator
    @_tabular_explainer_decorator
    def explain_global(self, evaluation_examples, top_k=None, explain_subset=None, features=None,
                       classes=None, sampling_policy=None, create_scoring_model=False):
        """Globally explains the black box model or function.

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
                  ExplainParams.TOP_K: top_k}
        if classes is not None:
            kwargs[ExplainParams.CLASSES] = classes
        return self.explainer.explain_global(evaluation_examples, **kwargs)

    @tabular_decorator
    @_tabular_explainer_decorator
    def explain_local(self, evaluation_examples, explain_subset=None, features=None,
                      classes=None):
        """Locally explains the black box model or function.

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
        kwargs = {ExplainParams.EXPLAIN_SUBSET: explain_subset, ExplainParams.FEATURES: features}
        if classes is not None:
            kwargs[ExplainParams.CLASSES] = classes
        return self.explainer.explain_local(evaluation_examples, **kwargs)

    def is_valid(self, **kwargs):
        """Determine if the given model is valid.

        Runs all initialized explainers and validates the given model is valid for at least one of them.
        """
        # Note: we rerun the original explainer instead of caching on init because args could be different
        # and supposedly explainer may throw (eg if invalid subset is specified).
        return self.explainer.is_valid(**kwargs)
