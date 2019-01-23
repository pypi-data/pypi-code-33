import asyncpg
import threading
import json
import dateparser

from datetime import date, datetime
from collections import OrderedDict
from async_generator import asynccontextmanager
from longitude import config
from longitude.utils import allow_sync, datetime_to_utc, chain_fns

from .sql import SQLFetchable


class PostgresqlModel(SQLFetchable):

    def __init__(self, pool):
        # The connection has to be local because has to
        # be tied to the thread's event loop
        self.thead_locals = threading.local()
        self.thead_locals.pool = pool

    async def get_poll(self):

        # If the current thread has no conn, try to
        # create it from the current thread's event loop
        if not hasattr(self.thead_locals, 'pool'):
            self.thead_locals.pool = await self._create_pool()

        return self.thead_locals.pool

    @classmethod
    async def instantiate(cls):
        return cls(await cls._create_pool())

    @staticmethod
    async def _conn_init(conn):

        await conn.set_type_codec(
            'json',
            encoder=json.dumps,
            decoder=json.loads,
            schema='pg_catalog'
        )

        await conn.set_type_codec(
            'jsonb',
            encoder=json.dumps,
            decoder=json.loads,
            schema='pg_catalog'
        )

        await conn.set_type_codec(
            'timestamp',
            encoder=chain_fns(datetime_to_utc, str),
            decoder=dateparser.parse,
            schema='pg_catalog'
        )

        await conn.set_type_codec(
            'timestamptz',
            encoder=chain_fns(datetime_to_utc, str),
            decoder=dateparser.parse,
            schema='pg_catalog'
        )

        await conn.set_type_codec(
            'date',
            encoder=str,
            decoder=lambda x: date(*(int(x) for x in x.split('-'))),
            schema='pg_catalog'
        )

        return conn

    @classmethod
    async def _create_pool(cls):

        return await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            host=config.DB_HOST,
            port=config.DB_PORT,
            init=cls._conn_init,
            max_size=50
        )

    @asynccontextmanager
    async def get_conn(self):
        pool = await self.get_poll()
        conn = await pool.acquire(timeout=10)
        yield conn
        await pool.release(conn)

    @allow_sync
    async def fetch(self, *args, **kwargs):
        # TODO: allow the connection to be passed as
        # argument

        conn = kwargs.pop('conn', None)

        if conn is not None:
            res = await conn.fetch(*args, **kwargs)
        else:
            async with self.get_conn() as conn:
                res = await conn.fetch(*args, **kwargs)

        return [
            OrderedDict(x.items())
            for x
            in res
        ]
