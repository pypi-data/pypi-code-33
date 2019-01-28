from peewee import PostgresqlDatabase

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 5432


class PostgresDatabase(object):
    def __init__(self, app, config):
        host = config.get('host', DEFAULT_HOST)
        port = config.get('port', DEFAULT_PORT)
        user = config.get('user')
        password = config.get('password')
        name = config.get('name')

        self.connection = PostgresqlDatabase(
            host=host,
            port=port,
            user=user,
            password=password,
            database=name
        )
        self.connection.connect()

    def get(self):
        return self.connection
