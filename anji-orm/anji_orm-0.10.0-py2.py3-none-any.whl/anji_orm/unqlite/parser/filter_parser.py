# pylint: disable=no-self-use
import functools
from typing import Type, Callable
import operator

from toolz import curried, functoolz

from ...core import (
    QueryBinaryFilterStatement, SamplingType, Model,
    BaseFilterQueryParser, QueryFilterStatement, QueryTable,
    QueryRowOrderMark
)

from .utils import UnqliteQuery

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.0"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['UnqliteFilterQueryParser']


SAMPLING_CANDIDATE = 5


_itemgetter_rows = operator.itemgetter("rows")  # pylint: disable=invalid-name
_itemgetter_doc = operator.itemgetter("doc")  # pylint: disable=invalid-name


class UnqliteFilterQueryParser(BaseFilterQueryParser[UnqliteQuery]):

    __index_selection__ = False
    __sample_emulation__ = True
    __processing_hook_support__ = True
    __target_database__ = 'Unqlite'

    def build_empty_query(self, _db_query: UnqliteQuery) -> UnqliteQuery:
        new_query = UnqliteQuery('non_table')
        new_query.set_filter(lambda x: False)
        return new_query

    def build_table_query(self, db_query: UnqliteQuery, _model_class: Type[Model]) -> UnqliteQuery:
        return db_query

    def parse_filter_query(
            self, db_query: UnqliteQuery, query: QueryFilterStatement,
            model_class: Type[Model]) -> UnqliteQuery:
        if isinstance(query, QueryTable):
            db_query = self.build_table_query(db_query, model_class)
        else:
            db_query.set_filter(
                functools.partial(
                    query.to_python,
                    access_method=operator.getitem
                )
            )
        return self.process_sampling_statements(query, db_query)

    def process_sampling_statement(self, db_query: UnqliteQuery, sampling_type: SamplingType, sampling_arg) -> UnqliteQuery:
        if sampling_type == SamplingType.order_by:
            general_direction = None
            sort_steps = []
            sort_buffer = []
            order_mark: QueryRowOrderMark
            for order_mark in sampling_arg:
                if general_direction is None:
                    general_direction = order_mark.order
                if general_direction == order_mark.order:
                    sort_buffer.append(order_mark.row_name)
                else:
                    sort_steps.append({
                        'order': general_direction,
                        'keys': sort_buffer.copy()
                    })
                    sort_buffer.clear()
            sort_steps.append({  # type: ignore
                'order': general_direction,
                'keys': sort_buffer.copy()
            })
            sort_buffer.clear()
            sort_steps.reverse()
            db_query = self.add_post_processing_hook(
                db_query,
                functoolz.compose(
                    iter,
                    functoolz.compose(
                        *[
                            curried.sorted(
                                key=operator.attrgetter(*x['keys']),
                                reverse=x['order'] == 'desc'
                            )
                            for x in sort_steps
                        ]
                    )
                )
            )
        elif sampling_type == SamplingType.limit:
            db_query = self.add_post_processing_hook(db_query, curried.take(sampling_arg))
        elif sampling_type == SamplingType.skip:
            db_query = self.add_post_processing_hook(db_query, curried.drop(sampling_arg))
        return db_query

    def add_post_processing_hook(self, db_query: UnqliteQuery, hook: Callable) -> UnqliteQuery:
        db_query.add_post_hook(hook)
        return db_query

    def add_pre_processing_hook(self, db_query: UnqliteQuery, hook: Callable) -> UnqliteQuery:
        db_query.add_pre_hook(hook)
        return db_query

    def process_simple_statement(
            self, db_query: UnqliteQuery,  # pylint: disable=unused-argument
            simple_statement: QueryBinaryFilterStatement) -> UnqliteQuery:  # pylint: disable=unused-argument
        raise TypeError('You should not call this methods ...')

    def process_complicated_statement(
            self, db_query: UnqliteQuery,  # pylint: disable=unused-argument
            statement: QueryBinaryFilterStatement) -> UnqliteQuery:  # pylint: disable=unused-argument
        raise TypeError('You should not call this methods ...')
