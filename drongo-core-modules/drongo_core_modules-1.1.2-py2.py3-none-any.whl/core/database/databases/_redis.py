import redis

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 6379
DEFAULT_DB = 0


class RedisDatabase(object):
    def __init__(self, app, config):
        # TODO: connection parameters
        uri = config.get('uri')
        host = config.get('host', DEFAULT_HOST)
        port = config.get('port', DEFAULT_PORT)
        db = config.get('db', DEFAULT_DB)

        if uri:
            client = redis.from_url(uri, db=db)
        else:
            client = redis.Redis(host=host, port=port, db=db)

        self.db = client

    def get(self):
        return self.db
