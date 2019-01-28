# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Exceptions thrown by AutoML."""


class DataException(Exception):
    """
    Exception related to data validations.

    :param message: Details on the exception.
    """

    def __init__(self, message=""):
        """
        Construct a new DataException.

        :param message: details on the exception.
        """
        super().__init__(message)


class ServiceException(Exception):
    """
    Exception related to JOS.

    :param message: Details on the exception.
    """

    def __init__(self, message=""):
        """
        Construct a new ServiceException.

        :param message: details on the exception.
        """
        super().__init__(message)
