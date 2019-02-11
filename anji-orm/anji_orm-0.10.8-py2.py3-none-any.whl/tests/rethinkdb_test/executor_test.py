import unittest
from unittest.mock import patch
from typing import Optional

import asynctest
from parameterized import parameterized
import pytest

from anji_orm import Model, orm_register
from anji_orm.rethinkdb.executor import (
    RethinkDBSyncExecutor, RethinkDBAsyncExecutor, _convert_changefeed
)

from ..base import BaseTestCase


class T1(Model):

    t1: Optional[str]  # pylint: disable=invalid-name


@pytest.mark.rethinkdb
class ExecutorToolsTestCase(unittest.TestCase):

    @parameterized.expand([
        (
            {'type': 'change', 'new_val': {1: 1}, 'old_val': {5: 5}},
            {'type': 'change', 'doc': {1: 1}}
        ),
        (
            {'type': 'remove', 'new_val': None, 'old_val': {5: 5}},
            {'type': 'remove', 'doc': {5: 5}}
        ),
        (
            {'type': 'add', 'new_val': {5: 5}, 'old_val': None},
            {'type': 'add', 'doc': {5: 5}}
        ),
    ])
    def test_convert_changefeed(self, rethinkdb_doc, anji_doc):
        self.assertEqual(_convert_changefeed(rethinkdb_doc), anji_doc)


class SyncStrategyDummy:

    def __init__(self, value):
        self.value = value

    def execute_query(self, *_args, **_kwargs):
        return self.value


@pytest.mark.rethinkdb
class SyncExecutorTestCase(BaseTestCase):

    @parameterized.expand([
        (None, None),
        (
            {
                '_python_info': 'tests.rethinkdb_test.executor_test.T1',
                '_schema_version': 'v0.4',
                't1': '5',
                'id': '5'
            },
            dict(t1='5', id='5')
        )
    ])
    def test_executor_get(self, query_result, result_object_kwargs):
        if result_object_kwargs is None:
            result_object = None
        else:
            result_object = T1(**result_object_kwargs)
        executor = RethinkDBSyncExecutor(SyncStrategyDummy(query_result))
        self.assertEqual(
            executor.get_model(T1, '5'),
            result_object
        )


class AsyncStrategyDummy:

    def __init__(self, value):
        self.value = value

    async def execute_query(self, *_args, **_kwargs):
        return self.value


@pytest.mark.rethinkdb
class AsyncExecutorTestCase(asynctest.TestCase):

    async def setUp(self):
        with patch('rethinkdb.connect'):
            orm_register.init('rethinkdb://', {})

    @parameterized.expand([
        (None, None),
        (
            {
                '_python_info': 'tests.rethinkdb_test.executor_test.T1',
                '_schema_version': 'v0.5',
                't1': '5',
                'id': '5'
            },
            dict(t1='5', id='5')
        )
    ])
    async def test_executor_get(self, query_result, result_object_kwargs):
        if result_object_kwargs is None:
            result_object = None
        else:
            result_object = T1(**result_object_kwargs)
        executor = RethinkDBAsyncExecutor(AsyncStrategyDummy(query_result))
        self.assertEqual(
            await executor.get_model(T1, '5'),
            result_object
        )
