class ProKnowError(Exception):
    """All errors involved in interacting with the ProKnow DS - Python SDK modules extend this."""
    pass

class HttpError(ProKnowError):
    """Errors produced at the HTTP layer.

    Attributes:
        status_code (int): The status code.
        body (str): The response body.
    """

    def __init__(self, status_code, body):
        """Initializes the WorkspaceLookupError class.

        Parameters:
            status_code (int): The status code.
            body (str): The response body.
        """
        super(HttpError, self).__init__(status_code, body)
        self.status_code = status_code
        self.body = body

    def __repr__(self):
        return 'HttpError({}, {!r})'.format(self.status_code, self.body)

class WorkspaceLookupError(ProKnowError):
    """Indicates that there was a problem looking up the workspace by the given identifier.

    Attributes:
        message (str): An explanation of the error.
    """

    def __init__(self, message):
        """Initializes the WorkspaceLookupError class.

        Parameters:
            message (str): An explanation of the error.
        """
        super(WorkspaceLookupError, self).__init__(message)
        self.message = message

    def __repr__(self):
        return 'WorkspaceLookupError({!r})'.format(self.message)

class CustomMetricLookupError(ProKnowError):
    """Indicates that there was a problem looking up the custom metric by the given identifier.

    Attributes:
        message (str): An explanation of the error.
    """

    def __init__(self, message):
        """Initializes the CustomMetricLookupError class.

        Parameters:
            message (str): An explanation of the error.
        """
        super(CustomMetricLookupError, self).__init__(message)
        self.message = message

    def __repr__(self):
        return 'CustomMetricLookupError({!r})'.format(self.message)
