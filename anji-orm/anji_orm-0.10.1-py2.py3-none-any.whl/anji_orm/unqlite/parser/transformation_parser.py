# pylint: disable=no-self-use

from typing import Callable

from toolz import curried

from ...core import QueryRow, BaseTransformationQueryParser
from .utils import UnqliteQuery, build_row

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.1"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['UnqliteTransformationQueryParser']


class UnqliteTransformationQueryParser(BaseTransformationQueryParser[UnqliteQuery]):

    def add_post_processing_hook(self, db_query: UnqliteQuery, hook: Callable) -> UnqliteQuery:
        db_query.add_post_hook(hook)
        return db_query

    def add_pre_processing_hook(self, db_query: UnqliteQuery, hook: Callable) -> UnqliteQuery:
        db_query.add_pre_hook(hook)
        return db_query

    def process_group_statement(self, db_query: UnqliteQuery, group_row: QueryRow) -> UnqliteQuery:
        db_query.group_usage = True
        return self.add_post_processing_hook(
            db_query,
            curried.groupby(build_row(group_row))  # pylint: disable=no-value-for-parameter
        )
