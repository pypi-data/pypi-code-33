# pylint: disable=no-self-use
import operator
from typing import Optional, Dict, Type, Callable
from functools import partial
from collections import Counter

from toolz import excepts, compose

try:
    import ujson as json
except ImportError:
    import json  # type: ignore

from ...core import (
    QueryRow, BaseOperationQueryParser, AggregationType,
    QueryChangeStatement, Model, QueryUpdateStatement
)
from ...core.register import orm_register
from ..lib import AbstractCouchDBQuery, CouchDBReduceFunction

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.1"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['CouchDBOperationQueryParser']


_aggregation_result_getter = excepts(StopIteration, compose(operator.itemgetter('value'), next))  # pylint: disable=invalid-name
_aggregation_group_result_converter = compose(dict, partial(map, lambda x: (x['key'], x['value'])))  # pylint: disable=invalid-name


def _convert_dict_to_compatiable_event_format(model_cls: Type[Model], event: Optional[Dict]) -> Optional[Dict]:
    result = {}
    if not event:
        return event
    event_data = event['data']
    if event_data['doc']['_id'].startswith('_design'):
        return None
    result['type'] = 'change' if event_data.get('deleted') is None else 'remove'
    event_data['doc'] = orm_register.backend_adapter.model_deserialization(event_data['doc'], model_cls)
    result['doc'] = event_data['doc']
    return result


def _convert_sse_to_compatiable_event_format(model_cls: Type[Model], event) -> Optional[Dict]:
    result = {}
    if not event or event.event == 'heartbeat':
        return None
    event_data = json.loads(event.data)
    if event_data['doc']['_id'].startswith('_design'):
        return None
    result['type'] = 'change' if event_data.get('deleted') is None else 'remove'
    event_data['doc'] = orm_register.backend_adapter.model_deserialization(event_data['doc'], model_cls)
    result['doc'] = event_data['doc']
    return result


async def _async_map(function, async_generator):
    async for element in async_generator:
        result = function(element)
        if result is not None:
            yield result


def _sync_map(function, sync_generator):
    for element in sync_generator:
        result = function(element)
        if result is not None:
            yield result


def _collect_update_results(result):
    counter = Counter(result)
    return {
        'replaced': counter.get('Document updated', 0),
        'skipped': counter.get('Document ignored', 0)
    }


class CouchDBOperationQueryParser(BaseOperationQueryParser[AbstractCouchDBQuery]):

    def add_post_processing_hook(self, db_query: AbstractCouchDBQuery, hook: Callable) -> AbstractCouchDBQuery:
        if db_query.post_processors is None:
            db_query.post_processors = []
        db_query.post_processors.append(hook)
        return db_query

    def add_pre_processing_hook(self, db_query: AbstractCouchDBQuery, hook: Callable) -> AbstractCouchDBQuery:
        if db_query.pre_processors is None:
            db_query.pre_processors = []
        db_query.pre_processors.append(hook)
        return db_query

    def process_aggregation_statement(
            self, db_query: AbstractCouchDBQuery, aggregation_type: AggregationType,
            row: Optional[QueryRow]) -> AbstractCouchDBQuery:
        db_query = db_query.to_ddoc_view()
        db_query.ddoc_view.map_function.emit_row = row
        db_query.ddoc_view.reduce_function = CouchDBReduceFunction(aggregation_type)
        if db_query.params and db_query.params.get('group', None):
            # Avoiding get first result of aggregation in case of grouping
            self.add_post_processing_hook(db_query, _aggregation_group_result_converter)
        else:
            self.add_post_processing_hook(db_query, _aggregation_result_getter)
        return db_query

    def process_change_statement(
            self, db_query: AbstractCouchDBQuery, change_statement: QueryChangeStatement) -> AbstractCouchDBQuery:
        if db_query.design_doc_usage:
            db_query = db_query.to_ddoc_filter()
        else:
            if db_query.params is None:
                db_query.params = {}
            db_query.params['filter'] = '_selector'
            db_query.url = "_changes"
            db_query.grab_connection = True
        if db_query.params is None:
            db_query.params = {}
        db_query.params.update({
            "include_docs": "true",
            "feed": "eventsource",
            "since": '0' if change_statement.with_initial else 'now',
        })
        event_processing = partial(
            _async_map if orm_register.async_mode else _sync_map,
            partial(
                _convert_dict_to_compatiable_event_format if orm_register.async_mode else _convert_sse_to_compatiable_event_format,
                change_statement.model_ref
            )
        )
        self.add_post_processing_hook(db_query, event_processing)
        return db_query

    def process_update_statement(self, db_query: AbstractCouchDBQuery, update_statement: QueryUpdateStatement) -> AbstractCouchDBQuery:  # pylint: disable=unused-argument
        base_update = db_query.to_ddoc_update()
        base_update.ddoc_update.update_function.update_dict = update_statement.update_dict
        if not update_statement.atomic:
            base_update.ddoc_update.update_function.filter_map = None
        return self.add_post_processing_hook(base_update, _collect_update_results)
