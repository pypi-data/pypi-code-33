from datetime import datetime

from reliabilly.components.data.mongo_client import MongoDataClient
from reliabilly.settings import Constants


class CollectionManager:

    def __init__(self, **kwargs):
        self.id_key = kwargs.get(Constants.ID, Constants.DB_ID_KEY)
        self.data_client = kwargs.get(Constants.CLIENT, MongoDataClient(table=Constants.COLLECTION_MANAGER_TABLE))

    def is_collection_running(self, collector_name):
        doc = self.get_collection_record(collector_name)
        if doc:
            if doc[Constants.COLLECTION_STATUS_KEY] != Constants.COLLECTION_STARTED_STATUS:
                self.data_client.delete(doc[self.id_key])
                return False
            return True
        return False

    def collection_started(self, collector_name):
        return self.data_client.create(
            {Constants.NAME: collector_name,
             Constants.STARTED: str(datetime.now()),
             Constants.COLLECTION_STATUS_KEY: Constants.COLLECTION_STARTED_STATUS})

    def collection_completed(self, collector_name, success=False):
        collection_doc = self.get_collection_record(collector_name)
        status = Constants.COLLECTION_FAILED_STATUS
        if success:
            status = Constants.COLLECTION_SUCCESS_STATUS
        self.data_client.delete(collection_doc[self.id_key])
        return self.data_client.create(
            {Constants.NAME: collector_name,
             Constants.STARTED: collection_doc[Constants.STARTED],
             Constants.COMPLETED: str(datetime.now()),
             Constants.COLLECTION_STATUS_KEY: status})

    def get_collection_status(self, collector_name):
        status = self.get_collection_record(collector_name)
        if status:
            if status[Constants.COLLECTION_STATUS_KEY] != Constants.COLLECTION_STARTED_STATUS:
                self.data_client.delete(status[self.id_key])
            return status
        return None

    def get_collection_record(self, collector_name):
        doc = self.data_client.find(Constants.NAME, collector_name)
        if isinstance(doc, list):
            if doc:
                return doc[0]
            return None
        return doc

    def purge_prior_collections(self):
        return self.data_client.purge()
