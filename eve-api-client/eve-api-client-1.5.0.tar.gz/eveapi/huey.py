import datetime
import json
import logging

import math
import redis
import requests
from django.conf import settings
from django.utils import timezone
from huey.contrib.djhuey import task

from eveapi.esi.errors import ESIErrorLimitReached, ESIPageCacheRefresh
from huey.exceptions import TaskException, RetryTask

TIMEOUT = 10000

logger = logging.getLogger(__name__)
redis = redis.StrictRedis(connection_pool=settings.REDIS_POOL)


def log_data_age(r):
    """
    Logs data age and expiry time in seconds.
    Age is time since last modified, expiry is the time until the esi refreshes the cache.
    """
    if 'Last-Modified' in r.headers:
        time = datetime.datetime.now() - datetime.datetime.strptime(r.headers['Last-Modified'],
                                                                    '%a, %d %b %Y %H:%M:%S %Z')
        time = round(time.total_seconds())
        logging.info('ESI data is {} seconds old'.format(time))

    if 'Expires' in r.headers:
        time = datetime.datetime.strptime(r.headers['Expires'], '%a, %d %b %Y %H:%M:%S %Z') - datetime.datetime.now()
        time = round(time.total_seconds())
        logging.info('New ESI data in {} seconds'.format(time))


def get_cache_url(url, params):
    """
    Appends the parameters to the url.
    This is used to cache urls with specific parameters.
    Parameters are sorted by key names since parameters are unordered.

    This may not generate valid urls, this should only be used for redis keys.
    """
    params = map(lambda param: str(param[0]) + '=' + str(param[1]), params.items())  # join param key/value pairs
    params = '&'.join(sorted(params))  # sort since dicts can be in any order, sort by key
    return url + '?' + params


def error_limit_retry(delay=settings.ESI_RETRY, *args, **kwargs):
    """
    Schedule another esi task after the esi error limit reset ends then return the result.
    """
    return esi.schedule(
        args=args,
        kwargs=kwargs,
        delay=delay,
    ).get(timeout=600, blocking=True)


def cache_response(endpoint, expires, data):
    if expires:
        cached_until = timezone.make_aware(datetime.datetime.strptime(expires, '%a, %d %b %Y %H:%M:%S %Z'))
        time_delta = cached_until - timezone.now()
        seconds = int(time_delta.total_seconds())
    else:
        seconds = 300  # default to 5 minutes

    if seconds > 0:
        data = json.dumps(data)
        redis.setex(endpoint, seconds, data)

        return True


@task(retries=5, retry_delay=10)
def esi_task(*args, **kwargs):
    """
    Huey task method.
    Passes all args to the esi method.

    The esi method is rarely run by itself.
    The only reason it is needed is for calling esi endpoints with as little delay as possible.
    """
    return esi(*args, **kwargs)


def esi(*args, **kwargs):
    """
    ESI call method.
    This calls the esi, aggregates pages, and caches results.
    On errors this will run another

    The esi method is rarely run by itself.
    The only reason it is needed is for calling esi endpoints with as little delay as possible.
    """
    method, url, headers, params, data, fetch_pages, auth_callback, cache, raise_error = args
    page = kwargs.get('page', False)
    parent_expires = kwargs.get('parent_expires', None)

    # set page number
    if page:
        params['page'] = page  # unspecified gives the first page in esi

    cache_url = get_cache_url(url, params)

    # log route info
    logger.info('({}) {}'.format(method, cache_url))

    # check for cached request
    cached = redis.get(cache_url)
    if method == 'GET' and cached:  # return cached get response
        logger.info('Cached ESI call')
        return json.loads(cached.decode('utf-8'))

    # check for esi_api_client.delay to esi rate limit
    delay = redis.ttl('esi_api_client.delay')
    if delay and delay > 0:
        logger.warning('error limit hit, retrying soon')
        return error_limit_retry(*args, delay=delay, **kwargs)

    # set auth header using auth_callback function
    if auth_callback:
        headers['Authorization'] = auth_callback()

    # make request
    r = requests.request(method, url, params=params, headers=headers, data=data, timeout=TIMEOUT)

    # check ESI error rate limiting
    if 'X-Esi-Error-Limit-Remain' in r.headers and int(r.headers['X-Esi-Error-Limit-Remain']) <= 20:
        redis.setex('esi_api_client.delay', r.headers['X-Esi-Error-Limit-Reset'], r.headers['X-Esi-Error-Limit-Reset'])

    if 200 <= r.status_code < 300:  # is 2xx
        log_data_age(r)

        if 'application/json' not in r.headers.get('Content-Type', ''):
            return True

        if parent_expires and r.headers['Expires'] != parent_expires:
            # return (not raise) an exception, since we want the parent call (page 1) to retry
            return ESIPageCacheRefresh()

        response_data = r.json()

        # load multiple pages if able to
        total_pages = int(r.headers.get('x-pages', 1))
        if fetch_pages and total_pages > 1:
            logging.info('got {} pages, fetching all'.format(total_pages))
            pages = [
                esi_task(  # needs to match this function's signature
                    method,
                    url,
                    headers,
                    params,
                    data,
                    False,
                    auth_callback,
                    cache,
                    raise_error,
                    page=p + 2,
                    parent_expires=r.headers['Expires']
                )
                for p in range(total_pages - 1)  # +2 since pages are 1-based indexed
            ]
            for page_request in pages:
                page_data = page_request.get(blocking=True)  # block to get result

                if isinstance(page_data, ESIPageCacheRefresh):
                    logger.warning(page_data)
                    for p in pages:
                        p.revoke()

                    # retry this task
                    raise RetryTask()

                response_data.extend(page_data)  # assume both are lists

        # cache response if get request
        if method == 'GET' and cache:  # assume fetch_pages and save the full data list for page=false
            cache_response(get_cache_url(url, params), r.headers.get('Expires', None), response_data)

        return response_data

    else:
        logger.error('ESI request {} error: {} - {}, {}'.format(
            r.url,
            r.status_code,
            r.content,
            r.headers.get('X-ESI-Error-Limit-Remain', '')
        ))

        # remake request if token was expired
        if r.json()['error'] == 'expired':
            raise RetryTask()

        # log error for esi rate limiting
        if int(r.headers.get('X-ESI-Error-Limit-Remain', '100')) == 0:
            logger.error('ESI error limit hit 0')
            return error_limit_retry(*args, delay=delay, **kwargs)

        if raise_error == r.status_code:
            return r
        elif raise_error is True:
            return r

        raise RetryTask()
