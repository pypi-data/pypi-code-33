# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for managing Webservice Schema client side exceptions."""

import abc

from azureml.webservice_schema.schema_exceptions.api_exception import ApiException


class ClientSideException(ApiException):
    """Class to group all client side errors (4xx error codes) to one hierarchy."""

    __metaclass__ = abc.ABCMeta

    @property
    def status_code(self):
        """
        Status code property for this exception.

        :return: Status code associated with this exception
        :rtype: int
        """
        pass

    def __init__(self, message):
        """
        Initialize a ClientSideException object.

        :param message: The message associated with this exception
        :type message: str
        """
        super(ClientSideException, self).__init__(message)


class BadRequestException(ClientSideException):
    """Class for handling of bad request exceptions."""

    @property
    def status_code(self):
        """
        Status code property for this exception.

        :return: Status code associated with this exception
        :rtype: int
        """
        return 400

    def __init__(self, message):
        """
        Initialize a BadRequestException object.

        :param message: The message associated with this exception
        :type message: str
        """
        super(BadRequestException, self).__init__(message)
