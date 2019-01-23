import abc
from functools import wraps
import json
import logging
from urllib.parse import urlencode

from django.conf import settings

from requests.exceptions import HTTPError, RequestException
from w3lib.url import canonicalize_url

from directory_client_core.cache_control import ETagCacheControl


logger = logging.getLogger(__name__)


MESSAGE_CACHE_HIT = 'Fallback cache hit. Using cached content.'
MESSAGE_CACHE_MISS = 'Fallback cache miss. Cannot use any content.'
MESSAGE_NOT_FOUND = 'Resource not found.'


class AbstractResponse(abc.ABC):

    def __init__(self, content, status_code, raw_response=None):
        self.content = content
        self.status_code = status_code
        self.raw_response = raw_response

    def raise_for_status(self):
        if not 200 <= self.status_code < 300:
            raise HTTPError(self.content)

    def json(self):
        return json.loads(self.content.decode('utf-8'))

    @classmethod
    def from_response(cls, response):
        return cls(
            content=response.content,
            status_code=response.status_code,
            raw_response=response,
        )


class LiveResponse(AbstractResponse):
    pass


class CacheResponse(AbstractResponse):
    pass


class FailureResponse(AbstractResponse):
    pass


def fallback(cache):
    """
    Caches content retrieved by the client, thus allowing the cached
    content to be used later if the live content cannot be retrieved.

    """

    def get_cache_response(cache_key):
        content = cache.get(cache_key)
        if content:
            return CacheResponse(content=content, status_code=200)

    def get_cache_control(etag_cache_key):
        etag = cache.get(etag_cache_key)
        if etag:
            return ETagCacheControl(etag)

    def closure(func):
        @wraps(func)
        def wrapper(client, url, params={}, *args, **kwargs):
            cache_key = canonicalize_url(url + '?' + urlencode(params))
            etag_cache_key = 'etag-' + cache_key
            try:
                remote_response = func(
                    client,
                    url=url,
                    params=params,
                    cache_control=get_cache_control(etag_cache_key),
                    *args,
                    **kwargs,
                )
            except RequestException:
                # Failed to create the request e.g., the remote server is down,
                # perhaps a timeout occurred, or even connection closed by
                # remote, etc.
                response = get_cache_response(cache_key)
                if response:
                    logger.error(MESSAGE_CACHE_HIT, extra={'url': url})
                else:
                    raise
            else:
                log_context = {
                    'status_code': remote_response.status_code, 'url': url
                }
                if remote_response.status_code == 404:
                    logger.error(MESSAGE_NOT_FOUND, extra=log_context)
                    return LiveResponse.from_response(remote_response)
                elif remote_response.status_code == 304:
                    response = get_cache_response(cache_key)
                elif not remote_response.ok:
                    # Successfully requested the content, but the response is
                    # not OK (e.g., 500, 403, etc)
                    response = get_cache_response(cache_key)
                    if response:
                        logger.error(MESSAGE_CACHE_HIT, extra=log_context)
                    else:
                        logger.exception(MESSAGE_CACHE_MISS, extra=log_context)
                        response = FailureResponse.from_response(
                            remote_response
                        )
                else:
                    cache.set_many({
                        cache_key: remote_response.content,
                        etag_cache_key: remote_response.headers.get('ETag'),
                    }, settings.DIRECTORY_CLIENT_CORE_CACHE_EXPIRE_SECONDS)
                    response = LiveResponse.from_response(remote_response)
            return response
        return wrapper
    return closure
