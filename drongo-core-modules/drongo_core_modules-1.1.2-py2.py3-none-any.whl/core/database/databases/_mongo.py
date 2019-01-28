import pymongo

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 27017


class MongoDatabase(object):
    def __init__(self, app, config):
        # TODO: connection parameters
        uri = config.get('uri')
        host = config.get('host', DEFAULT_HOST)
        port = config.get('port', DEFAULT_PORT)
        name = config.get('name')
        if uri:
            client = pymongo.MongoClient(uri)
        else:
            client = pymongo.MongoClient(host, port)

        self.db = client[name]

    def get(self, collection=None):
        if collection is None:
            return self.db
        else:
            return self.db[collection]

    def get_collection(self, name):
        return self.db[name]
