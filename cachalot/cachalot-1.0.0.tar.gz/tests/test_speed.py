import time
from urllib import request

import pytest

from .context import cachalot


def plain_request():
    response = request.urlopen('http://httpbin.org/get')
    return response.read().decode('utf-8')


@cachalot.Cache()
def cached_request():
    return plain_request()


@pytest.fixture(scope='session')
def cached():
    start = time.time()
    3 * cached_request()
    end = time.time()
    yield end - start


@pytest.fixture(scope='session')
def uncached():
    start = time.time()
    3 * plain_request()
    end = time.time()
    yield end - start


@pytest.mark.xfail(reason='It seems Gitlab CI is caching all requests')
def test_speed(cached, uncached):
    # GIVEN a cached and uncached request
    # WHEN repeating the same request
    # THEN the cached request should be faster
    assert cached < uncached
