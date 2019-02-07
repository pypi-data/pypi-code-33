import datetime
import json
import logging

import requests
from dateutil import parser

HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_401_UNAUTHORIZED = 401
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_429_TOO_MANY_REQUESTS = 429

logger = logging.getLogger(__name__)


_session = None


def _handle_status_code_error(response):
    logger.info('response: %s' % response.text)
    try:
        errors = response.json()['errors']
    except:
        raise SerenyticsException('Error while calling Serenytics API. Please retry or contact support.')
    else:
        raise SerenyticsException(errors[0])


def make_request(method, url,
                 custom_exceptions=None,
                 expected_status_code=HTTP_200_OK,
                 expected_json_status=None,
                 log_request=True,
                 **kwargs):

    # reuse https session
    global _session
    if _session is None:
        _session = requests.session()

    response = _session.request(method, url, allow_redirects=False, **kwargs)
    if log_request:
        logger.info('{method} {url} {code}'.format(method=method.upper(),
                                                   url=url,
                                                   code=response.status_code))

    if custom_exceptions is not None and response.status_code in custom_exceptions:
        raise custom_exceptions[response.status_code]

    if response.status_code == HTTP_401_UNAUTHORIZED:
        raise SerenyticsException('Unauthorized: please check your API key and retry')

    if response.status_code != expected_status_code:
        _handle_status_code_error(response)

    if expected_json_status is not None:
        response_content = response.json()
        status = response_content['status']
        if status != expected_json_status:
            raise SerenyticsException(response_content.get('errors', ['Error: Please retry or contact support.'])[0])

    return response


class SerenyticsException(Exception):
    """Exception launched by Serenytics Client when an error occured."""


class StorageJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return {
                '__type__': 'datetime',
                'value': obj.isoformat()
            }
        return super(StorageJsonEncoder, self).default(obj)


class StorageJsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super(StorageJsonDecoder, self).__init__(object_hook=self._object_hook, *args, **kwargs)

    @staticmethod
    def _object_hook(obj):
        _type = obj.get('__type__')
        if _type == 'datetime':
            return parser.parse(obj['value'])
        return obj
