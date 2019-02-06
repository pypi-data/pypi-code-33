from typing import Optional

from parameterized import parameterized

from anji_orm import Model, Interval, EmptyQueryStatement, QueryRow
from anji_orm.core.ast.filters import QueryBoundStatement

from ..base import BaseTestCase


class T1(Model):

    _table = 'non_table'

    c1: Optional[str]
    c2: Optional[str]


bound_statement = QueryBoundStatement(QueryRow('c1'), Interval(4, 6, right_close=True))  # pylint: disable=invalid-name
bound_statement_rev = QueryBoundStatement(QueryRow('c1'), Interval(4, 6, left_close=True))  # pylint: disable=invalid-name
one_of_statement = T1.c1.one_of(5, 6)  # pylint: disable=invalid-name
le_statement = T1.c1 <= 5  # pylint: disable=invalid-name
empty_statement = EmptyQueryStatement()  # pylint: disable=invalid-name


class QueryMergeTest(BaseTestCase):

    @parameterized.expand([
        # equals consume check
        (T1.c1 == 5, (T1.c1 == 5) & (T1.c1.one_of(5, 6))),
        (T1.c1 == 5, (T1.c1 == 5) & (T1.c1 == 5)),
        (T1.c1 == 5, (T1.c1 == 5) & (T1.c1 <= 5)),
        (T1.c1 == 5, (T1.c1 == 5) & (T1.c1 >= 5)),
        (T1.c1 == 5, (T1.c1 == 5) & (T1.c1 < 6)),
        (T1.c1 == 5, (T1.c1 == 5) & (T1.c1 > 4)),
        (T1.c1 == 5, (T1.c1 == 5) & (T1.c1 != 4)),
        (T1.c1 == 5, (T1.c1 == 5) & ((T1.c1 < 6) & (T1.c1 > 4))),
        # equals merge check
        ((T1.c1 == 5) & (T1.c2 == 4), (T1.c1 == 5) & (T1.c2 == 4) & (T1.c1.one_of(5, 6))),
        ((T1.c1 == 5) & (T1.c2 == 4), (T1.c1 == 5) & (T1.c2 == 4) & (T1.c1 == 5)),
        ((T1.c1 == 5) & (T1.c2 == 4), (T1.c1 == 5) & (T1.c2 == 4) & (T1.c1 <= 5)),
        ((T1.c1 == 5) & (T1.c2 == 4), (T1.c1 == 5) & (T1.c2 == 4) & (T1.c1 >= 5)),
        ((T1.c1 == 5) & (T1.c2 == 4), (T1.c1 == 5) & (T1.c2 == 4) & (T1.c1 < 6)),
        ((T1.c1 == 5) & (T1.c2 == 4), (T1.c1 == 5) & (T1.c2 == 4) & (T1.c1 > 4)),
        ((T1.c1 == 5) & (T1.c2 == 4), (T1.c1 == 5) & (T1.c2 == 4) & (T1.c1 != 4)),
        ((T1.c1 == 5) & (T1.c2 == 4), (T1.c1 == 5) & (T1.c2 == 4) & ((T1.c1 < 6) & (T1.c1 > 4))),
        # bound merge check
        (T1.c1.one_of(5, 6), bound_statement & T1.c1.one_of(5, 6)),
        (bound_statement, bound_statement & (T1.c1 < 7)),
        (bound_statement, bound_statement & (T1.c1 <= 7)),
        (bound_statement, bound_statement & (T1.c1 > 4)),
        (bound_statement, bound_statement & (T1.c1 >= 4)),
        (
            bound_statement,
            QueryBoundStatement(QueryRow('c1'), Interval(3, 6, right_close=True)) & (T1.c1 > 4)
        ),
        (
            bound_statement,
            QueryBoundStatement(QueryRow('c1'), Interval(4, 8, right_close=True)) & (T1.c1 <= 6)
        ),
        (
            bound_statement_rev,
            QueryBoundStatement(QueryRow('c1'), Interval(3, 6, left_close=True)) & (T1.c1 >= 4)
        ),
        (
            bound_statement_rev,
            QueryBoundStatement(QueryRow('c1'), Interval(4, 8, left_close=True)) & (T1.c1 < 6)
        ),
        (
            bound_statement_rev,
            QueryBoundStatement(QueryRow('c1'), Interval(3, 6, left_close=True)) & bound_statement_rev
        ),
        # isin merge check
        (one_of_statement, T1.c1.one_of(5, 6, 7) & one_of_statement),
        (one_of_statement, one_of_statement & (T1.c1 >= 5)),
        (one_of_statement, one_of_statement & (T1.c1 > 4)),
        (one_of_statement, one_of_statement & (T1.c1 <= 6)),
        (one_of_statement, one_of_statement & (T1.c1 < 7)),
        # le merge
        (le_statement, le_statement & (T1.c1 < 6)),
        (le_statement, le_statement & (T1.c1 <= 6)),
        (T1.c1 < 5, le_statement & (T1.c1 < 5)),
        (T1.c1 < 4, le_statement & (T1.c1 < 4)),
        (
            QueryBoundStatement(T1.c1, Interval(4, 5, right_close=True)),
            (T1.c1 <= 5) & (T1.c1 > 4)
        ),
        (
            QueryBoundStatement(T1.c1, Interval(4, 5, right_close=True, left_close=True)),
            (T1.c1 <= 5) & (T1.c1 >= 4)
        ),
        # lt merge
        (T1.c1 < 5, (T1.c1 < 5) & (T1.c1 < 6)),
        (QueryBoundStatement(T1.c1, Interval(4, 5)), (T1.c1 < 5) & (T1.c1 > 4)),
        (QueryBoundStatement(T1.c1, Interval(4, 5, left_close=True)), (T1.c1 < 5) & (T1.c1 >= 4)),
        # ge merge
        (T1.c1 >= 5, (T1.c1 >= 5) & (T1.c1 >= 4)),
        (T1.c1 >= 5, (T1.c1 >= 5) & (T1.c1 > 4)),
        (T1.c1 > 5, (T1.c1 > 5) & (T1.c1 >= 4)),
        # gt merge
        (T1.c1 > 6, (T1.c1 > 5) & (T1.c1 > 6)),
        # ne merge
        (T1.c1.one_of(5, 10), T1.c1.one_of(5, 10, 15) & (T1.c1 != 15)),
        ((T1.c1 >= 20) & (T1.c1 <= 40), (T1.c1 >= 20) & (T1.c1 <= 40) & (T1.c1 != 15)),
        ((T1.c1 >= 20) & (T1.c1 <= 40), (T1.c1 >= 20) & (T1.c1 <= 40) & (T1.c1 != 35))
    ])
    def test_equals_merge_short(self, first_query, second_query):
        self.assertAstEqual(first_query, second_query)


class QueryEmptyTest(BaseTestCase):

    @parameterized.expand([
        # Eq statements
        ((T1.c1 == 7) & (T1.c1.one_of(5, 6)),),
        ((T1.c1 == 7) & (T1.c1 == 5),),
        ((T1.c1 == 7) & (T1.c1 <= 5),),
        ((T1.c1 == 4) & (T1.c1 >= 5),),
        ((T1.c1 == 7) & (T1.c1 < 6),),
        ((T1.c1 == 4) & (T1.c1 > 4),),
        ((T1.c1 == 4) & (T1.c1 != 4),),
        ((T1.c1 == 8) & (T1.c1 < 6) & (T1.c1 > 4),),
        # Bound statements
        ((T1.c1 >= 20) & (T1.c1 <= 40) & T1.c1.one_of(5, 6),),
        ((T1.c1 >= 20) & (T1.c1 <= 40) & (T1.c1 == 5),),
        ((T1.c1 >= 20) & (T1.c1 <= 40) & (T1.c1 <= 10),),
        ((T1.c1 >= 20) & (T1.c1 <= 40) & (T1.c1 >= 50),),
        ((T1.c1 >= 20) & (T1.c1 <= 40) & (T1.c1 < 10),),
        ((T1.c1 >= 20) & (T1.c1 <= 40) & (T1.c1 > 45),),
        ((T1.c1 >= 20) & (T1.c1 <= 40) & (T1.c1 < 6) & (T1.c1 > 4),),
        # isin statement
        (T1.c1.one_of(10, 15, 20) & T1.c1.one_of(5, 6),),
        (T1.c1.one_of(10, 15, 20) & (T1.c1 == 5),),
        (T1.c1.one_of(10, 15, 20) & (T1.c1 <= 5),),
        (T1.c1.one_of(10, 15, 20) & (T1.c1 >= 50),),
        (T1.c1.one_of(10, 15, 20) & (T1.c1 < 5),),
        (T1.c1.one_of(10, 15, 20) & (T1.c1 > 45),),
        (T1.c1.one_of(10, 15, 20) & (T1.c1 != 15) & (T1.c1 != 20) & (T1.c1 != 10),),
        (T1.c1.one_of(10, 15, 20) & ((T1.c1 < 6) & (T1.c1 > 4)),),
        # le statement
        ((T1.c1 <= 40) & T1.c1.one_of(50, 60),),
        ((T1.c1 <= 40) & (T1.c1 == 50),),
        ((T1.c1 <= 40) & (T1.c1 >= 50),),
        ((T1.c1 <= 40) & (T1.c1 > 45),),
        ((T1.c1 <= 40) & ((T1.c1 < 60) & (T1.c1 > 50)),),
        # lt statement
        ((T1.c1 < 40) & T1.c1.one_of(50, 60),),
        ((T1.c1 < 40) & (T1.c1 == 50),),
        ((T1.c1 < 40) & (T1.c1 >= 50),),
        ((T1.c1 < 40) & (T1.c1 > 45),),
        ((T1.c1 < 40) & ((T1.c1 < 60) & (T1.c1 > 50)),),
        # ge statement
        ((T1.c1 >= 40) & T1.c1.one_of(5, 6),),
        ((T1.c1 >= 40) & (T1.c1 == 5),),
        ((T1.c1 >= 40) & (T1.c1 <= 30),),
        ((T1.c1 >= 40) & (T1.c1 < 30),),
        ((T1.c1 >= 40) & ((T1.c1 < 6) & (T1.c1 > 4)),),
        # gt statement
        ((T1.c1 > 40) & T1.c1.one_of(5, 6),),
        ((T1.c1 > 40) & (T1.c1 == 5),),
        ((T1.c1 > 40) & (T1.c1 <= 30),),
        ((T1.c1 > 40) & (T1.c1 < 30),),
        ((T1.c1 > 40) & ((T1.c1 < 6) & (T1.c1 > 4)),),
        # special cases
        (empty_statement & empty_statement,)
    ])
    def test_eq_empty(self, query):
        self.assertAstEqual(empty_statement, query)
