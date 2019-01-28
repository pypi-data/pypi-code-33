# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines an explainer."""

from abc import ABCMeta
from azureml._logging import ChainedIdentity


class Explainer(ChainedIdentity):
    """The base class for explainers."""

    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        """Initialize the explainer."""
        super(Explainer, self).__init__(**kwargs)
        self._logger.debug('Initializing Explainer')

    def __str__(self):
        """Get string representation of the explainer.

        :return: A string containing explainer name.
        :rtype: str
        """
        return "{}".format(self.__class__.__name__)
