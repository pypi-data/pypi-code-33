import json


__all__ = ('Error', 'RequestError', 'BadRequest', 'Unauthorized',
           'Forbidden', 'NotFound', 'MethodNotAllowed', 'TooManyRequests',
           'GatewayUnavailable')


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


class BadRequest(RequestError):

    """
    Rquest was improperly formatted, or the server couldn't understand it.
    """

    __slots__ = ()


class Unauthorized(RequestError):

    """
    The Authorization header was missing or invalid.
    """

    __slots__ = ()


class Forbidden(RequestError):

    """
    The Authorization token you passed did not have permission to the resource.
    """

    __slots__ = ()


class NotFound(RequestError):

    """
    The resource at the location specified doesn't exist.
    """

    __slots__ = ()


class MethodNotAllowed(RequestError):

    """
    The HTTP method used is not valid for the location specified.
    """

    __slots__ = ()


class TooManyRequests(RequestError):

    """
    You've made too many requests.
    """

    __slots__ = ()


class GatewayUnavailable(RequestError):

    """
    There was not a gateway available to process your request.
    """

    __slots__ = ()


class InterruptedRequestError(Error):

    """
    Session was closed during the handling of a request.
    """

    __slots__ = ()
