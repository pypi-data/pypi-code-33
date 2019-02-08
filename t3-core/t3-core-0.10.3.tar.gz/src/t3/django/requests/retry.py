import requests
from django.conf import settings
import logging

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

log = logging.getLogger(__name__)


def log_retry_obj(message, retries, factor, status_codes):
    log.info({
        'message': message,
        'retries': retries,
        'factor': factor,
        'statuses': ', '.join(status_codes),
    })


def get_retry_requests():
    # Check settings
    if not settings.EXTERNAL_RETRY:
        return None
    external_retry = settings.EXTERNAL_RETRY
    number = external_retry.get('number')
    factor = external_retry.get('factor')
    statuses = external_retry.get('status_codes')
    if (number or factor or statuses) is None:
        log_mess = 'Unable to use retry requests -> missing information'
        log_retry_obj(log_mess, number, factor, statuses.split(','))
        return None
    # Mount adapter
    session = requests.session()
    retry = Retry(
        total=int(number),
        read=int(number),
        connect=int(number),
        backoff_factor=float(factor),
        status_forcelist=tuple([int(s.strip()) for s in statuses.split(',')]),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    log_mess = 'Using retry requests'
    log_retry_obj(log_mess, number, factor, statuses.split(','))
    return session


# HTTP Get Request
def get(url, **kwargs):
    req = get_retry_requests()
    if req is not None:
        return req.get(url, **kwargs)
    return requests.get(url, **kwargs)


# HTTP Options Request
def options(url, **kwargs):
    req = get_retry_requests()
    if req is not None:
        return req.options(url, **kwargs)
    return requests.options(url, **kwargs)


# HTTP Head Request
def head(url, **kwargs):
    req = get_retry_requests()
    if req is not None:
        return req.head(url, **kwargs)
    return requests.head(url, **kwargs)


# HTTP Post Request
def post(url, **kwargs):
    req = get_retry_requests()
    if req is not None:
        return req.post(url, **kwargs)
    return requests.post(url, **kwargs)


# HTTP Put Request
def put(url, **kwargs):
    req = get_retry_requests()
    if req is not None:
        return req.put(url, **kwargs)
    return requests.put(url, **kwargs)


# HTTP Patch Request
def patch(url, **kwargs):
    req = get_retry_requests()
    if req is not None:
        return req.patch(url, **kwargs)
    return requests.patch(url, **kwargs)


# HTTP Delete Request
def delete(url, **kwargs):
    req = get_retry_requests()
    if req is not None:
        return req.delete(url, **kwargs)
    return requests.delete(url, **kwargs)
