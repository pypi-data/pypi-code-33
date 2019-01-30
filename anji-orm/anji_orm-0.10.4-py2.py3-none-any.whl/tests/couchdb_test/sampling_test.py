# pylint: disable=invalid-name
from typing import Optional
from parameterized import parameterized

import pytest

from anji_orm import Model, Field, QueryAst, IndexPolicy
from anji_orm.couchdb.lib import CouchDBMangoQuery

from .base import CouchDBTestCase


class T1(Model):

    _table = 'non_table'
    _index_policy: IndexPolicy = IndexPolicy.greedyless

    c1: Optional[str] = Field(secondary_index=True)
    c2: Optional[str] = Field(secondary_index=True)
    c3: Optional[str]
    c4: Optional[str] = Field(secondary_index=True)
    c5: Optional[bool]


@pytest.mark.couchdb
class SamplingTest(CouchDBTestCase):

    def test_limit_sampling(self):
        mango_query = CouchDBMangoQuery({'c1': {'$eq': 5}})
        mango_query.limit = 2
        build_result = (T1.c1 == 5).limit(2).build_query()
        mango_query.table_name = T1._table
        mango_query.query_identity = build_result.query_identity
        self.assertEqual(build_result, mango_query)

    def test_skip_sampling(self):
        mango_query = CouchDBMangoQuery({'c1': {'$eq': 5}})
        mango_query.skip = 2
        build_result = (T1.c1 == 5).skip(2).build_query()
        mango_query.table_name = T1._table
        mango_query.query_identity = build_result.query_identity
        self.assertEqual(build_result, mango_query)

    def test_sample_sampling(self):
        mango_query = CouchDBMangoQuery({'c1': {'$eq': 5}})
        mango_query.limit = 10
        mango_query.post_processors = [None]
        build_result = (T1.c1 == 5).sample(2).build_query()
        mango_query.table_name = T1._table
        mango_query.query_identity = build_result.query_identity
        self.assertEqual(build_result, mango_query)

    def test_complex_sampling(self):
        mango_query = CouchDBMangoQuery({'c1': {'$eq': 5}})
        mango_query.limit = 10
        mango_query.skip = 3
        mango_query.post_processors = [None]
        build_result = (T1.c1 == 5).limit(10).skip(3).sample(2).build_query()
        mango_query.table_name = T1._table
        mango_query.query_identity = build_result.query_identity
        self.assertEqual(build_result, mango_query)


@pytest.mark.couchdb
class OrderByTestCase(CouchDBTestCase):

    @parameterized.expand([
        (
            CouchDBMangoQuery({'c1': {'$eq': 5}}),
            ['c2'],
            (T1.c1 == 5).order_by(T1.c2.amount)
        ),
        (
            CouchDBMangoQuery({'c1': {'$eq': 5}}),
            ['c3'],
            (T1.c1 == 5).order_by(T1.c3.amount)
        ),
        (
            CouchDBMangoQuery({'_id': {'$gt': None}}),
            ['c2', 'c4'],
            T1.all().order_by(T1.c2.amount, T1.c4.amount)
        ),
        (
            CouchDBMangoQuery({'_id': {'$gt': None}}),
            ['c2', 'c4', 'c3'],
            T1.all().order_by(T1.c2.amount, T1.c4.amount, T1.c3.amount)
        ),
        (
            CouchDBMangoQuery({'_id': {'$gt': None}}),
            ['c4', 'c3', 'c2'],
            T1.all().order_by(T1.c4.amount, T1.c3.amount, T1.c2.amount)
        ),
        (
            CouchDBMangoQuery({'_id': {'$gt': None}}),
            [{'c4': 'desc'}, {'c3': 'desc'}, {'c2': 'desc'}],
            T1.all().order_by(T1.c4.amount.desc, T1.c3.amount.desc, T1.c2.amount.desc)
        )
    ])
    def test_order_sampling(self, mango_query: CouchDBMangoQuery, sort_expr, ast_expr: QueryAst):
        mango_query.sort = sort_expr
        build_result = ast_expr.build_query()
        mango_query.table_name = T1._table
        mango_query.query_identity = build_result.query_identity
        self.assertEqual(build_result, mango_query)


@pytest.mark.couchdb
class TableSamplingTest(CouchDBTestCase):

    def test_limit_sampling(self):
        mango_query = CouchDBMangoQuery({'_id': {'$gt': None}})
        mango_query.limit = 2
        build_result = T1.all().limit(2).build_query()
        mango_query.table_name = T1._table
        mango_query.query_identity = build_result.query_identity
        self.assertEqual(build_result, mango_query)

    def test_skip_sampling(self):
        mango_query = CouchDBMangoQuery({'_id': {'$gt': None}})
        mango_query.skip = 2
        build_result = T1.all().skip(2).build_query()
        mango_query.table_name = T1._table
        mango_query.query_identity = build_result.query_identity
        self.assertEqual(build_result, mango_query)

    def test_sample_sampling(self):
        mango_query = CouchDBMangoQuery({'_id': {'$gt': None}})
        mango_query.limit = 10
        mango_query.post_processors = [None]
        build_result = T1.all().sample(2).build_query()
        mango_query.table_name = T1._table
        mango_query.query_identity = build_result.query_identity
        self.assertEqual(build_result, mango_query)

    def test_complex_sampling(self):
        mango_query = CouchDBMangoQuery({'_id': {'$gt': None}})
        mango_query.limit = 10
        mango_query.skip = 3
        mango_query.post_processors = [None]
        build_result = T1.all().limit(10).skip(3).sample(2).build_query()
        mango_query.table_name = T1._table
        mango_query.query_identity = build_result.query_identity
        self.assertEqual(build_result, mango_query)
