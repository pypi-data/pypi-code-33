import logging
from typing import Any, Optional, Dict, Type, AsyncIterable, Tuple
from datetime import datetime
import operator

import rethinkdb as R

from ..core import AbstractAsyncExecutor, AbstractSyncExecutor, Model, ensure_dict, fetch, orm_register

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.3"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ["RethinkDBSyncExecutor", "RethinkDBAsyncExecutor"]

_log = logging.getLogger(__name__)


def _convert_changefeed(doc):
    old_val = doc.pop('old_val', None)
    doc['doc'] = doc.pop('new_val', None)
    if doc['doc'] is None:
        doc['doc'] = old_val
    return orm_register.backend_adapter.ensure_compatibility(doc)


def _save_fetch(iterable):
    try:
        for next_doc in iterable:
            if 'new_val' in next_doc or 'old_val' in next_doc:
                yield _convert_changefeed(next_doc)
            else:
                yield fetch(next_doc)
    except R.ReqlOpFailedError as exc:
        if not exc.message == 'Changefeed aborted (unavailable).':
            raise
        _log.info("Exception %s was hidden, because of useless ...", repr(exc))


def process_driver_response(result):
    if isinstance(result, (R.net.DefaultCursor, list)):
        return filter(
            operator.truth,
            _save_fetch(result)
        )
    if isinstance(result, dict):
        return fetch(result)
    return orm_register.backend_adapter.ensure_compatibility(result)


async def fetch_cursor(cursor) -> AsyncIterable[Dict[str, Any]]:
    """
    Additonal method that wraps asyncio rethinkDB cursos to AsyncIterable.
    Just util method to allow async for usage
    """
    try:
        while await cursor.fetch_next():
            next_doc = await cursor.next()
            if 'new_val' in next_doc or 'old_val' in next_doc:
                yield _convert_changefeed(next_doc)
            else:
                yield orm_register.backend_adapter.ensure_compatibility(next_doc)
    except R.ReqlOpFailedError as exc:
        if not exc.message == 'Changefeed aborted (unavailable).':
            raise
        _log.info("Exception %s was hidden, because of useless ...", repr(exc))


async def process_async_driver_response(result, async_cursor_flush: bool):
    if result.__class__.__name__ == 'AsyncioCursor':
        if async_cursor_flush:
            return process_driver_response(
                [x async for x in fetch_cursor(result)]  # pylint: disable=not-an-iterable
            )
        return fetch_cursor(result)
    return process_driver_response(result)


class RethinkDBSyncExecutor(AbstractSyncExecutor[R.RqlQuery]):

    def send_model(self, model: Model) -> Dict:
        model.orm_last_write_timestamp = datetime.now(R.make_timezone("00:00"))
        model_dict = model.to_dict()
        model_dict = orm_register.backend_adapter.model_serialization(model_dict, model.__class__)
        if not model.id:
            result = self.strategy.execute_query(R.table(model._table).insert(model_dict))
            model.id = result['generated_keys'][0]
        else:
            result = self.strategy.execute_query(R.table(model._table).get(model.id).replace(model_dict))
            if result['skipped'] > 0:
                model_dict['id'] = model.id
                result = self.strategy.execute_query(R.table(model._table).insert(model_dict))
        return result

    def load_model(self, model: Model) -> Tuple[Dict, Optional[Dict]]:
        record_dict = self.strategy.execute_query(R.table(model._table).get(model.id))
        record_dict = orm_register.backend_adapter.model_deserialization(record_dict, model.__class__)
        return record_dict, None

    def delete_model(self, model: Model) -> Dict:
        return self.strategy.execute_query(R.table(model._table).get(model.id).delete())

    def get_model(self, model_cls: Type[Model], id_) -> Optional[Model]:
        model_data = self.strategy.execute_query(R.table(model_cls._table).get(id_))
        if model_data is None:
            return None
        return fetch(model_data)

    def execute_query(self, query, without_fetch: bool = False):
        execution_result = self.strategy.execute_query(query)
        if without_fetch:
            return execution_result
        return process_driver_response(execution_result)


class RethinkDBAsyncExecutor(AbstractAsyncExecutor[R.RqlQuery]):

    async def send_model(self, model: Model) -> Dict:
        model.orm_last_write_timestamp = datetime.now(R.make_timezone("00:00"))
        model_dict = model.to_dict()
        model_dict = orm_register.backend_adapter.model_serialization(model_dict, model.__class__)
        await ensure_dict(model_dict)
        if not model.id:
            result = await self.strategy.execute_query(R.table(model._table).insert(model_dict))
            model.id = result['generated_keys'][0]
        else:
            result = await self.strategy.execute_query(R.table(model._table).get(model.id).replace(model_dict))
            if result['skipped'] > 0:
                model_dict['id'] = model.id
                result = await self.strategy.execute_query(R.table(model._table).insert(model_dict))
        return result

    async def load_model(self, model: Model) -> Tuple[Dict, Optional[Dict]]:
        record_dict = await self.strategy.execute_query(R.table(model._table).get(model.id))
        record_dict = orm_register.backend_adapter.model_deserialization(record_dict, model.__class__)
        return record_dict, None

    async def delete_model(self, model: Model) -> Dict:
        return await self.strategy.execute_query(R.table(model._table).get(model.id).delete())

    async def get_model(self, model_cls: Type[Model], id_) -> Optional[Model]:
        model_data = await self.strategy.execute_query(R.table(model_cls._table).get(id_))
        if model_data is None:
            return None
        return fetch(model_data)

    async def execute_query(self, query, without_fetch: bool = False):
        execution_result = await self.strategy.execute_query(query)
        if without_fetch:
            return execution_result
        return await process_async_driver_response(
            execution_result,
            not isinstance(query, R.ast.Changes)
        )
