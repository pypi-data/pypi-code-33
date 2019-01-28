# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for managing Webservice Schema server side exceptions."""

import abc

from azureml.webservice_schema.schema_exceptions.api_exception import ApiException


class ServerSideException(ApiException):
    """Class to group all server side errors (5xx error codes) to one hierarchy."""

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
        Initialize a ServerSideException object.

        :param message: The message associated with this exception
        :type message: str
        """
        super(ServerSideException, self).__init__(message)


class InternalServerException(ServerSideException):
    """Class for handling of internal server exceptions."""

    @property
    def status_code(self):
        """
        Status code property for this exception.

        :return: Status code associated with this exception
        :rtype: int
        """
        return 500

    def __init__(self, message):
        """
        Initialize a InternalServerException object.

        :param message: The message associated with this exception
        :type message: str
        """
        super(InternalServerException, self).__init__(message)
