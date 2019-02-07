class Error(Exception):

    def __init__(self, code, error):
        super(Error, self).__init__()
        self.code = code
        self.message = error


class BadRequestError(Error):
    pass


class AuthenticationError(Error):
    pass


class ForbiddenError(Error):
    pass


class InternalError(Error):
    pass


class NotFoundError(Error):
    pass


class TooManyRequestsError(Error):
    pass


class ServiceUnavailable(Error):
    pass


class MethodNotAllowed(Error):
    pass


class RequestTimeout(Error):
    pass


class PreconditionFailed(Error):
    pass


class ValidationError(Error):
    def __init__(self, message):
        super().__init__(code=412, error=message)
