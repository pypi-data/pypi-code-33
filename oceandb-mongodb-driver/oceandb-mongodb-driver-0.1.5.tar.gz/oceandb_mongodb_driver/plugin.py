"""Implementation of OceanDB plugin based in MongoDB"""
import logging

from oceandb_driver_interface.plugin import AbstractPlugin
from oceandb_driver_interface.search_model import FullTextModel, QueryModel
from pymongo import DESCENDING

from oceandb_mongodb_driver.instance import get_database_instance
from oceandb_mongodb_driver.utils import query_parser

logger = logging.getLogger(__name__)


class Plugin(AbstractPlugin):
    """Mongo ledger plugin for `Ocean DB's Python reference
    implementation <https://github.com/oceanprotocol/oceandb-mongo-driver>`_.
    Plugs in a MongoDB instance as the persistence layer for Ocean Db
    related actions.
    """

    def __init__(self, config=None):
        """Initialize a :class:`~.Plugin` instance and connect to MongoDB.
        Args:
            *nodes (str): One or more URLs of MongoDB nodes to
                connect to as the persistence layer
        """
        self.driver = get_database_instance(config)
        self.logger = logging.getLogger('Plugin')
        logging.basicConfig(level=logging.INFO)

    @property
    def type(self):
        """str: the type of this plugin (``'MongoDB'``)"""
        return 'MongoDB'

    def write(self, obj, resource_id=None):
        if resource_id is not None:
            obj['_id'] = resource_id
        o = self.driver.instance.insert_one(obj)
        self.logger.debug('mongo::write::{}'.format(o.inserted_id))
        return o.inserted_id

    def read(self, resource_id):
        return self.driver.instance.find_one({"_id": resource_id})

    def update(self, obj, resource_id):
        prev = self.read(resource_id)
        self.logger.debug('mongo::update::{}'.format(resource_id))
        return self.driver.instance.replace_one(prev, obj)

    def delete(self, resource_id):
        self.logger.debug('mongo::delete::{}'.format(resource_id))
        return self.driver.instance.delete_one({"_id": resource_id})

    def list(self, search_from=None, search_to=None, limit=0):
        return self.driver.instance.find().limit(limit)

    def query(self, search_model: QueryModel):
        if search_model.sort is None:
            return self.driver.instance.find(query_parser(search_model.query)).sort(
                [('service.metadata.curation.rating', DESCENDING)]).skip(
                search_model.page * search_model.offset) \
                .limit(search_model.offset)
        else:
            return self.driver.instance.find(query_parser(search_model.query)).sort(
                list(search_model.sort.items())).skip(
                search_model.page * search_model.offset) \
                .limit(search_model.offset)

    def text_query(self, full_text_model: FullTextModel):
        if full_text_model.sort is None:
            return self.driver.instance.find({"$text": {"$search": full_text_model.text}}).sort(
                [('service.metadata.curation.rating', DESCENDING)]).skip(
                full_text_model.page * full_text_model.offset) \
                .limit(full_text_model.offset)
        else:
            return self.driver.instance.find({"$text": {"$search": full_text_model.text}}).sort(
                list(full_text_model.sort.items())).skip(
                full_text_model.page * full_text_model.offset) \
                .limit(full_text_model.offset)
