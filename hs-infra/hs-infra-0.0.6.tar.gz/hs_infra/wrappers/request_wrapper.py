import json
from functools import wraps
from typing import Tuple, Any

import requests


def request_wrapper(f):
    @wraps(f)
    def wrap(*args, **kwargs) -> Tuple[bool, Any, str]:
        error_message = None
        response = None
        is_success = False
        try:
            response = f(*args, **kwargs)
            if response.status_code // 100 is 2:
                is_success = True
                response = json.loads(response.content)
            else:
                response = None
        except requests.exceptions.Timeout:
            error_message = 'request timeout'
        except requests.exceptions.TooManyRedirects:
            error_message = 'too many redirects'
        except requests.exceptions.RequestException:
            error_message = 'catastrophic error'

        return response, is_success, error_message

    return wrap
