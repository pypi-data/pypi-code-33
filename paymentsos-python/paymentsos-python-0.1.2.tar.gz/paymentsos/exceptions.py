class BaseError(Exception):
    pass


class BadRequestError(BaseError):
    pass


class UnauthorizedError(BaseError):
    pass


class NotFoundError(BaseError):
    pass


class MethodNotAllowedError(BaseError):
    pass


class ConflictError(BaseError):
    pass


class ServerError(BaseError):
    pass


class ServiceUnavailableError(BaseError):
    pass
