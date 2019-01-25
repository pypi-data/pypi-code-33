import json

from pymongo import MongoClient
from pymongo.cursor import Cursor

from kpc_nifi_utils.common.json_encoder import EnhancedJSONEncoder
from kpc_nifi_utils.parser.mongodb import MongoArgs


class MongoConnector:
    def __init__(self):
        self._args = MongoArgs()

    def get_db(self,
               host=None,
               port=None,
               document_class=dict,
               tz_aware=None,
               connect=None,
               **kwargs):
        client = MongoClient(host, port, document_class, tz_aware, connect, **kwargs)
        return client[self._args.get_db_name()]

    def parse_as_json(self, data):
        data_parse = data
        if isinstance(data, Cursor):
            data_parse = list(data)

        return json.dumps(list(data_parse), cls=EnhancedJSONEncoder)
