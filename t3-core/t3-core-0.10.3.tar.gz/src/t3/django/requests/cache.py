import requests
import redis

from cachecontrol import CacheControlAdapter
from cachecontrol.heuristics import ExpiresAfter
from cachecontrol.caches.redis_cache import RedisCache

from django.conf import settings
import logging
import re

log = logging.getLogger(__name__)


def log_cache_obj(message, redis_url, pattern, minutes, url):
    password_sub = re.sub('(password=)[^&\n\r]+', 'password=xxxxxxxxxx', redis_url)
    log.info({
        'message': message,
        'redis': password_sub,
        'pattern': pattern,
        'minutes': minutes,
        'url': url,
    })


def get_cache_requests(url):
    # Check settings
    if not hasattr(settings, 'EXTERNAL_CACHE'):
        return None
    external_cache = settings.EXTERNAL_CACHE
    redis_url = external_cache.get('redis')
    pattern = external_cache.get('pattern')
    minutes = external_cache.get('minutes')
    if (redis_url or pattern or minutes) is None:
        log_mess = 'Unable to use cache requests -> missing information'
        log_cache_obj(log_mess, redis_url, pattern, minutes, url)
        return None
    # Check if redis is connected
    r = redis.from_url(redis_url)
    try:
        r.info()
    except redis.ConnectionError:
        log_mess = 'Unable to use cache requests -> no redis connection'
        log_cache_obj(log_mess, redis_url, pattern, minutes, url)
        return None  # No cache connection, cannot use cache
    session = requests.session()
    # Check if url path matches (RegEx: https://regexr.com/)
    match = re.search(r'%s' % pattern, url)
    if match is None:
        log_mess = 'Unable to use cache requests -> url does not match'
        log_cache_obj(log_mess, redis_url, pattern, minutes, url)
        return None
    # Everything is connected and matches, can use cached request
    adapter = CacheControlAdapter(heuristic=ExpiresAfter(minutes=int(minutes)), cache=RedisCache(r))
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    log_mess = 'Using cache requests'
    log_cache_obj(log_mess, redis_url, pattern, minutes, url)
    return session


# HTTP Get Request
def get(url, **kwargs):
    req = get_cache_requests(url)  # Use cache if available
    if req is not None:
        return req.get(url, **kwargs)
    return requests.get(url, **kwargs)


# HTTP Options Request
def options(url, **kwargs):
    return requests.options(url, **kwargs)


# HTTP Head Request
def head(url, **kwargs):
    return requests.head(url, **kwargs)


# HTTP Post Request
def post(url, **kwargs):
    return requests.post(url, **kwargs)


# HTTP Put Request
def put(url, **kwargs):
    return requests.put(url, **kwargs)


# HTTP Patch Request
def patch(url, **kwargs):
    return requests.patch(url, **kwargs)


# HTTP Delete Request
def delete(url, **kwargs):
    return requests.delete(url, **kwargs)
