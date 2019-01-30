from typing import List, Any
import logging
from datetime import datetime

import rethinkdb as R

from ..core import (
    AbstractSyncRegisterStrategy, AbstractAsyncRegisterStrategy,
    AbstractAsyncExecutor, AbstractSyncExecutor, AbstractQueryParser, AbstractBackendAdapter,
    compitability
)
from .executor import RethinkDBAsyncExecutor, RethinkDBSyncExecutor
from .parser import RethinkDBQueryParser
from .utils import parse_rethinkdb_connection_uri

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.2"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ["SyncRethinkDBRegisterStrategy", "AsyncRethinkDBRegisterStrategy", "RethinkDBBackendAdapter"]

_log = logging.getLogger(__name__)


class RethinkDBBackendAdapter(AbstractBackendAdapter):

    @compitability(target_type=datetime)  # type: ignore
    def datetime_compitability(self, value):  # pylint: disable=no-self-use
        if not isinstance(value.tzinfo, R.ast.RqlTzinfo):
            if value.tzinfo is None:
                value = value.astimezone(R.make_timezone("00:00"))
            else:
                isoformat = value.isoformat(timespec='microseconds')
                if ':' in isoformat[-5:]:
                    value = value.astimezone(R.make_timezone(isoformat[-5:]))
                else:
                    value = value.astimezone(R.make_timezone("00:00"))
        return value.replace(microsecond=0)


class SyncRethinkDBRegisterStrategy(AbstractSyncRegisterStrategy):

    def __init__(self, connection_uri: str, **pool_kwargs: Any) -> None:  # pylint: disable=super-init-not-called
        from repool_forked import ConnectionPool

        self._connection_kwargs = parse_rethinkdb_connection_uri(connection_uri)
        self.pool = ConnectionPool(
            self._connection_kwargs,
            **pool_kwargs
        )
        self._executor = RethinkDBSyncExecutor(self)
        self._query_parser = RethinkDBQueryParser()
        self._backend_adapter = RethinkDBBackendAdapter()

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
        return self.pool

    def execute_query(self, query: Any) -> Any:
        looped_mode = isinstance(query, R.ast.Changes)
        with self.pool.connect(looped_mode=looped_mode) as conn:
            return query.run(conn)

    def load(self) -> None:
        self.pool.init_pool()
        with self.pool.connect() as conn:
            current_database = self._connection_kwargs.get('db', 'test')
            db_list = R.db_list().run(conn)
            if current_database not in db_list:
                R.db_create(current_database).run(conn)

    def create_index(
            self, table_name: str,
            index_name: str, index_fields: List[str]) -> None:
        if len(index_fields) == 1:
            with self.pool.connect() as conn:
                R.table(table_name).index_create(index_fields[0]).run(conn)
                R.table(table_name).index_wait(index_fields[0]).run(conn)
        else:
            with self.pool.connect() as conn:
                R.table(table_name).index_create(
                    index_name,
                    [R.row[x] for x in index_fields]).run(conn)
                R.table(table_name).index_wait(index_name).run(conn)

    def drop_index(self, table_name: str, index_name: str) -> None:
        with self.pool.connect() as conn:
            R.table(table_name).index_drop(index_name).run(conn)

    def list_indexes(self, table_name: str) -> List[str]:
        with self.pool.connect() as conn:
            return R.table(table_name).index_list().run(conn)

    def create_table(self, table_name: str) -> None:
        with self.pool.connect() as conn:
            R.table_create(table_name).run(conn)

    def drop_table(self, table_name: str) -> None:
        with self.pool.connect() as conn:
            R.table_drop(table_name).run(conn)

    def truncate_table(self, table_name: str) -> None:
        with self.pool.connect() as conn:
            R.table(table_name).delete().run(conn)

    def list_tables(self) -> List[str]:
        with self.pool.connect() as conn:
            return R.table_list().run(conn)

    def close(self) -> None:
        self.pool.release_pool()


class AsyncRethinkDBRegisterStrategy(AbstractAsyncRegisterStrategy):

    def __init__(self, connection_uri: str, **pool_kwargs: Any) -> None:  # pylint: disable=super-init-not-called
        from async_repool import AsyncConnectionPool

        self._connection_kwargs = parse_rethinkdb_connection_uri(connection_uri)
        self.pool = AsyncConnectionPool(
            self._connection_kwargs,
            **pool_kwargs
        )
        self._executor = RethinkDBAsyncExecutor(self)
        self._query_parser = RethinkDBQueryParser()
        self._backend_adapter = RethinkDBBackendAdapter()

        R.set_loop_type('asyncio')

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
        return self.pool

    async def execute_query(self, query: Any) -> Any:
        looped_mode = isinstance(query, R.ast.Changes)
        async with self.pool.connect(looped_mode=looped_mode) as conn:
            return await query.run(conn)

    async def load(self) -> None:
        await self.pool.init_pool()
        async with self.pool.connect() as conn:
            current_database = self._connection_kwargs.get('db', 'test')
            db_list = await R.db_list().run(conn)
            if current_database not in db_list:
                await R.db_create(current_database).run(conn)

    async def create_index(
            self, table_name: str,
            index_name: str, index_fields: List[str]) -> None:
        async with self.pool.connect() as conn:
            if len(index_fields) == 1:
                index_name = index_fields[0]
                await R.table(table_name).index_create(index_fields[0]).run(conn)
            else:
                await R.table(table_name).index_create(
                    index_name, [R.row[x] for x in index_fields]
                ).run(conn)
            await R.table(table_name).index_wait(index_name).run(conn)

    async def drop_index(self, table_name: str, index_name: str) -> None:
        async with self.pool.connect() as conn:
            await R.table(table_name).index_drop(index_name).run(conn)

    async def list_indexes(self, table_name: str) -> List[str]:
        async with self.pool.connect() as conn:
            return await R.table(table_name).index_list().run(conn)

    async def create_table(self, table_name: str) -> None:
        async with self.pool.connect() as conn:
            await R.table_create(table_name).run(conn)

    async def drop_table(self, table_name: str) -> None:
        async with self.pool.connect() as conn:
            await R.table_drop(table_name).run(conn)

    async def truncate_table(self, table_name: str) -> None:
        async with self.pool.connect() as conn:
            await R.table(table_name).delete().run(conn)

    async def list_tables(self) -> List[str]:
        async with self.pool.connect() as conn:
            return await R.table_list().run(conn)

    async def close(self) -> None:
        await self.pool.release_pool()
