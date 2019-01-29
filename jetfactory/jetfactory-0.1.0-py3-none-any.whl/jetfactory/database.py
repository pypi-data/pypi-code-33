# -*- coding: utf-8 -*-

from peewee_async import Manager, PooledMySQLDatabase, PooledPostgresqlDatabase
from urllib.parse import urlparse, parse_qs


class Database:
    connection: PooledPostgresqlDatabase
    manager: Manager

    @classmethod
    def register(cls, app, loop):
        db_url = app.config.get('DB_URL')
        if not db_url:
            return

        cls.connection = cls._create_connection(db_url)
        cls.connection.allow_sync = False
        cls.manager = Manager(cls.connection, loop=loop)

    @classmethod
    def _create_connection(cls, url):
        parsed = urlparse(url)

        if parsed.scheme == 'postgres':
            interface = PooledPostgresqlDatabase
        elif parsed.scheme == 'mysql':
            interface = PooledMySQLDatabase
        else:
            raise Exception(f'Database URL scheme must be "mysql" or "postgres", '
                            f'example: postgres://user:pass@127.0.0.1/database')

        params = parse_qs(parsed.query)
        pool_min = params.pop('pool_min', [5])[0]
        pool_max = params.pop('pool_max', [50])[0]

        settings = dict(
            database=parsed.path.lstrip('/'),
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port,
            min_connections=int(pool_min),
            max_connections=int(pool_max),
        )

        return interface(**settings)
