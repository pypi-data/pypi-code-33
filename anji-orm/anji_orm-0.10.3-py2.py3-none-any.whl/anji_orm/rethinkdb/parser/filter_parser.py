# pylint: disable=no-self-use
from itertools import product, starmap
from typing import List, Optional, Tuple, Iterable, Type

import rethinkdb as R

from ...core import (
    QueryBinaryFilterStatement, StatementType, Interval, QueryBuildException, QueryRow,
    SamplingType, Model, QueryRowOrderMark, BaseFilterQueryParser
)
from .utils import _build_row, ensure_order_str, ensure_order

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.3"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['RethinkDBFilterQueryParser']


class RethinkDBFilterQueryParser(BaseFilterQueryParser[R.RqlQuery]):

    __index_selection__: bool = True
    __target_database__: str = 'RethinkDB'

    def build_empty_query(self, db_query: R.RqlQuery) -> R.RqlQuery:  # pylint: disable=no-self-use
        return db_query.filter(lambda doc: False)

    def build_table_query(self, db_query: R.RqlQuery, _model_class: Type['Model']) -> R.RqlQuery:  # pylint: disable=no-self-use
        return db_query

    def complicated_statement_filter(self, statement: QueryBinaryFilterStatement) -> bool:  # pylint: disable=no-self-use
        return statement.complicated or statement.statement_type == StatementType.match

    def process_simple_statement(self, db_query: R.RqlQuery, simple_statement: QueryBinaryFilterStatement) -> R.RqlQuery:  # pylint: disable=no-self-use
        row = _build_row(simple_statement.left)
        if simple_statement.statement_type == StatementType.isin:
            rethinkdb_expr = R.expr(simple_statement.right)
            return db_query.filter(lambda doc: rethinkdb_expr.contains(_build_row(simple_statement.left, document=doc)))
        if simple_statement.statement_type == StatementType.bound:
            interval: Interval = simple_statement.right
            left_operation = 'ge' if interval.left_close else 'gt'
            right_operation = 'le' if interval.right_close else 'lt'
            return db_query.filter(
                getattr(row, left_operation)(interval.left_bound) &
                getattr(row, right_operation)(interval.right_bound)
            )
        return db_query.filter(getattr(row, f'__{simple_statement.statement_type.name}__')(simple_statement.right))

    def secondary_indexes_query(  # pylint: disable=too-many-locals,too-many-branches
            self, db_query: R.RqlQuery,
            indexed_statements: List[QueryBinaryFilterStatement], selected_index: str) -> R.RqlQuery:
        index_bounds = self.index_bounds(indexed_statements)
        isin_used = False
        left_filter: List[List] = [[]]
        right_filter: List[List] = [[]]
        for statement in indexed_statements:
            if statement.statement_type == StatementType.isin:
                isin_used = True
                if len(left_filter) == 1 and not left_filter[0]:
                    left_filter = [statement.right]
                    right_filter = [statement.right]
                else:
                    left_filter = list(starmap(lambda base, new_value: base + [new_value], product(left_filter, statement.right)))
                    right_filter = list(starmap(lambda base, new_value: base + [new_value], product(right_filter, statement.right)))
            else:
                new_left_filter = None
                new_right_filter = None
                if statement.statement_type in [StatementType.ge, StatementType.gt]:
                    new_left_filter = statement.right
                    new_right_filter = R.maxval
                elif statement.statement_type in [StatementType.le, StatementType.lt]:
                    new_right_filter = statement.right
                    new_left_filter = R.minval
                elif statement.statement_type == StatementType.eq:
                    new_right_filter = statement.right
                    new_left_filter = statement.right
                elif statement.statement_type == StatementType.bound:
                    new_left_filter = statement.right.left_bound
                    new_right_filter = statement.right.right_bound
                for filter_list in left_filter:
                    filter_list.append(new_left_filter)
                for filter_list in right_filter:
                    filter_list.append(new_right_filter)
        if index_bounds is None:
            if len(left_filter) == 1 and len(indexed_statements) == 1:
                return db_query.get_all(*left_filter[0], index=selected_index)
            return db_query.get_all(*left_filter, index=selected_index)
        if len(left_filter) > 1:
            raise QueryBuildException("Cannot use multiply index with between statement, please rewrite query or write query via rethinkdb")
        if len(left_filter[0]) == 1:
            # Just base unpack, to fix privous initial pack
            left_filter = left_filter[0]
            right_filter = right_filter[0]
        # Fix bound to not have None value
        default_bound_value = False
        if isin_used:
            if index_bounds[0] is False or index_bounds[1] is False:
                raise QueryBuildException("Cannot build valid query with one_of and between, please rewrite query or write query via rethinkdb")
            default_bound_value = True
        left_bound, right_bound = self.wrap_bounds(index_bounds, default_bound_value)
        return db_query.between(
            left_filter[0], right_filter[0], index=selected_index,
            left_bound=left_bound, right_bound=right_bound
        )

    def index_bounds(self, statements: Iterable[QueryBinaryFilterStatement]):  # pylint: disable=no-self-use
        right_close = None
        left_close = None
        bound_statements = [
            StatementType.bound, StatementType.ge, StatementType.gt,
            StatementType.le, StatementType.lt
        ]
        for statement in filter(lambda x: x.statement_type in bound_statements, statements):
            if statement.statement_type == StatementType.le and right_close is None or right_close:
                right_close = True
            elif statement.statement_type == StatementType.lt and right_close is None or not right_close:
                right_close = False
            elif statement.statement_type == StatementType.ge and left_close is None or left_close:
                left_close = True
            elif statement.statement_type == StatementType.gt and left_close is None or not left_close:
                left_close = False
            elif statement.statement_type == StatementType.bound:
                if left_close is None or left_close == statement.right.left_close:
                    left_close = statement.right.left_close
                else:
                    raise QueryBuildException("Cannot build query: inconsistency bounds for indexes")
                if right_close is None or right_close == statement.right.right_close:
                    right_close = statement.right.right_close
                else:
                    raise QueryBuildException("Cannot build query: inconsistency bounds for indexes")
            else:
                raise QueryBuildException("Cannot build query: inconsistency bounds for indexes")
        if right_close is None and left_close is None:
            return None
        return left_close, right_close

    def wrap_bound(self, bound: bool) -> str:  # pylint: disable=no-self-use
        return 'closed' if bound else 'open'

    def wrap_bounds(self, index_bounds: Tuple[bool, bool], default_value: bool) -> Tuple[str, str]:
        return self.wrap_bound(index_bounds[0] or default_value), self.wrap_bound(index_bounds[1] or default_value)

    def process_complicated_statement(self, db_query: R.RqlQuery, statement: QueryBinaryFilterStatement) -> R.RqlQuery:  # pylint: disable=no-self-use
        if not isinstance(statement, QueryBinaryFilterStatement):
            raise QueryBuildException("Unsupported query ast type to build")
        if statement.statement_type == StatementType.isin:
            if isinstance(statement.left, QueryRow):
                return db_query.filter(
                    lambda doc: _build_row(statement.right, document=doc).contains(
                        _build_row(statement.left, document=doc)
                    ))
            return db_query.filter(
                lambda doc: _build_row(
                    statement.right, document=doc
                ).contains(statement.left)
            )
        if statement.statement_type == StatementType.bound:
            raise QueryBuildException("How did you even get here?")
        if statement.statement_type == StatementType.match:
            if isinstance(statement.right, QueryRow):
                return db_query.filter(
                    lambda doc: _build_row(statement.left, document=doc).match(
                        _build_row(statement.right, document=doc)
                    ))
            return db_query.filter(
                lambda doc: _build_row(
                    statement.left, document=doc
                ).match(statement.right)
            )
        return db_query.filter(
            getattr(
                _build_row(statement.left),
                f'__{statement.statement_type.name}__'
            )(_build_row(statement.right))
        )

    def process_sampling_statement(self, db_query: R.RqlQuery, sampling_type: SamplingType, sampling_arg) -> R.RqlQuery:
        if sampling_type == SamplingType.order_by:
            db_query = self.process_order_by(db_query, sampling_arg)
        else:
            db_query = getattr(db_query, sampling_type.name)(sampling_arg)
        return db_query

    def process_order_by_possible_index(  # pylint: disable=no-self-use
            self, model: Optional[Type[Model]], order_possible_index: List[str]) -> Tuple[str, int]:
        if model is None:
            raise QueryBuildException("Cannot build order_by with model as None!")
        selected_index, unused_fields = model._index_policy.value.select_secondary_index(
            model, order_possible_index, ordered=True
        )
        return selected_index, len(unused_fields)

    def fast_order_by_process(self, db_query: R.RqlQuery, order_row: QueryRowOrderMark) -> R.RqlQuery:  # pylint: disable=no-self-use
        if order_row.secondary_index and not isinstance(db_query, R.ast.Filter):
            return db_query.order_by(index=ensure_order(order_row))
        return db_query.order_by(ensure_order(order_row))

    def process_order_by(
            self, db_query: R.RqlQuery,
            order_by_statements: List[QueryRowOrderMark]) -> R.RqlQuery:
        if len(order_by_statements) == 1:
            return self.fast_order_by_process(
                db_query, order_by_statements[0]
            )
        order_possible_index: List[str] = []
        global_order = order_by_statements[0].order
        counter = 0
        for order_row_mark in order_by_statements:
            if not order_row_mark.secondary_index:
                break
            if global_order == order_row_mark.order:
                order_possible_index.append(order_row_mark.row_name)
                counter += 1
            else:
                break
        if order_possible_index and not isinstance(db_query, R.ast.Filter):
            selected_index, useless_length = self.process_order_by_possible_index(
                order_by_statements[0].row.model_ref,
                order_possible_index
            )
            counter -= useless_length
            return db_query.order_by(
                *[ensure_order(row_mark) for row_mark in order_by_statements[counter:]],
                index=ensure_order_str(selected_index, global_order)
            )

        return db_query.order_by(
            *[ensure_order(row_mark) for row_mark in order_by_statements]
        )
