# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for managing the top level abstract ApiException for Webservice Schema handling."""

import abc


class ApiException(Exception):
    """Abstract parent class for exceptions related to webservice schema."""

    __metaclass__ = abc.ABCMeta

    @property
    @abc.abstractmethod
    def status_code(self):
        """Status code property."""
        pass

    @property
    def message(self):
        """
        Message property.

        :return: The message corresponding to this exception
        :rtype: str
        """
        return self._message

    def __init__(self, message):
        """
        Initialize this ApiException object.

        :param message: The message corresponding to this exception
        :type message: str
        """
        Exception.__init__(self)
        self._message = message

    def to_dict(self):
        """
        Return a dictionary representation of this exception.

        :return: A dictionary representation of this exception
        :rtype: dict
        """
        return {"errorCode": self.status_code, "message": self.message}
