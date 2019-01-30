import rethinkdb as R
from rethinkdb import ast

from anji_orm import QueryAst

from ..base import BaseTestCase


def check_equals(first_query: R.RqlQuery, second_query: R.RqlQuery) -> bool:  # pylint: disable=too-many-return-statements
    if first_query.__class__ != second_query.__class__:
        return False
    if first_query.__class__ == ast.Datum:
        return first_query.data == second_query.data
    if first_query.__class__ == ast.Var:
        return True
    if len(first_query._args) != len(second_query._args):
        return False
    if first_query.__class__ == ast.And:
        return (
            (check_equals(first_query._args[0], second_query._args[0]) and check_equals(first_query._args[1], second_query._args[1])) or
            (check_equals(first_query._args[0], second_query._args[1]) and check_equals(first_query._args[1], second_query._args[0]))
        )
    if first_query.__class__ == ast.Func:
        return check_for_args(first_query, second_query, start_from=1)
    return check_for_args(first_query, second_query)


def check_for_args(first_query: R.RqlQuery, second_query: R.RqlQuery, start_from: int = 0) -> bool:
    for index in range(start_from, len(first_query._args)):
        if not check_equals(first_query._args[index], second_query._args[index]):
            return False
    return True


class RethinkDBTestCase(BaseTestCase):

    def assertQueryEqual(self, first_query: R.RqlQuery, second_query: R.RqlQuery) -> None:  # pylint: disable=invalid-name
        if not check_equals(first_query, second_query):
            raise self.failureException(f"Query {str(first_query)} are not the same as query {str(second_query)}")

    def assertAstEqual(self, first_ast: QueryAst, second_ast: QueryAst) -> None:  # pylint: disable=invalid-name
        if first_ast != second_ast:
            raise self.failureException(f"Query ast {str(first_ast)} are not the same as query ast {str(second_ast)}")
