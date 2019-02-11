# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines a decorator for tabular data which wraps pandas dataframes, scipy and numpy arrays in a DatasetWrapper."""

from .dataset_wrapper import DatasetWrapper


def tabular_decorator(explain_func):
    """Decorate an explanation function to wrap evaluation examples in a DatasetWrapper.

    :param explain_func: An explanation function where the first argument is a dataset.
    :type explain_func: explanation function
    """
    def explain_func_wrapper(self, evaluation_examples, **kwargs):
        if not isinstance(evaluation_examples, DatasetWrapper):
            self._logger.debug('Eval examples not wrapped, wrapping')
            evaluation_examples = DatasetWrapper(evaluation_examples)
        return explain_func(self, evaluation_examples, **kwargs)
    return explain_func_wrapper
