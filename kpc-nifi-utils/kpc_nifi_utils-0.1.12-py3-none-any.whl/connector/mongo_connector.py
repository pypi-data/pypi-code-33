import json

from pymongo import MongoClient
from pymongo.cursor import Cursor

from kpc_nifi_utils.args.mongodb import MongoArgs
from kpc_nifi_utils.common.json_encoder import EnhancedJSONEncoder


class MongoConnector:
    def __init__(self, args: MongoArgs = None):
        if args is None:
            raise ValueError("MongoConnector could not init with null args.")

        self._args = args

    def get_db(self,
               host=None,
               port=None,
               document_class=dict,
               tz_aware=None,
               connect=None,
               **kwargs):

        if host is None:
            host = 'mongodb://{}/{}'.format(self._args.get_connection_string(), self._args.get_db_name())

        client = MongoClient(host,
                             port,
                             document_class,
                             tz_aware,
                             connect,
                             **kwargs)

        return client[self._args.get_db_name()]

    def parse_as_json(self, data):
        data_parse = data
        if isinstance(data, Cursor):
            data_parse = list(data)

        return json.dumps(list(data_parse), cls=EnhancedJSONEncoder)
