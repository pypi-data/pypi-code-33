# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the black box explainer API, which can either take in a black box model or function."""

from abc import abstractmethod
import numpy as np
import scipy as sp

from .base_explainer import BaseExplainer
from ..dataset.dataset_wrapper import DatasetWrapper
from .aggregate_explainer import AggregateExplainer


class BlackBoxExplainer(BaseExplainer):
    """The base class for black box models or functions."""

    def __init__(self, model, initialization_examples, is_function=False, **kwargs):
        """Initialize the BlackBoxExplainer.

        :param model: The model to explain or function if is_function is True.
        :type model: model that implements predict or predict_proba or function that accepts a 2d ndarray
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        :param is_function: Default set to false, set to True if passing predict or predict_proba
            function instead of model.
        :type is_function: bool
        """
        super(BlackBoxExplainer, self).__init__(**kwargs)
        self._logger.debug('Initializing BlackBoxExplainer')
        # If true, this is a classification model
        self.predict_proba_flag = hasattr(model, "predict_proba")

        if not isinstance(initialization_examples, DatasetWrapper):
            self._logger.debug('Init examples not wrapped, wrapping')
            self.initialization_examples = DatasetWrapper(initialization_examples)
        else:
            self.initialization_examples = initialization_examples
        if is_function:
            self._logger.debug('Function passed in, no model')
            self.function = model
            self.model = None
        else:
            self._logger.debug('Model passed in')
            self.model = model
            if self.predict_proba_flag:
                self.function = self.model.predict_proba
            else:
                errMsg = 'predict_proba not supported by given model, assuming regression model and trying predict'
                self._logger.info(errMsg)
                # try predict instead since this is likely a regression scenario
                self.function = self.model.predict

    def is_valid(self, **kwargs):
        """Determine whether the given model or function can be explained.

        :return: True if the model or function can be explained, False otherwise.
        :rtype: bool
        """
        return self._is_function_valid(self.function, **kwargs)

    @abstractmethod
    def _is_function_valid(self, function, **kwargs):
        """Protected method that returns whether explainer can evaluate model.

        :param function: The function to validate.
        :type function: function
        :return: True if the function can be explained, False otherwise.
        :rtype: bool
        """
        pass


class AggregateBlackBoxExplainer(BlackBoxExplainer, AggregateExplainer):
    """The base class for black box models or functions which aggregate local explanations to global."""

    def __init__(self, model, initialization_examples, is_function=False, **kwargs):
        """Initialize the AggregateBlackBoxExplainer.

        :param model: The model to explain or function if is_function is True.
        :type model: model that implements predict or predict_proba or function that accepts a 2d ndarray
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        :param is_function: Default set to false, set to True if passing function instead of model.
        :type is_function: bool
        """
        super(AggregateBlackBoxExplainer, self).__init__(model, initialization_examples, is_function=is_function,
                                                         **kwargs)
        self._logger.debug('Initializing AggregateBlackBoxExplainer')
        self.explainer = None
        self.current_index_list = [0]
        self.original_data_ref = [None]

    def _function_subset_wrapper(self, original_data_ref, explain_subset, f, current_index_list):
        """Create a wrapper around the prediction function.

        See more details on wrapper.

        :return: The wrapper around the prediction function.
        """
        def wrapper(data):
            """Private wrapper around the prediction function.

            Adds back in the removed columns when using the explain_subset parameter.
            We tile the original evaluation row by the number of samples generated
            and replace the subset of columns the user specified with the result from shap,
            which is the input data passed to the wrapper.

            :return: The prediction function wrapped by a helper method.
            """
            # If list is empty, just return the original data, as this is the background case
            original_data = original_data_ref[0]
            idx = current_index_list[0]
            tiles = int(data.shape[0])
            evaluation_row = original_data[idx]
            if sp.sparse.issparse(evaluation_row):
                if not sp.sparse.isspmatrix_csr(evaluation_row):
                    evaluation_row = evaluation_row.tocsr()
                nnz = evaluation_row.nnz
                rows, cols = evaluation_row.shape
                rows *= tiles
                shape = rows, cols
                if nnz == 0:
                    examples = sp.sparse.csr_matrix(shape, dtype=evaluation_row.dtype).tolil()
                else:
                    new_indptr = np.arange(0, rows * nnz + 1, nnz)
                    new_data = np.tile(evaluation_row.data, rows)
                    new_indices = np.tile(evaluation_row.indices, rows)
                    examples = sp.sparse.csr_matrix((new_data, new_indices, new_indptr),
                                                    shape=shape).tolil()
            else:
                examples = np.tile(original_data[idx], tiles).reshape((data.shape[0], original_data.shape[1]))
            examples[:, explain_subset] = data
            return f(examples)
        return wrapper

    def _prepare_function_and_summary(self, function, original_data_ref,
                                      current_index_list, explain_subset=None, **kwargs):
        if explain_subset:
            # Note: need to take subset before compute summary
            self.initialization_examples.take_subset(explain_subset)
        self.initialization_examples.compute_summary(**kwargs)
        if explain_subset:
            if original_data_ref[0] is None:
                # This is only used for is_valid method; not used during general computation
                original_data_ref[0] = self.initialization_examples.original_dataset
            function = self._function_subset_wrapper(original_data_ref, explain_subset,
                                                     function, current_index_list)
        summary = self.initialization_examples.dataset
        return function, summary
