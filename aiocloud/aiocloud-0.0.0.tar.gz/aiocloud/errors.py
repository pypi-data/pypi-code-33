import json


__all__ = ('Error', 'RequestError')


class Error(Exception):

    """
    Raised when something flops.
    """

    __slots__ = ()


class RequestError(Error):

    """
    Raised when a request fails.
    """

    __slots__ = ('response', 'data')

    def __init__(self, response, data):

        message = json.dumps(data, indent = 4)

        super().__init__(message)

        self.response = response

        self.data = data
