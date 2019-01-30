import asyncio
from uuid import uuid4
from typing import Optional, Dict, Type, Tuple, List
from datetime import datetime
import logging
import operator

from toolz.itertoolz import isiterable

from ..core import (
    AbstractAsyncExecutor, AbstractSyncExecutor, Model, ensure_dict, fetch
)
from ..core.register import orm_register
from .lib import AbstractCouchDBQuery
from .utils import CouchDBRequestException

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.2"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ["CouchDBSyncExecutor", "CouchDBAsyncExecutor"]

_log = logging.getLogger(__name__)


def process_driver_response(result):
    if isinstance(result, dict):
        if 'warning' in result:
            _log.warning("CouchDB warning: %s", result['warning'])
        if 'docs' in result:
            return filter(
                operator.truth,
                (fetch(obj_data) for obj_data in result["docs"])
            )
        if 'rows' in result:
            return filter(
                operator.truth,
                (fetch(obj_data) for obj_data in result["rows"])
            )
        return fetch(result)
    if isiterable(result):
        return filter(
            operator.truth,
            (
                fetch(obj_data) if isinstance(obj_data, dict) else obj_data
                for obj_data in result
            )
        )
    return result


def generate_uuid() -> str:
    return str(uuid4()).replace('-', '')


class CouchModel:

    __slots__: List[str] = []

    @staticmethod
    def pre_put(model: Model) -> Dict:
        model.orm_last_write_timestamp = datetime.now()
        if not model.id:
            model.id = generate_uuid()
        return model.to_dict()

    @staticmethod
    def put(model: Model, model_dict: Dict) -> Dict:
        model_dict = orm_register.backend_adapter.model_serialization(model_dict, model.__class__)
        params = {}
        if '_rev' in model._meta:
            params['rev'] = model._meta['_rev']
        return {
            "method": "put",
            "url": f"/{model._table}/{model.id}",
            "json": model_dict,
            "params": params
        }

    @staticmethod
    def post_put(model: Model, result: Dict) -> None:
        model._meta['_rev'] = result['rev']

    @staticmethod
    def get(model_cls: Type[Model], record_id: str) -> Dict:
        return {
            "method": "get",
            "url": f"/{model_cls._table}/{record_id}"
        }

    @staticmethod
    def post_get(model_cls: Type[Model], model_dict: Dict) -> Tuple[Dict, Dict]:
        model_dict = orm_register.backend_adapter.model_deserialization(model_dict, model_cls)
        return model_dict, model_dict.pop('_meta')

    @staticmethod
    def delete(model: Model) -> Dict:
        return {
            "method": "delete",
            "url": f"/{model._table}/{model.id}",
            "params": dict(rev=model._meta['_rev'])
        }


class QueryExecution:

    __slots__: List[str] = []

    @staticmethod
    def post_execution(execution_result, query: AbstractCouchDBQuery, without_fetch: bool):
        if query.pre_processors is not None:
            for pre_processor in query.pre_processors:
                execution_result = pre_processor(execution_result)
        if not without_fetch:
            execution_result = process_driver_response(execution_result)
        if query.post_processors is not None:
            for post_processor in query.post_processors:
                execution_result = post_processor(execution_result)
        return execution_result


class CouchDBSyncExecutor(AbstractSyncExecutor[AbstractCouchDBQuery]):

    def send_model(self, model: Model) -> Dict:
        model_dict = CouchModel.pre_put(model)
        result = self.strategy.execute_query(CouchModel.put(model, model_dict))
        CouchModel.post_put(model, result)
        return result

    def load_model(self, model: Model) -> Tuple[Dict, Optional[Dict]]:
        if model.id is None:
            raise ValueError("Cannot load model without id")
        model_dict = self.strategy.execute_query(CouchModel.get(model.__class__, model.id))
        return CouchModel.post_get(model.__class__, model_dict)

    def delete_model(self, model: Model) -> Dict:
        return self.strategy.execute_query(CouchModel.delete(model))

    def get_model(self, model_cls: Type[Model], id_) -> Optional[Model]:
        try:
            model_dict = self.strategy.execute_query(CouchModel.get(model_cls, id_))
            record = fetch(model_dict)
        except CouchDBRequestException as exc:
            if exc.status_code == 404:
                return None
            raise
        return record

    def execute_query(self, query: AbstractCouchDBQuery, without_fetch: bool = False):
        http_generator = query.start()
        http_query = next(http_generator)
        try:
            while True:
                if not isinstance(http_query, dict) and isiterable(http_query):
                    execution_result = [self.strategy.execute_query(query) for query in http_query]
                else:
                    execution_result = self.strategy.execute_query(http_query)
                http_query = http_generator.send(execution_result)
        except StopIteration:
            pass
        return QueryExecution.post_execution(execution_result, query, without_fetch)


class CouchDBAsyncExecutor(AbstractAsyncExecutor[AbstractCouchDBQuery]):

    async def send_model(self, model: Model) -> Dict:
        model_dict = CouchModel.pre_put(model)
        await ensure_dict(model_dict)
        result = await self.strategy.execute_query(CouchModel.put(model, model_dict))
        CouchModel.post_put(model, result)
        return result

    async def load_model(self, model: Model) -> Tuple[Dict, Optional[Dict]]:
        if model.id is None:
            raise ValueError("Cannot load model without id")
        model_dict = await self.strategy.execute_query(CouchModel.get(model.__class__, model.id))
        return CouchModel.post_get(model.__class__, model_dict)

    async def delete_model(self, model: Model) -> Dict:
        return await self.strategy.execute_query(CouchModel.delete(model))

    async def get_model(self, model_cls: Type[Model], id_) -> Optional[Model]:
        try:
            model_dict = await self.strategy.execute_query(CouchModel.get(model_cls, id_))
            record = fetch(model_dict)
        except CouchDBRequestException as exc:
            if exc.status_code == 404:
                return None
            raise
        return record

    async def execute_query(self, query: AbstractCouchDBQuery, without_fetch: bool = False):
        http_generator = query.start()
        http_query = next(http_generator)
        try:
            while True:
                if not isinstance(http_query, dict) and isiterable(http_query):
                    execution_result = await asyncio.gather(
                        *(self.strategy.execute_query(query) for query in http_query)
                    )
                else:
                    execution_result = await self.strategy.execute_query(http_query)
                http_query = http_generator.send(execution_result)
        except StopIteration:
            pass
        return QueryExecution.post_execution(execution_result, query, without_fetch)
