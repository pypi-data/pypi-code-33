# pylint: disable=invalid-name,singleton-comparison
from typing import Dict, Optional
import rethinkdb as R

from parameterized import parameterized
import pytest

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
    c6: Optional[str]
    c7: Optional[Dict]


boolean_row = R.row['c5']
row = R.row['c3']
rethinkdb_list = R.expr(['a1', 'a2'])


@pytest.mark.rethinkdb
class BaseQueryTest(RethinkDBTestCase):

    @parameterized.expand([
        [
            R.table('non_table').get_all('a1', 'a2', index='c2'),
            T1.c2.one_of('a1', 'a2')
        ],
        [
            R.table('non_table').get_all('a1', index='c2'),
            T1.c2 == 'a1'
        ],
        [
            R.table('non_table').between(
                'a1', R.maxval, index='c2', left_bound='open', right_bound='open'
            ),
            T1.c2 > 'a1'
        ],
        [
            R.table('non_table').between(
                'a1', R.maxval, index='c2', left_bound='closed', right_bound='open'
            ),
            T1.c2 >= 'a1'
        ],
        [
            R.table('non_table').between(
                R.minval, 'a1', index='c2', left_bound='open', right_bound='open'
            ),
            T1.c2 < 'a1'
        ],
        [
            R.table('non_table').between(
                R.minval, 'a1', index='c2', left_bound='open', right_bound='closed'
            ),
            T1.c2 <= 'a1'
        ],
        [
            R.table('non_table').between(
                5, 10, index='c2', left_bound='closed', right_bound='closed'
            ),
            (T1.c2 <= 10) & (T1.c2 >= 5)
        ],
        [
            R.table('non_table').between(
                5, 10, index='c2', left_bound='closed', right_bound='open'
            ),
            (T1.c2 < 10) & (T1.c2 >= 5)
        ],
        [
            R.table('non_table').between(
                5, 10, index='c2', left_bound='open', right_bound='closed'
            ),
            (T1.c2 <= 10) & (T1.c2 > 5)
        ],
        [
            R.table('non_table').between(
                5, 10, index='c2', left_bound='open', right_bound='open'
            ),
            (T1.c2 < 10) & (T1.c2 > 5)
        ],
        [
            R.table('non_table').get_all(['t1', 't2'], index='c1:c2'),
            (T1.c1 == 't1') & (T1.c2 == 't2'),

        ],
        [
            R.table('non_table').filter(lambda doc: doc['c1'].contains('5')),
            T1.c1.contains('5')
        ],
        [
            R.table('non_table').filter(lambda doc: doc['c1'].contains(doc['c2'])),
            T1.c1.contains(T1.c2)
        ],
        [
            R.table('non_table').get_all('a1', 'a2', index='c2').filter(R.row['c3'] < 5),
            (T1.c2.one_of('a1', 'a2')) & (T1.c3 < 5)
        ]
    ])
    def test_secondary_index_build(self, r_query, query):
        self.assertQueryEqual(r_query, query.build_query())

    def test_table_query_build(self):
        self.assertQueryEqual(
            T1.all().build_query(),
            R.table(T1._table)
        )

    @parameterized.expand([
        [
            R.table('non_table').filter(boolean_row == True).filter(row == 5),
            T1.c5 & (T1.c3 == 5)
        ],
        [
            R.table('non_table').filter(row == 5).filter(boolean_row == True),
            (T1.c3 == 5) & T1.c5
        ],
        [
            R.table('non_table').filter(boolean_row == True).filter(row == 5).filter(R.row['c6'] > 5),
            T1.c5 & (T1.c3 == 5) & (T1.c6 > 5)
        ],
        [
            R.table('non_table').filter(row == 5).filter(R.row['c6'] > 5).filter(boolean_row == True),
            (T1.c3 == 5) & (T1.c6 > 5) & T1.c5
        ],
        [
            R.table('non_table').filter(boolean_row == False).filter(row == 5),
            T1.c5.false() & (T1.c3 == 5)
        ],
    ])
    def test_boolean_convert(self, r_query, query):
        self.assertQueryEqual(r_query, query.build_query())

    @parameterized.expand([
        [
            R.table('non_table').filter(lambda doc: rethinkdb_list.contains(doc['c3'])),
            T1.c3.one_of('a1', 'a2')
        ],
        [
            R.table('non_table').filter(row == 'a1'),
            T1.c3 == 'a1'
        ],
        [
            R.table('non_table').filter(row > 'a1'),
            T1.c3 > 'a1'
        ],
        [
            R.table('non_table').filter(row >= 'a1'),
            T1.c3 >= 'a1'
        ],
        [
            R.table('non_table').filter(row < 'a1'),
            T1.c3 < 'a1'
        ],
        [
            R.table('non_table').filter(row <= 'a1'),
            T1.c3 <= 'a1'
        ],
        [
            R.table('non_table').filter((row <= 10) & (row >= 5)),
            (T1.c3 <= 10) & (T1.c3 >= 5)
        ],
        [
            R.table('non_table').filter((row < 10) & (row >= 5)),
            (T1.c3 < 10) & (T1.c3 >= 5)
        ],
        [
            R.table('non_table').filter((row <= 10) & (row > 5)),
            (T1.c3 <= 10) & (T1.c3 > 5)
        ],
        [
            R.table('non_table').filter((row < 10) & (row > 5)),
            (T1.c3 < 10) & (T1.c3 > 5)
        ],
        (
            R.table('non_table').filter(lambda doc: doc['c7']['c2'].match(5)),
            T1.c7.c2.match(5)
        )
    ])
    def test_simple_build(self, r_query, query):
        self.assertQueryEqual(r_query, query.build_query())

    @parameterized.expand([
        (
            R.table('non_table').get_all(5, index='c1').filter(lambda doc: doc['c7']['c2'].match(5)),
            (T1.c1 == 5) & T1.c7.c2.match(5)
        )
    ])
    def test_complex_build(self, r_query, query):
        self.assertQueryEqual(r_query, query.build_query())
