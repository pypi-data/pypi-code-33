# pylint: disable=invalid-name
from typing import Optional

from parameterized import parameterized
import pytest
import rethinkdb as R

from anji_orm import Model, Field, IndexPolicy

from .base import RethinkDBTestCase


class T1(Model):

    _table = 'non_table'
    _index_policy: IndexPolicy = IndexPolicy.greedyless

    c1: Optional[str] = Field(secondary_index=True)
    c2: Optional[str] = Field(secondary_index=True)
    c3: Optional[str]
    c4: Optional[str] = Field(secondary_index=True)
    c5: Optional[bool]


@pytest.mark.rethinkdb
class SamplingTest(RethinkDBTestCase):

    def test_limit_sampling(self):
        self.assertQueryEqual(
            R.table(T1._table).get_all(5, index='c1').limit(2),
            (T1.c1 == 5).limit(2).build_query()
        )

    def test_skip_sampling(self):
        self.assertQueryEqual(
            R.table(T1._table).get_all(5, index='c1').skip(2),
            (T1.c1 == 5).skip(2).build_query()
        )

    def test_sample_sampling(self):
        self.assertQueryEqual(
            R.table(T1._table).get_all(5, index='c1').sample(2),
            (T1.c1 == 5).sample(2).build_query()
        )

    def test_complex_sampling(self):
        self.assertQueryEqual(
            R.table(T1._table).get_all(5, index='c1').limit(10).skip(3).sample(2),
            (T1.c1 == 5).limit(10).skip(3).sample(2).build_query()
        )


@pytest.mark.rethinkdb
class OrderByTestCase(RethinkDBTestCase):

    @parameterized.expand([
        (
            R.table(T1._table).get_all(5, index='c1').order_by(index='c2'),
            (T1.c1 == 5).order_by(T1.c2.amount)
        ),
        (
            R.table(T1._table).get_all(5, index='c1').order_by('c3'),
            (T1.c1 == 5).order_by(T1.c3.amount)
        ),
        (
            R.table(T1._table).order_by(index='c2:c4'),
            T1.all().order_by(T1.c2.amount, T1.c4.amount)
        ),
        (
            R.table(T1._table).order_by('c3', index='c2:c4'),
            T1.all().order_by(T1.c2.amount, T1.c4.amount, T1.c3.amount)
        ),
        (
            R.table(T1._table).order_by('c3', 'c2', index='c4'),
            T1.all().order_by(T1.c4.amount, T1.c3.amount, T1.c2.amount)
        )
    ])
    def test_order_sampling(self, target_query, ast_expr):
        self.assertQueryEqual(
            target_query,
            ast_expr.build_query()
        )


@pytest.mark.rethinkdb
class TableSamplingTest(RethinkDBTestCase):

    def test_limit_sampling(self):
        self.assertQueryEqual(
            R.table(T1._table).limit(2),
            T1.all().limit(2).build_query()
        )

    def test_skip_sampling(self):
        self.assertQueryEqual(
            R.table(T1._table).skip(2),
            T1.all().skip(2).build_query()
        )

    def test_sample_sampling(self):
        self.assertQueryEqual(
            R.table(T1._table).sample(2),
            T1.all().sample(2).build_query()
        )

    def test_complex_sampling(self):
        self.assertQueryEqual(
            R.table(T1._table).limit(10).skip(3).sample(2),
            T1.all().limit(10).skip(3).sample(2).build_query()
        )
