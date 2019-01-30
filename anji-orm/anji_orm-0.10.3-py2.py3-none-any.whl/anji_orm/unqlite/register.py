import concurrent.futures
from datetime import datetime
from enum import Enum
import logging
from typing import List, Any, Dict, Type, Tuple, Optional, Union

import unqlite


from ..core import (
    AbstractSyncRegisterStrategy, AbstractAsyncRegisterStrategy,
    AbstractAsyncExecutor, AbstractSyncExecutor, AbstractQueryParser,
    AbstractBackendAdapter, NotSupportException, register, Model,
    DeserializationException
)

from .parser import UnqliteQueryParser
from .executor import UnqliteSyncExecutor, UnqliteAsyncExecutor


__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.3"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = [
    "SyncUnqliteRegisterStrategy", "AsyncUnqliteRegisterStrategy",
    "UnqliteBackendAdapter"
]

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

_log = logging.getLogger(__name__)


class UnqliteBackendAdapter(AbstractBackendAdapter):

    @register.value_serialization(target_type=datetime)  # type: ignore
    def serialize_datetime(self, value):  # pylint: disable=no-self-use
        if value is None:
            return value
        return value.strftime(DATETIME_FORMAT).encode()

    @register.value_deserialization(target_type=datetime)  # type: ignore
    def deserialize_datetime(self, value, result_type):  # pylint: disable=no-self-use,unused-argument
        if value is None:
            return value
        if isinstance(value, bytes):
            value = value.decode()
        return datetime.strptime(value, DATETIME_FORMAT)

    @register.value_deserialization(target_type=dict)  # type: ignore
    def deserialize_dict(self, value, _):  # pylint: disable=no-self-use,unused-argument
        if isinstance(value, dict) or value is None:
            return value
        if isinstance(value, list) and not value:
            return {}
        raise DeserializationException("Dict can be only dict or empty list!")

    @register.value_deserialization(target_type=str)  # type: ignore
    def deserialize_string(self, value, _):  # pylint: disable=no-self-use
        if isinstance(value, bytes):
            return value.decode()
        return value

    @register.value_serialization(target_type=str)  # type: ignore
    def serialize_string(self, value: str) -> bytes:  # pylint: disable=no-self-use
        if value is None:
            return value
        return value.encode('utf-8')

    @register.value_serialization(target_type=Enum)  # type: ignore
    def serialize_enum(self, value):  # pylint: disable=no-self-use
        if value is None:
            return value
        return value.name.encode('utf-8')

    @register.value_deserialization(target_type=Enum)  # type: ignore
    def deserialize_enum(self, value, result_type):  # pylint: disable=no-self-use
        if value is None:
            return value
        if isinstance(value, bytes):
            value = value.decode()
        if hasattr(result_type, '__origin__') and result_type.__origin__ is Union:
            # Try to search something for enum
            enum_class = next(filter(lambda x: issubclass(x, Enum), result_type.__args__), None)
            if enum_class is not None:
                return getattr(enum_class, value)
            raise DeserializationException("Cannot find enum ... is this even possible?")
        return getattr(result_type, value)

    def record_dict_serialization(self, record_dict: Dict, model_class: Type[Model]) -> Dict:
        record_dict.pop('id', None)
        return record_dict

    def record_dict_deserialization(self, record_dict: Dict, model_class: Type[Model]) -> Dict:
        record_dict['id'] = str(record_dict.pop('__id', None))
        return record_dict

    def fetch_processor(self, record_dict: Dict) -> Tuple[Optional[Dict], Optional[Dict]]:
        processed_record_dict, meta = super().fetch_processor(record_dict)
        if processed_record_dict is None:
            return processed_record_dict, meta
        if '_python_info' in processed_record_dict:
            processed_record_dict['_python_info'] = processed_record_dict['_python_info'].decode()
        return processed_record_dict, meta


class SyncUnqliteRegisterStrategy(AbstractSyncRegisterStrategy):

    def __init__(self, connection_uri: str, **pool_kwargs: Any) -> None:  # pylint: disable=super-init-not-called

        self.db_connection = unqlite.UnQLite(filename=connection_uri.split('://')[1])
        self._backend_adapter = UnqliteBackendAdapter()
        self._query_parser = UnqliteQueryParser()
        self._executor = UnqliteSyncExecutor(self)

    @property
    def executor(self) -> AbstractSyncExecutor:
        return self._executor

    @property
    def query_parser(self) -> AbstractQueryParser:
        return self._query_parser

    @property
    def backend_adapter(self) -> AbstractBackendAdapter:
        return self._backend_adapter

    @property
    def db(self) -> Any:
        return self.db_connection

    def execute_query(self, query: Any) -> Any:
        raise NotSupportException("Please, use db object directly")

    def load(self) -> None:
        pass

    def create_index(
            self, table_name: str,
            index_name: str, index_fields: List[str]) -> None:
        _log.warning(
            'Unqlite backend does not support indexing, index %s will not be created',
            index_name
        )

    def drop_index(self, table_name: str, index_name: str) -> None:
        _log.warning(
            'Unqlite backend does not support indexing, index %s will not be dropped',
            index_name
        )

    def list_indexes(self, table_name: str) -> List[str]:
        return []

    def create_table(self, table_name: str) -> None:
        self.db.collection(table_name).create()

    def drop_table(self, table_name: str) -> None:
        self.db.collection(table_name).drop()

    def truncate_table(self, table_name: str) -> None:
        self.db.collection(table_name).drop()
        self.db.collection(table_name).create()

    def list_tables(self) -> List[str]:
        # Note, that in unqlite currently you cannot fetch
        # list of tables, so we will be recreated it over and over
        return []

    def close(self) -> None:
        self.db.close()


class AsyncUnqliteRegisterStrategy(AbstractAsyncRegisterStrategy):

    def __init__(self, connection_uri: str, **pool_kwargs: Any) -> None:  # pylint: disable=super-init-not-called

        self.db_connection = unqlite.UnQLite(filename=connection_uri.split('://')[1])
        self._backend_adapter = UnqliteBackendAdapter()
        self._query_parser = UnqliteQueryParser()
        self._thread_executor = concurrent.futures.ThreadPoolExecutor(max_workers=pool_kwargs.get('max_workers', 4))
        self._executor = UnqliteAsyncExecutor(self, self._thread_executor)

    @property
    def executor(self) -> AbstractAsyncExecutor:
        return self._executor

    @property
    def query_parser(self) -> AbstractQueryParser:
        return self._query_parser

    @property
    def backend_adapter(self) -> AbstractBackendAdapter:
        return self._backend_adapter

    @property
    def db(self) -> Any:
        return self.db_connection

    async def execute_query(self, query: Any) -> Any:
        raise NotSupportException("Please, use db object directly")

    async def load(self) -> None:
        pass

    async def create_index(
            self, table_name: str,
            index_name: str, index_fields: List[str]) -> None:
        _log.warning(
            'Unqlite backend does not support indexing, index %s will not be created',
            index_name
        )

    async def drop_index(self, table_name: str, index_name: str) -> None:
        _log.warning(
            'Unqlite backend does not support indexing, index %s will not be dropped',
            index_name
        )

    async def list_indexes(self, table_name: str) -> List[str]:
        return []

    async def create_table(self, table_name: str) -> None:
        self.db.collection(table_name).create()

    async def drop_table(self, table_name: str) -> None:
        self.db.collection(table_name).drop()

    async def truncate_table(self, table_name: str) -> None:
        self.db.collection(table_name).drop()
        self.db.collection(table_name).create()

    async def list_tables(self) -> List[str]:
        # Note, that in unqlite currently you cannot fetch
        # list of tables, so we will be recreated it over and over
        return []

    async def close(self) -> None:
        self.db.close()
