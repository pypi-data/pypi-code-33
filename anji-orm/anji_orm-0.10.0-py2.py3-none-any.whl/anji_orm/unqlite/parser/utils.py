import functools
import operator
import typing

from toolz import functoolz

from ...core import QueryRow

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.0"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ['UnqliteQuery', 'build_row']


@functoolz.curry
def build_row(row: QueryRow, record):
    return functools.reduce(operator.getitem, row.row_path[1:], getattr(record, row.row_path[0]))


class UnqliteQuery:

    __slots__ = (
        'table', 'filter_function',
        'post_hooks', 'pre_hooks',
        'transaction_usage', 'group_usage'
    )

    def __init__(self, table: str) -> None:
        self.table = table
        self.filter_function: typing.Optional[typing.Callable[[typing.Any], bool]] = None
        self.post_hooks: typing.List[typing.Callable[[typing.Any], typing.Any]] = []
        self.pre_hooks: typing.List[typing.Callable[[typing.Any], typing.Any]] = []
        self.transaction_usage = False
        self.group_usage = False

    def add_post_hook(self, hook: typing.Callable[[typing.Any], typing.Any]) -> None:
        self.post_hooks.append(hook)

    def add_pre_hook(self, hook: typing.Callable[[typing.Any], typing.Any]) -> None:
        self.pre_hooks.append(hook)

    def set_filter(self, filter_function: typing.Callable[[typing.Any], bool]) -> None:
        self.filter_function = filter_function
