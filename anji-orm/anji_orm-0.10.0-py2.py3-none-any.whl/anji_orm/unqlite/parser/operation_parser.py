# pylint: disable=no-self-use
from collections import Counter
from typing import Optional, Callable, Dict, Any

from toolz import itertoolz, curried, functoolz

from ...core import (
    QueryRow, BaseOperationQueryParser, AggregationType,
    QueryChangeStatement, QueryUpdateStatement, Model,
    QueryBuildException, orm_register
)
from .utils import UnqliteQuery, build_row

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.0"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['UnqliteOperationQueryParser']


def _avg_function(iterable):
    compressed_iterable = tuple(iterable)
    return sum(compressed_iterable) / len(compressed_iterable)


AGGREGATION_DICT = {
    AggregationType.max: max,
    AggregationType.min: min,
    AggregationType.sum: sum,
    AggregationType.count: itertoolz.count,
    AggregationType.avg: _avg_function
}


def _collect_update_results(result):
    counter = Counter(result)
    return {
        'replaced': counter.get(True, 0),
        'skipped': counter.get(False, 0)
    }


@functoolz.curry
def _apply_update_to_record(update_dict: Dict[str, Any], record: Model) -> bool:
    from ..executor import UnqliteModel

    was_updated = False
    for key, value in update_dict.items():
        if key in record._fields:
            if getattr(record, key) != value:
                setattr(record, key, value)
                was_updated = True
    if was_updated:
        # Note, unqlite does not support async mode
        # so there is should be something syncronous
        model_dict = UnqliteModel.pre_put(record)
        if record.id:
            result = orm_register.shared.executor.strategy.db.collection(
                record._table
            ).update(record.id, model_dict)
        else:
            result = orm_register.shared.executo.db.collection(
                record._table
            ).store(model_dict)
        UnqliteModel.post_put(record, result)
    return was_updated


class UnqliteOperationQueryParser(BaseOperationQueryParser[UnqliteQuery]):

    def add_post_processing_hook(self, db_query: UnqliteQuery, hook: Callable) -> UnqliteQuery:
        db_query.add_post_hook(hook)
        return db_query

    def add_pre_processing_hook(self, db_query: UnqliteQuery, hook: Callable) -> UnqliteQuery:
        db_query.add_pre_hook(hook)
        return db_query

    def process_aggregation_statement(
            self, db_query: UnqliteQuery, aggregation_type: AggregationType,
            row: Optional[QueryRow]) -> UnqliteQuery:  # pylint: disable=unused-argument
        next_hooks = [AGGREGATION_DICT[aggregation_type]]
        if aggregation_type != AggregationType.count:
            next_hooks.insert(0, curried.map(build_row(row)))  # pylint: disable=no-value-for-parameter
        if db_query.group_usage:
            next_hooks.reverse()
            compressed_hooks = functoolz.compose(*next_hooks)

            def group_hook_wrapper(group_dict):
                return {
                    key: compressed_hooks(value)
                    for key, value in group_dict.items()
                }

            db_query = self.add_post_processing_hook(db_query, group_hook_wrapper)
        else:
            for hook in next_hooks:
                db_query = self.add_post_processing_hook(db_query, hook)
        return db_query

    def process_change_statement(
            self, db_query: UnqliteQuery, change_statement: QueryChangeStatement) -> UnqliteQuery:
        raise NotImplementedError()

    def process_update_statement(self, db_query: UnqliteQuery, update_statement: QueryUpdateStatement) -> UnqliteQuery:  # pylint: disable=unused-argument
        if db_query.group_usage:
            raise QueryBuildException("Cannot use update for groups!")
        db_query.transaction_usage = db_query.transaction_usage or update_statement.atomic
        return self.add_post_processing_hook(
            db_query,
            functoolz.compose(
                _collect_update_results,
                curried.map(_apply_update_to_record(update_statement.update_dict))  # pylint: disable=no-value-for-parameter
            )
        )
