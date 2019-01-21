import logging
from traceback import format_exc

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ErrorDetail
from rest_framework.views import exception_handler
from rest_framework.response import Response

log = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    exc - exception object, example: <class 'django.core.exceptions.PermissionDenied'>
    context - not use

    Example:
    http://localhost:8000/agent/salesplan/
    intercept <class 'django.core.exceptions.PermissionDenied'>

    http://localhost:8000/agent
    404 not interception
    но http://localhost:8000/agent/salesplan/2000/
    404 intercepted

    message:
        response.data: it's object different type, can contain detailed information about error
        OR
        exc.default_detail: it's str with short description error

    Need add your settings:

    import universal_response_mobile_api as u_mobile_api

    REST_FRAMEWORK = {
        ...
        'EXCEPTION_HANDLER': 'u_mobile_api.custom_exception_handler',
        ...
    }
    """
    response = exception_handler(exc, context)
    msg = _('Ошибка в запросе')
    status_code = 500

    try:
        if not hasattr(response, 'status_code'):
            # python exception:
            if isinstance(exc, ValidationError):
                msg = '\n '.join([str(i) for i in exc.messages])
            else:
                msg = str(exc)
            status_code = 500

        elif not hasattr(exc, 'detail'):
            msg = str(exc)
            status_code = response.status_code

        elif isinstance(exc.detail, ErrorDetail):  # auth
            msg = exc.detail
            status_code = response.status_code

        elif isinstance(exc.detail, list):
            msg = '\n '.join([_(value[0]) for value in exc.detail])
            status_code = response.status_code

        else:
            msg = '\n '.join(['{0} - {1}'.format(key, _(value[0])) for key,value in exc.detail.items()])
            status_code = response.status_code
    except:
        log.error(format_exc())

    log.error(exc)

    structured_exc = {
        'success': False,
        'error': status_code,
        'message': msg,
        'response': None
    }
    return Response(structured_exc, status=status_code)
