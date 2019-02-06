import unittest
from unittest.mock import patch

from toolz.functoolz import compose

from anji_orm import QueryAst, orm_register, Model


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        with patch('rethinkdb.connect'):
            orm_register.init('rethinkdb://', {})

    def assertAstEqual(self, first_ast: QueryAst, second_ast: QueryAst) -> None:  # pylint: disable=invalid-name
        if first_ast != second_ast:
            raise self.failureException(f"Query ast {str(first_ast)} are not the same as query ast {str(second_ast)}")


def mark_class(*markers):
    '''Workaround for https://github.com/pytest-dev/pytest/issues/568'''
    import types

    marker_func = compose(*markers)

    def copy_func(func):
        try:
            return types.FunctionType(func.__code__, func.__globals__,
                                      name=func.__name__, argdefs=func.__defaults__,
                                      closure=func.__closure__)
        except AttributeError:
            return types.FunctionType(func.func_code, func.func_globals,
                                      name=func.func_name,
                                      argdefs=func.func_defaults,
                                      closure=func.func_closure)

    def mark(cls):
        for method in dir(cls):
            if method.startswith('test_'):
                func = copy_func(getattr(cls, method))
                setattr(cls, method, marker_func(func))
        return cls
    return mark


def purge_query_row_cache(*models: Model) -> None:
    for model in models:
        for field in model._fields.values():
            field._query_row_cache = {}
