import logging
from collections import OrderedDict
from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from t3.util import get_response_type
from t3.util import json_traceback


log = logging.getLogger(__name__)


def enveloped_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        try:
            response.data['status_code'] = response.status_code
        except:  # noqa
            pass

    response = exception_handler(exc, context)
    if not response:
        response = Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        short_code = exc.get_codes()
    except AttributeError:
        short_code = get_response_type(response.status_code)

    try:
        message = exc.detail
    except AttributeError:
        message = 'Server Error'

    response.data = OrderedDict([
        ('status', short_code),
        ('status_code', response.status_code),
        ('message', message),
        ('data', json_traceback()),
    ])

    # Log stuff
    if response.status_code < 500:
        log.info(response.data)
    else:
        log.error(response.data)

    # Remove traceback if debug is off, or we don't have a 500 error
    if not settings.DEBUG or response.status_code < 500:
        del response.data['data']

    return response
