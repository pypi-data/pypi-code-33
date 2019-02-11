import unittest

import rethinkdb as R
from parameterized import parameterized
import pytest

from .base import check_equals


@pytest.mark.rethinkdb
@pytest.mark.utils
class QueryCompareTest(unittest.TestCase):

    @parameterized.expand([
        [R.table('non_table').filter(R.row['t1'] == 't2').limit(5).count(6)],
        [R.table('non_table').filter(lambda doc: doc.match('5')).limit(5).count(6)],
        [R.table('non_table').get_all('a1', 'a2', index='c2').filter(
            lambda doc: R.expr(['a1', 'a2']).contains(doc['c3'])
        )],
        [R.table('non_table').filter((R.row['c1'] >= 5) & (R.row['c2'] <= 6))],
    ])
    def test_true_answers(self, query):
        self.assertTrue(check_equals(query, query))

    @parameterized.expand([
        (
            R.table('non_table').filter(R.row['t1'] == 't2').limit(5).count(6),
            R.table('non_table').filter(R.row['t1'] == 't3').limit(5).count(6),
        ),
        (
            R.table('non_table').get_all('a1', 'a2', index='c2').filter(
                lambda doc: R.expr(['a1', 'a2']).contains(doc['c3'])
            ),
            R.table('non_table').get_all('a1', 'a2', index='c2').filter(
                lambda doc: R.expr(['a1', 'a3']).contains(doc['c3'])
            )
        ),
        (
            R.table('non_table').min(lambda doc: doc['c6']['c3']),
            R.table('non_table').min(lambda doc: None),
        ),
        (
            R.table('non_table').min(lambda doc: doc['c6'].contains('c5')),
            R.table('non_table').min(lambda doc: doc['c6'].contains(doc['c5'])),
        )
    ])
    def test_false_positive(self, first_query, second_query):
        self.assertFalse(check_equals(first_query, second_query))
