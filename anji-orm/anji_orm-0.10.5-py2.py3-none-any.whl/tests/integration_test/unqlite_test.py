# pylint: disable=invalid-name
import tempfile

import pytest

from .base import AsyncTestSkeleton, SyncTestSkeleton
from ..base import mark_class

__all__ = ["SyncDBTestCase", "AsyncDBTestCase"]


class UnqliteTestTempalte:

    @classmethod
    def generate_connection_uri(cls):
        return f'unqlite://', {}

    @classmethod
    def extensions(cls):
        return {
            'file': f'disk://{tempfile.mkdtemp()}'
        }


@mark_class(pytest.mark.unqlite, pytest.mark.sync_test, pytest.mark.integration)
class SyncDBTestCase(UnqliteTestTempalte, SyncTestSkeleton):

    def test_changes(self):
        pass

    def test_complex_changes(self):
        pass


@mark_class(pytest.mark.unqlite, pytest.mark.async_test, pytest.mark.integration)
class AsyncDBTestCase(UnqliteTestTempalte, AsyncTestSkeleton):

    use_default_loop = True

    def test_changes(self):
        pass

    def test_complex_changes(self):
        pass
