import abc
import asyncio
from typing import Dict, Any, List, Type, TYPE_CHECKING, Tuple
from urllib.parse import urlparse
from weakref import WeakValueDictionary

from aenum import Enum, enum

from .adapter import AbstractBackendAdapter
from ..executor import AbstractSyncExecutor, AbstractAsyncExecutor
from ..parser import AbstractQueryParser
from ..utils import import_class

from ...extensions import ExtensionType, BaseExtension

if TYPE_CHECKING:
    from ..model import Model  # pylint: disable=unused-import

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.0"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = [
    'orm_register', 'AbstractAsyncRegisterStrategy',
    'AbstractSyncRegisterStrategy', 'SharedEnv', 'RegistryProtocol'
]

DUMMY_ADAPTER = AbstractBackendAdapter()


class RegisterModeMissmatch(Exception):
    """
    Base exception, that caused when you try to use sync commands in async mode
    and async commands in sync mode
    """


class RegistryProtocol(Enum):

    rethinkdb = enum(
        sync_strategy='anji_orm.rethinkdb.SyncRethinkDBRegisterStrategy',
        async_strategy='anji_orm.rethinkdb.AsyncRethinkDBRegisterStrategy'
    )

    couchdb = enum(
        sync_strategy='anji_orm.couchdb.SyncCouchDBRegisterStrategy',
        async_strategy='anji_orm.couchdb.AsyncCouchDBRegisterStrategy'
    )

    unqlite = enum(
        sync_strategy='anji_orm.unqlite.SyncUnqliteRegisterStrategy',
        async_strategy='anji_orm.unqlite.AsyncUnqliteRegisterStrategy'
    )


class RelactionCache:  # pylint: disable=too-few-public-methods

    def __init__(self):
        self._models_cache = {}

    def __getitem__(self, key: str) -> WeakValueDictionary:
        return self._models_cache.setdefault(key, WeakValueDictionary())


class SharedEnv:

    def __init__(self):
        self._env = {}
        self.share('relation_cache', RelactionCache())

    def share(self, key: str, value: Any) -> None:
        self._env[key] = value

    def __getattr__(self, key: str) -> Any:
        if key in self._env:
            return self._env[key]
        raise AttributeError


class AbstractAsyncRegisterStrategy(abc.ABC):

    @abc.abstractmethod
    def __init__(self, connection_uri: str, **pool_kwargs: Any) -> None:
        pass

    @property
    @abc.abstractmethod
    def executor(self) -> AbstractAsyncExecutor:
        pass

    @property
    @abc.abstractmethod
    def query_parser(self) -> AbstractQueryParser:
        pass

    @property
    @abc.abstractmethod
    def backend_adapter(self) -> AbstractBackendAdapter:
        pass

    @property
    @abc.abstractmethod
    def db(self) -> Any:
        pass

    @abc.abstractmethod
    async def execute_query(self, query: Any) -> Any:
        pass

    @abc.abstractmethod
    async def load(self) -> None:
        pass

    @abc.abstractmethod
    async def create_index(
            self, table_name: str,
            index_name: str, index_fields: List[str]) -> None:
        pass

    @abc.abstractmethod
    async def drop_index(self, table_name: str, index_name: str) -> None:
        pass

    @abc.abstractmethod
    async def list_indexes(self, table_name: str) -> List[str]:
        pass

    @abc.abstractmethod
    async def create_table(self, table_name: str) -> None:
        pass

    @abc.abstractmethod
    async def drop_table(self, table_name: str) -> None:
        pass

    @abc.abstractmethod
    async def truncate_table(self, table_name: str) -> None:
        pass

    @abc.abstractmethod
    async def list_tables(self) -> List[str]:
        pass

    async def ensure_tables(self, table_list: List[str]) -> None:
        exists_tables = await self.list_tables()
        coroutines_for_tables = [
            self.create_table(table)
            for table in table_list
            if table not in exists_tables
        ]
        if coroutines_for_tables:
            await asyncio.wait(coroutines_for_tables)

    async def ensure_indexes(self, table_name: str, table_models: List[Type['Model']]) -> None:
        current_index_list = await self.list_indexes(table_name)
        orm_required_indexes: List[Tuple[str, List[str]]] = []
        for table_model in table_models:
            indexes = table_model.build_index_list()
            if indexes:
                orm_required_indexes.extend(indexes)
        # Create new indexes
        # TODO: thinks about many awaiting coroutines, at least same as pool size
        for index_name, index_fields in orm_required_indexes:
            if index_name not in current_index_list:
                await self.create_index(
                    table_name, index_name,
                    [
                        self.backend_adapter.row_name_serialization(x)
                        for x in index_fields
                    ]
                )
                current_index_list.append(index_name)
        orm_required_indexes_name: List[str] = [x[0] for x in orm_required_indexes]
        for index in (
                index for index in current_index_list if index
                not in orm_required_indexes_name):
            await self.drop_index(table_name, index)

    @abc.abstractmethod
    async def close(self) -> None:
        pass


class AbstractSyncRegisterStrategy(abc.ABC):

    @abc.abstractmethod
    def __init__(self, connection_uri: str, **pool_kwargs: Any) -> None:
        pass

    @property
    @abc.abstractmethod
    def executor(self) -> AbstractSyncExecutor:
        pass

    @property
    @abc.abstractmethod
    def query_parser(self) -> AbstractQueryParser:
        pass

    @property
    @abc.abstractmethod
    def backend_adapter(self) -> AbstractBackendAdapter:
        pass

    @property
    @abc.abstractmethod
    def db(self) -> Any:
        pass

    @abc.abstractmethod
    def execute_query(self, query: Any) -> Any:
        pass

    @abc.abstractmethod
    def load(self) -> None:
        pass

    @abc.abstractmethod
    def create_index(
            self, table_name: str,
            index_name: str, index_fields: List[str]) -> None:
        pass

    @abc.abstractmethod
    def drop_index(self, table_name: str, index_name: str) -> None:
        pass

    @abc.abstractmethod
    def list_indexes(self, table_name: str) -> List[str]:
        pass

    @abc.abstractmethod
    def create_table(self, table_name: str) -> None:
        pass

    @abc.abstractmethod
    def drop_table(self, table_name: str) -> None:
        pass

    @abc.abstractmethod
    def truncate_table(self, table_name: str) -> None:
        pass

    @abc.abstractmethod
    def list_tables(self) -> List[str]:
        pass

    def ensure_tables(self, table_list: List[str]) -> None:
        exists_tables = self.list_tables()
        for table in table_list:
            if table not in exists_tables:
                self.create_table(table)

    def ensure_indexes(self, table_name: str, table_models: List[Type['Model']]) -> None:
        current_index_list = self.list_indexes(table_name)
        orm_required_indexes: List[Tuple[str, List[str]]] = []
        for table_model in table_models:
            indexes = table_model.build_index_list()
            if indexes:
                orm_required_indexes.extend(indexes)
        # Create new indexes
        for index_name, index_fields in orm_required_indexes:
            if index_name not in current_index_list:
                self.create_index(
                    table_name, index_name,
                    [
                        self.backend_adapter.row_name_serialization(x)
                        for x in index_fields
                    ]
                )
                current_index_list.append(index_name)
        orm_required_indexes_name: List[str] = [x[0] for x in orm_required_indexes]
        for index in (
                index for index in current_index_list if index
                not in orm_required_indexes_name):
            self.drop_index(table_name, index)

    @abc.abstractmethod
    def close(self) -> None:
        pass


class ORMRegister:  # pylint: disable=too-many-instance-attributes

    """
    Register object that store any information about models, tables.
    Store and control pool and wrap logic.
    """

    def __init__(self) -> None:
        super().__init__()
        self.async_loop: asyncio.AbstractEventLoop
        self.selected_protocol: RegistryProtocol
        self.tables: List[str] = []
        self.tables_model_link: Dict[str, List[Type['Model']]] = {}
        self.sync_strategy: AbstractSyncRegisterStrategy
        self.async_strategy: AbstractAsyncRegisterStrategy
        self.async_mode: bool = False
        self.shared = SharedEnv()
        self._extensions: List[BaseExtension] = []

    def init(self, connection_uri: str, pool_kwargs: Dict, async_mode: bool = False, extensions=None) -> None:
        self.async_mode = async_mode
        required_protocol = urlparse(connection_uri).scheme
        self.selected_protocol = RegistryProtocol.__members__.get(required_protocol, None)
        self._extensions.clear()
        if self.selected_protocol is None:
            raise ValueError(f"Cannot find implementation for {connection_uri}")

        if async_mode:
            self.async_strategy = import_class(
                self.selected_protocol.value.kwds['async_strategy']
            )(connection_uri, **pool_kwargs)
        else:
            self.sync_strategy = import_class(
                self.selected_protocol.value.kwds['sync_strategy']
            )(connection_uri, **pool_kwargs)
        if async_mode:
            self.shared.share('executor', self.async_strategy.executor)
            self.shared.share('query_parser', self.async_strategy.query_parser)
            self.shared.share('backend_adapter', self.async_strategy.backend_adapter)
        else:
            self.shared.share('executor', self.sync_strategy.executor)
            self.shared.share('query_parser', self.sync_strategy.query_parser)
            self.shared.share('backend_adapter', self.sync_strategy.backend_adapter)
        if extensions:
            for extension_type_name, extension_uri in extensions.items():
                extension_type = ExtensionType.__members__.get(extension_type_name, None)
                if extension_type is None:
                    raise ValueError(f'Cannot find extension {extension_type_name}')
                extension_type_protocols = import_class(extension_type.value)
                required_extensio_protocol = urlparse(extension_uri).scheme
                selected_extension_protocol = extension_type_protocols.__members__.get(required_extensio_protocol, None)
                if selected_extension_protocol is None:
                    raise ValueError(f'Cannot find protocol {selected_extension_protocol} for extension {extension_type_name}')
                selected_extension = import_class(selected_extension_protocol.value)(extension_uri)
                self._extensions.append(selected_extension)
                self.shared.share(f'{extension_type_name}_extension', selected_extension)

    def add_table(self, table: str, model_cls: Type['Model']):
        if table and (table not in self.tables):
            self.tables.append(table)
        self.tables_model_link.setdefault(table, []).append(model_cls)

    async def async_load(self, database_setup=True) -> None:
        await self.async_strategy.load()
        self.async_loop = asyncio.get_event_loop()
        if database_setup:
            await self.async_strategy.ensure_tables(self.tables)
            for table_name, table_models in self.tables_model_link.items():
                await self.async_strategy.ensure_indexes(table_name, table_models)
        for extension in self._extensions:
            await extension.async_load()

    def load(self, database_setup=True) -> None:
        self.sync_strategy.load()
        if database_setup:
            self.sync_strategy.ensure_tables(self.tables)
            for table_name, table_models in self.tables_model_link.items():
                self.sync_strategy.ensure_indexes(table_name, table_models)
        for extension in self._extensions:
            extension.load()

    def close(self) -> None:
        self.sync_strategy.close()

    @property
    def backend_adapter(self) -> 'AbstractBackendAdapter':
        try:
            return self.shared.backend_adapter
        except AttributeError:
            return DUMMY_ADAPTER

    async def async_close(self) -> None:
        await self.async_strategy.close()


orm_register = ORMRegister()  # pylint: disable=invalid-name
