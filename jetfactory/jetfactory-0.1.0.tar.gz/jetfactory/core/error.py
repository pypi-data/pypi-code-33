# -*- coding: utf-8 -*-

from logging import getLogger
from sanic.helpers import STATUS_CODES
from sanic.handlers import ErrorHandler
from sanic.exceptions import SanicException
from jetfactory.exceptions import JetfactoryException
from marshmallow.exceptions import ValidationError
from jetfactory.utils import jsonify

log = getLogger('root')


class JetErrorHandler(ErrorHandler):
    def __init__(self):
        super(JetErrorHandler, self).__init__()

    def default(self, request, exception):
        if isinstance(exception, ValidationError):
            handler = validation
        elif isinstance(exception, JetfactoryException):
            handler = jetfactory
        elif isinstance(exception, SanicException):
            handler = http_usage
        else:
            handler = fallback

        return handler(request, exception)


def validation(_, exception):
    return jsonify({'error': exception.messages}, status=422)


def http_usage(_, exception):
    if hasattr(exception, 'args'):
        message = '\n'.join(exception.args)
    else:
        message = str(exception)

    # @TODO - Remove this block if https://github.com/huge-success/sanic/issues/1455 gets fixed.
    if 'HttpParserInvalidMethodError' in message:
        message = 'Invalid HTTP method'
    elif 'Traceback' in message:
        message = STATUS_CODES.get(exception.status_code)

    return jsonify({'error': message}, status=exception.status_code)


def fallback(_, exception):
    if hasattr(exception, 'status_code'):
        status = exception.status_code
    else:
        status = 500

    log.exception(exception)
    message = STATUS_CODES.get(status)
    return jsonify({'error': message}, status=status)


def jetfactory(_, exception):
    return jsonify({'error': str(exception)}, status=exception.status_code)
