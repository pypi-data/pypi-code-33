# pylint: disable=invalid-name
from typing import Dict, Optional
from parameterized import parameterized

import pytest

from anji_orm import Model, Field, QueryAst, IndexPolicy
from anji_orm.couchdb.lib import CouchDBMangoQuery

from .base import CouchDBTestCase


class T1(Model):

    _table = 'non_table'
    _index_policy: IndexPolicy = IndexPolicy.greedyless

    c1: Optional[int] = Field(secondary_index=True)
    c2: Optional[str] = Field(secondary_index=True)
    c3: Optional[str]
    c4: Optional[str] = Field(secondary_index=True)
    c5: Optional[bool]
    c6: Optional[str]
    c7: Optional[Dict]


@pytest.mark.couchdb
class QueryTestCase(CouchDBTestCase):

    @parameterized.expand([
        [T1.c3.one_of(1, 2), CouchDBMangoQuery({"c3": {"$in": (1, 2)}})],
        [T1.c3 == 1, CouchDBMangoQuery({"c3": {"$eq": 1}})],
        [T1.c3 > 1, CouchDBMangoQuery({"c3": {"$gt": 1}})],
        [T1.c3 >= 1, CouchDBMangoQuery({"c3": {"$gte": 1}})],
        [T1.c3 < 1, CouchDBMangoQuery({"c3": {"$lt": 1}})],
        [T1.c3 <= 1, CouchDBMangoQuery({"c3": {"$lte": 1}})],
        [T1.c3 != 1, CouchDBMangoQuery({"c3": {"$ne": 1}})],
        [(T1.c3 <= 10) & (T1.c3 >= 5), CouchDBMangoQuery({"c3": {"$lte": 10, "$gte": 5}})],
        [(T1.c3 < 10) & (T1.c3 >= 5), CouchDBMangoQuery({"c3": {"$lt": 10, "$gte": 5}})],
        [(T1.c3 <= 10) & (T1.c3 > 5), CouchDBMangoQuery({"c3": {"$lte": 10, "$gt": 5}})],
        [(T1.c3 < 10) & (T1.c3 > 5), CouchDBMangoQuery({"c3": {"$lt": 10, "$gt": 5}})],
    ])
    def test_simple_build(self, query: QueryAst, mango_query: CouchDBMangoQuery):
        build_result = query.build_query()
        mango_query.table_name = T1._table
        mango_query.query_identity = build_result.query_identity
        self.assertEqual(build_result, mango_query)

    @parameterized.expand([
        [T1.c5 & (T1.c3 == 5), CouchDBMangoQuery({"c5": {"$eq": True}, "c3": {"$eq": 5}})],
        [(T1.c3 == 5) & T1.c5, CouchDBMangoQuery({"c5": {"$eq": True}, "c3": {"$eq": 5}})],
        [T1.c5 & (T1.c3 == 5) & (T1.c6 > 5), CouchDBMangoQuery({"c5": {"$eq": True}, "c3": {"$eq": 5}, "c6": {"$gt": 5}})],
        [(T1.c3 == 5) & (T1.c6 > 5) & T1.c5, CouchDBMangoQuery({"c5": {"$eq": True}, "c3": {"$eq": 5}, "c6": {"$gt": 5}})],
        [T1.c5.false() & (T1.c3 == 5), CouchDBMangoQuery({"c5": {"$eq": False}, "c3": {"$eq": 5}})],
    ])
    def test_boolean_convert(self, query: QueryAst, mango_query: CouchDBMangoQuery):
        build_result = query.build_query()
        mango_query.table_name = T1._table
        mango_query.query_identity = build_result.query_identity
        self.assertEqual(build_result, mango_query)

    def test_table_query(self):
        build_result = T1.all().build_query()
        mango_query = CouchDBMangoQuery({"_id": {"$gt": None}})
        mango_query.table_name = T1._table
        mango_query.query_identity = build_result.query_identity
        self.assertEqual(build_result, mango_query)

    @parameterized.expand([
        [T1.c7.c1 == 6, CouchDBMangoQuery({"c7.c1": {"$eq": 6}})],
        [(T1.c7.c1 == 6) & (T1.c7.c2 > 5), CouchDBMangoQuery({"c7.c1": {"$eq": 6}, "c7.c2": {"$gt": 5}})],
        [(T1.c7.c1 >= 6) & (T1.c7.c1 <= 10), CouchDBMangoQuery({"c7.c1": {"$gte": 6, "$lte": 10}})],
    ])
    def test_nested_build(self, query: QueryAst, mango_query: CouchDBMangoQuery):
        build_result = query.build_query()
        mango_query.table_name = T1._table
        mango_query.query_identity = build_result.query_identity
        self.assertEqual(build_result, mango_query)
