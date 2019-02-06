# pylint: disable=invalid-name
import os
import tempfile
import sys

import unittest
import pytest

from .base import AsyncTestSkeleton, SyncTestSkeleton
from ..base import mark_class

__all__ = ["SyncDBTestCase", "AsyncDBTestCase"]


class RethinkDBTestTempalte:

    @classmethod
    def generate_connection_uri(cls):
        if sys.version[0:3] == '3.7':
            raise unittest.SkipTest("RethinkDB driver does not support python 3.7")
        rethinkdb_host = os.environ.get('RETHINKDB_HOST', '127.0.0.1')
        return f'rethinkdb://{rethinkdb_host}', {"pool_size": 10}

    @classmethod
    def extensions(cls):
        return {
            'file': f'disk://{tempfile.mkdtemp()}'
        }


@mark_class(pytest.mark.rethinkdb, pytest.mark.sync_test, pytest.mark.integration)
class SyncDBTestCase(RethinkDBTestTempalte, SyncTestSkeleton):

    pass


@mark_class(pytest.mark.rethinkdb, pytest.mark.async_test, pytest.mark.integration)
class AsyncDBTestCase(RethinkDBTestTempalte, AsyncTestSkeleton):

    use_default_loop = True
