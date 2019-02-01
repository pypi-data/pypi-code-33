import time

import pytest
from tinydb import storages

from .context import cachalot


@pytest.fixture(scope='session')
def cache_file(tmpdir_factory):
    return str(tmpdir_factory.mktemp('cache').join('.cache'))


@pytest.fixture(scope='session')
def cache(cache_file):
    return cachalot.Cache(path=cache_file, size=2, storage=storages.MemoryStorage)


@pytest.fixture()
def empty_cache(cache):
    yield cache
    cache.db.purge()


@pytest.fixture()
def full_cache(cache):
    cache.db.insert_multiple([{'key': 'test', 'time': 9999999999, 'value': '1'},
                              {'key': 'test2', 'time': 9999999999, 'value': '2'}])
    yield cache
    cache.db.purge()


@pytest.fixture()
def expired_cache(cache):
    cache.db.insert_multiple([{'key': 'test', 'time': 1, 'value': '1'},
                              {'key': 'test2', 'time': 1, 'value': '2'}])
    yield cache
    cache.db.purge()


class TestCache:

    def test_expiry(self, empty_cache):
        # GIVEN an empty cache
        cache = empty_cache

        # WHEN checking expiration time
        # THEN it show be roughly current time + defined expiry
        now = time.time()
        expiry = cache.expiry()
        assert int(expiry) == int(now + cache.timeout)


    def test_clear(self, full_cache):
        # GIVEN a cache with items
        cache = full_cache
        assert len(cache.db) == 2

        # WHEN clearing a cache
        cache.clear()

        # THEN there should be no items left
        assert len(cache.db) == 0

    def test_get(self, expired_cache):
        # GIVEN a cache with expired a non-expired items
        cache = expired_cache
        cache.timeout = 86400
        cache.db.insert({'key': 'test3', 'time': 9999999999, 'value': '3'})

        # WHEN getting the results
        # THEN only the non-expired items should return a result
        assert cache.get('test') == None
        assert cache.get('test2') == None
        assert cache.get('test3') == 3

    def test_insert(self, empty_cache):
        # GIVEN an empty cache
        cache = empty_cache

        # WHEN inserting an item
        cache.insert('test', 1)

        # THEN the cache should contain only this item
        assert len(cache.db) == 1
        assert int(cache.db.all()[0]['value']) == 1

    def test_insert_overflow(self, empty_cache):
        # GIVEN an empty cache
        cache = empty_cache

        # WHEN inserting more items than the cache size
        cache.insert('test', 1)
        cache.insert('test2', 2)
        cache.insert('test3', 3)

        # THEN the oldest item should be removed
        assert len(cache.db) == 2
        assert int(cache.db.all()[0]['value']) == 2

    def test_remove(self, full_cache):
        # GIVEN a cache with items
        cache = full_cache

        # WHEN removing an item
        cache.remove('test')

        # THEN the cache should only the remaining items
        assert len(cache.db) == 1
        assert int(cache.db.all()[0]['value']) == 2

    def test_remove_oldest(self, full_cache):
        # GIVEN a cache with items
        cache = full_cache

        # WHEN removing the oldest items
        cache._remove_oldest()

        # THEN the first items inserted should be removed
        assert len(cache.db) == 1
        assert int(cache.db.all()[0]['value']) == 2

    def test_remove_no_timeout(self, expired_cache):
        # GIVEN a cache with expired items
        cache = expired_cache
        cache.timeout = 0

        # WHEN removing with timeout set to infinite
        cache._remove_expired()

        # THEN they should not be deleted
        assert len(cache.db) == 2
        assert int(cache.db.all()[0]['value']) == 1
        assert int(cache.db.all()[1]['value']) == 2

    def test_remove_expired(self, expired_cache):
        # GIVEN a cache with expired items
        cache = expired_cache
        cache.timeout = 86400

        # WHEN removing expired items
        cache._remove_expired()

        # THEN there should be none left
        assert len(cache.db) == 0

    def test_retry(self, cache_file):
        # GIVEN a cached function and cache with retry on

        @cachalot.Cache(path=cache_file, size=1, storage=storages.MemoryStorage, retry=True)
        def mocks():
            return 1

        # WHEN an empty result is cached
        mocks()
        cache = cachalot.Cache(path=cache_file, size=2,
                               storage=storages.MemoryStorage, retry=True)
        cache.db.update({'value': '0'})

        # THEN running the cached function should be retried
        assert mocks() == 1

    def test_no_retry(self, cache_file):
        # GIVEN a cached function and cache with retry off

        @cachalot.Cache(path=cache_file, size=1, storage=storages.MemoryStorage)
        def mocks():
            return 1

        # WHEN an empty result is cached
        mocks()
        cache = cachalot.Cache(path=cache_file, size=2,
                               storage=storages.MemoryStorage, retry=True)
        cache.db.update({'value': '0'})

        # THEN running the cached function should return the empty result
        assert mocks() == 0
