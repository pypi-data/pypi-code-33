import asyncio
import concurrent.futures
from typing import Optional, Dict, Type, Tuple, List
from datetime import datetime
import logging
import operator

from toolz.itertoolz import isiterable

from ..core import (
    AbstractAsyncExecutor, AbstractSyncExecutor, Model, fetch,
    orm_register, AbstractAsyncRegisterStrategy
)

from .parser.utils import UnqliteQuery

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.2"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ["UnqliteSyncExecutor", "UnqliteAsyncExecutor"]

_log = logging.getLogger(__name__)


def process_driver_response(result):
    if isinstance(result, dict):
        return fetch(result)
    if isiterable(result):
        return filter(
            operator.truth,
            (
                fetch(obj_data)
                if isinstance(obj_data, dict) else obj_data
                for obj_data in result
            )
        )
    return result


class UnqliteModel:

    __slots__: List[str] = []

    @staticmethod
    def pre_put(model: Model) -> Dict:
        model.orm_last_write_timestamp = datetime.now()
        model_dict = model.to_dict()
        return orm_register.backend_adapter.model_serialization(model_dict, model.__class__)

    @staticmethod
    def post_put(model: Model, result: int) -> None:
        if model.id is None:
            try:
                model.id = str(result)
            except ValueError as exc:
                _log.warning(
                    'Strange error %s when processing put result %s',
                    exc, result
                )

    @staticmethod
    def post_get(model_cls: Type[Model], model_dict: Dict) -> Dict:
        return orm_register.backend_adapter.model_deserialization(model_dict, model_cls)


class QueryExecution:

    __slots__: List[str] = []

    @staticmethod
    def post_execution(execution_result, query: UnqliteQuery, without_fetch: bool):
        if query.pre_hooks:
            for pre_hook in query.pre_hooks:
                execution_result = pre_hook(execution_result)
        if not without_fetch:
            execution_result = process_driver_response(execution_result)
        if query.post_hooks:
            for post_hook in query.post_hooks:
                execution_result = post_hook(execution_result)
        return execution_result


class UnqliteSyncExecutor(AbstractSyncExecutor[UnqliteQuery]):

    def send_model(self, model: Model) -> Dict:
        model_dict = UnqliteModel.pre_put(model)
        if model.id:
            result = self.strategy.db.collection(model._table).update(model.id, model_dict)
        else:
            result = self.strategy.db.collection(model._table).store(model_dict)
        UnqliteModel.post_put(model, result)
        return result

    def load_model(self, model: Model) -> Tuple[Dict, Optional[Dict]]:
        if model.id is None:
            raise ValueError("Cannot load model without id")
        model_dict = self.strategy.db.collection(model._table).fetch(model.id)
        return UnqliteModel.post_get(model.__class__, model_dict), {}

    def delete_model(self, model: Model) -> Dict:
        if model.id is None:
            raise ValueError("Cannot load model without id")
        return self.strategy.db.collection(model._table).delete(model.id)

    def get_model(self, model_cls: Type[Model], id_) -> Optional[Model]:
        model_dict = self.strategy.db.collection(model_cls._table).fetch(id_)
        record = fetch(model_dict)
        return record

    def execute_query(self, query: UnqliteQuery, without_fetch: bool = False):
        if query.transaction_usage:
            self.strategy.db.begin()
        if query.filter_function is not None:
            execution_result = self.strategy.db.collection(query.table).filter(
                query.filter_function
            )
        else:
            execution_result = self.strategy.db.collection(query.table).all()
        if query.transaction_usage:
            self.strategy.db.commit()
        return QueryExecution.post_execution(execution_result, query, without_fetch)


class UnqliteAsyncExecutor(AbstractAsyncExecutor[UnqliteQuery]):

    def __init__(
            self, async_strategy: AbstractAsyncRegisterStrategy,
            thread_executor: concurrent.futures.ThreadPoolExecutor) -> None:
        super().__init__(async_strategy)
        self.thread_executor = thread_executor
        self.sync_executor = UnqliteSyncExecutor(async_strategy)  # type: ignore
        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

    async def send_model(self, model: Model) -> Dict:
        return await self.loop.run_in_executor(self.thread_executor, self.sync_executor.send_model, model)

    async def load_model(self, model: Model) -> Tuple[Dict, Optional[Dict]]:
        return await self.loop.run_in_executor(self.thread_executor, self.sync_executor.load_model, model)

    async def delete_model(self, model: Model) -> Dict:
        return await self.loop.run_in_executor(self.thread_executor, self.sync_executor.delete_model, model)

    async def get_model(self, model_cls: Type[Model], id_) -> Optional[Model]:
        return await self.loop.run_in_executor(self.thread_executor, self.sync_executor.get_model, model_cls, id_)

    async def execute_query(self, query: UnqliteQuery, without_fetch: bool = False):
        return await self.loop.run_in_executor(self.thread_executor, self.sync_executor.execute_query, query, without_fetch)
