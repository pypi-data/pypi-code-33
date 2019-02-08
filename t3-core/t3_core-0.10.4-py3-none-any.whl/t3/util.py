import sys
import traceback
from collections import OrderedDict


def json_traceback():
    """Gathers exception details, such as trace info."""
    exc_info = sys.exc_info()
    traceback_list = ''.join(traceback.format_exc()).split('\n')

    return OrderedDict([
        ('exception_class', str(exc_info[0])),
        ('exception_message', str(exc_info[1])),
        ('exception_traceback', traceback_list),
    ])


def get_response_type(code):
    if 100 <= code <= 199:
        return 'informational'
    if 200 <= code <= 299:
        return 'success'
    if 300 <= code <= 399:
        return 'redirect'
    if 400 <= code <= 499:
        return 'client_error'
    if 500 <= code <= 599:
        return 'server_error'
    return None
