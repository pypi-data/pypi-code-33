from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from bson import ObjectId
from reliabilly.components.data import DataClient, get_query
from reliabilly.components.logger import Logger, log_exception
from reliabilly.components.models.base import BaseModel
from reliabilly.components.monitoring import monitor, MonitoringProvider
from reliabilly.settings import Constants, Settings


class MongoDataClient(DataClient):
    """ Data client for the mongodb nosql document data store. """

    def __init__(self, **kwargs):
        """ Initialization for mongodb with support for TDD. """
        super().__init__(**kwargs)
        self.db_name = Settings.MONGO_DB_NAME
        collection_name = kwargs.get(Constants.TABLE, Settings.SERVICE_NAME)
        self.host = kwargs.get(Constants.HOST, Settings.MONGO_URL)
        self.port = kwargs.get(Constants.PORT, Settings.MONGO_PORT)
        self.client = kwargs.get(Constants.CLIENT, MongoClient(self.host, self.port, serverSelectionTimeoutMS=20))
        self.collection = None
        self.logger = Logger()
        self.database = self.client[self.db_name]
        self._select_collection(collection_name)

    def get_health(self):
        try:
            return self.database.command(Constants.MONGO_STATS_COMMAND)
        except ServerSelectionTimeoutError:
            return {Constants.HEALTH: Constants.MONGO_CONNECTION_HEALTH_ERROR.format(host=self.host, port=self.port)}

    @log_exception
    def _select_collection(self, collection_name):
        collection = self.get_collection_name(collection_name)
        self.collection = self.client[self.db_name][collection]

    @log_exception
    def rename_table(self, old_name, new_name):
        self.logger.debug(f'Rename table called on data client. old: {old_name} new: {new_name}')
        self.database[old_name].rename(new_name, dropTarget=True)

    @log_exception
    def table_exists(self, table_name):
        self.logger.debug(f'Existence check on table: {table_name}')
        return table_name in self.database.collection_names()

    @log_exception
    @monitor(monitor_name=MonitoringProvider.get_monitor_prefix(Settings.SERVICE_NAME, 'mongo_create'))
    def create(self, model):
        if isinstance(model, BaseModel):
            model = model.__dict__
        result = self.collection.insert_one(model)
        return result.inserted_id is not None

    @log_exception
    def restore(self, data):
        self.logger.debug(f'Restoring data...')
        result = self.collection.insert_many(data)
        return result.inserted_ids is not None

    @log_exception
    @monitor(monitor_name=MonitoringProvider.get_monitor_prefix(Settings.SERVICE_NAME, 'mongo_get'))
    def get(self, key):
        self.logger.debug(f'Get item for id: {key}')
        return self.collection.find_one({Constants.DB_ID_KEY: ObjectId(key)})

    @log_exception
    @monitor(monitor_name=MonitoringProvider.get_monitor_prefix(Settings.SERVICE_NAME, 'mongo_update'))
    def update(self, key, model):
        self.logger.debug(f'Update item for id: {key}')
        if isinstance(model, BaseModel):
            model = model.__dict__
            model.pop(Constants.ID)
        return self.collection.find_one_and_replace({Constants.DB_ID_KEY: ObjectId(key)}, model, upsert=True)

    @log_exception
    @monitor(monitor_name=MonitoringProvider.get_monitor_prefix(Settings.SERVICE_NAME, 'mongo_get_specific'))
    def get_specific(self, id_value, collection):
        self.logger.debug(f'Get specific item for id: {id_value} from {collection}')
        self.collection = self.client[self.db_name][collection]
        return self.collection.find_one({Constants.DB_ID_KEY: id_value})

    @log_exception
    @monitor(monitor_name=MonitoringProvider.get_monitor_prefix(Settings.SERVICE_NAME, 'mongo_get_all'))
    def get_all(self):
        self.logger.debug(f'Get all called')
        return self.convert_cursor_to_array(self.collection.find())

    @log_exception
    @monitor(monitor_name=MonitoringProvider.get_monitor_prefix(Settings.SERVICE_NAME, 'mongo_find'))
    def find(self, key, value):
        self.logger.debug(f'Find called key: {key} val: {value}')
        return self.collection.find_one({key: value})

    @log_exception
    @monitor(monitor_name=MonitoringProvider.get_monitor_prefix(Settings.SERVICE_NAME, 'mongo_count'))
    def count(self):
        self.logger.debug('Count called')
        return self.collection.find().count(True)

    @log_exception
    @monitor(monitor_name=MonitoringProvider.get_monitor_prefix(Settings.SERVICE_NAME, 'mongo_purge'))
    def purge(self):
        self.logger.debug('Purge called')
        return self.collection.drop()

    @log_exception
    @monitor(monitor_name=MonitoringProvider.get_monitor_prefix(Settings.SERVICE_NAME, 'mongo_read'))
    def read(self, offset, limit, query):
        self.logger.debug(f'Read called offset: {offset} limit: {limit} query: {query}')
        count = self.collection.find(query).count()
        cursor = self.collection.find(query).skip(offset).limit(limit)
        return self.convert_cursor_to_array(cursor), offset, limit, count

    @log_exception
    @monitor(monitor_name=MonitoringProvider.get_monitor_prefix(
        Settings.SERVICE_NAME, 'mongo_delete'))
    def delete(self, key):
        self.logger.debug(f'Delete called id: {key}')
        result = self.collection.delete_one({Constants.DB_ID_KEY: ObjectId(key)})
        return result.deleted_count == 1

    @log_exception
    def delete_db(self):
        self.logger.debug('Drop db called.')
        self.client.drop_database(self.db_name)

    @log_exception
    def get_server_info(self):
        self.logger.debug('Queries DB for server info')
        return self.client.server_info()

    @staticmethod
    def convert_cursor_to_array(cursor):
        documents = []
        if cursor is not None:
            for document in cursor:
                documents.append(document)
        return documents

    @staticmethod
    def get_collection_name(model):
        if model:
            if isinstance(model, str):
                return model
            return model.__name__
        return 'not_set'

    def get_status(self):
        pass

    def filter(self, **kwargs):
        offset, limit, query = get_query(**kwargs)
        return self.read(offset, limit, query)
