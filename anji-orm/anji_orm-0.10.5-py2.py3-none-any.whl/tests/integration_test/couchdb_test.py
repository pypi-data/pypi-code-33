# pylint: disable=invalid-name
import os

import pytest

from .base import SyncTestSkeleton, AsyncTestSkeleton
from ..base import mark_class


__all__ = ["SyncDBTestCase", "AsyncDBTestCase"]


@mark_class(pytest.mark.couchdb, pytest.mark.sync_test, pytest.mark.integration)
class SyncDBTestCase(SyncTestSkeleton, ):

    @classmethod
    def generate_connection_uri(cls):
        couchdb_host = os.environ.get('COUCHDB_HOST', '127.0.0.1')
        return f'couchdb://{couchdb_host}', {}

    @classmethod
    def extensions(cls):
        return {
            'file': 'couchdb://'
        }


@mark_class(pytest.mark.couchdb, pytest.mark.async_test, pytest.mark.integration)
class AsyncDBTestCase(AsyncTestSkeleton):

    @classmethod
    def generate_connection_uri(cls):
        couchdb_host = os.environ.get('COUCHDB_HOST', '127.0.0.1')
        return f'couchdb://{couchdb_host}', {}

    @classmethod
    def extensions(cls):
        return {
            'file': 'couchdb://'
        }
