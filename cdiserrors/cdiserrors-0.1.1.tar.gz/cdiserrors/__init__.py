from cdislogging import get_logger
from flask import jsonify
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException


class APIError(Exception):
    def __init__(self, message=None, code=None, json=None):
        super(APIError, self).__init__()
        self.message = message
        self.code = code
        self.json = json

    def __str__(self):
        error_msg = ''
        if self.code:
            error_msg = '[{}]'.format(self.code)
        if self.message:
            error_msg = '{} - {}'.format(error_msg, self.message)
        return error_msg

class APINotImplemented(APIError):
    def __init__(self, message, code=501, json=None):
        super(APINotImplemented, self).__init__(message, code, json)

class NotFoundError(APIError):
    def __init__(self, message):
        self.message = message
        self.code = 404

class UserError(APIError):
    def __init__(self, message, code=400, json=None):
        if json is None:
            json = {}
        super(UserError, self).__init__(message, code, json)

class BaseUnsupportedError(UserError):
    def __init__(self, file_format, code=400, json=None):
        if json is None:
            json = {}
        message = (
            "Format {} is not supported; supported formats are: {}."
            .format(file_format, ",".join(self.supported_formats))
        )
        super(BaseUnsupportedError, self).__init__(message, code, json)


class AuthError(APIError):
    """
    Authorization Error. This is for any case that user
    has valid authentication but is unauthorized to access
    particular resources

    This is deprecated, should use AuthZError explicitly
    """
    def __init__(self, message=None, code=403, json=None):
        if json is None:
            json = {}
        auth_message = "You don't have access to this resource"
        if message is not None:
            auth_message += ': {}'.format(message)
        super(AuthError, self).__init__(auth_message, code, json)


class AuthZError(AuthError):
    """
    Authorization Error. This is for any case that user
    has valid authentication but is unauthorized to access
    particular resources
    """
    pass

class AuthNError(APIError):
    """
    Authentication Error. This is for any case that user
    is not authenticated or authenticated incorrectly
    """
    def __init__(self, message=None, code=401, json=None):
        if message is not None:
            message = "Authentication Error: {}".format(message)
        super(AuthNError, self).__init__(message, code, json)


class InvalidTokenError(AuthError):
    def __init__(self):
        self.message = (
            "Your token is invalid or expired. Please get a new token from GDC"
            " Data Portal."
        )
        self.code = 403


class InternalError(APIError):
    def __init__(self, message=None, code=500):
        self.message = "Internal server error"
        if message:
            self.message += ': {}'.format(message)
        self.code = code


class ServiceUnavailableError(APIError):
    def __init__(self, message, code=503):
        self.message = message
        self.code = code


class ParsingError(Exception):
    pass


class SchemaError(Exception):
    def __init__(self, message, e=None):
        if e:
            log = get_logger(__name__)
            log.exception(e)
        message = "{}: {}".format(message, e) if e else message
        super(SchemaError, self).__init__(message)

class UnhealthyCheck(APIError):
    def __init__(self, message):
        self.message = str(message)
        self.code = 500

def make_json_error(ex):
    response = jsonify(message=str(ex))
    response.status_code = (
        ex.code if isinstance(ex, HTTPException) else 500)
    return response

def setup_default_handlers(app):
    for code in default_exceptions.iterkeys():
        app.register_error_handler(code, make_json_error)
