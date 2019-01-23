from abc import ABC, abstractmethod
from nameko.extensions import DependencyProvider

from reliabilly.components.health import HealthProvider
from reliabilly.components.logger import log_exception
from reliabilly.settings import Constants


@log_exception
def get_query(**args):
    offset = int(get_request_arg(args, Constants.PAGE_OFFSET, Constants.DEFAULT_PAGE_OFFSET))
    limit = int(get_request_arg(args, Constants.PAGE_SIZE, Constants.DEFAULT_PAGE_SIZE))
    if limit > Constants.MAX_PAGE_SIZE:
        limit = Constants.MAX_PAGE_SIZE
    query = dict()
    for key, value in args.items():
        if key not in (Constants.PAGE_OFFSET, Constants.PAGE_SIZE):
            query[key] = value
    return offset, limit, query


@log_exception
def get_request_arg(args, key, default):
    arg = default
    read_arg = args.get(key, None)
    if read_arg:
        arg = read_arg
    return arg


class DataClient(ABC, HealthProvider):
    """ A data client interface to all supported data storage databases. """
    @abstractmethod
    def __init__(self, **kwargs):
        """ Initializer function with keyword arguments that likely vary based on implementation. """

    @abstractmethod
    def create(self, model):
        """ Create a new record in the data store. """

    @abstractmethod
    def update(self, key, model):
        """ Update a record in the data store. """

    @abstractmethod
    def get(self, key):
        """ Get a record by key from the data store. """

    @abstractmethod
    def get_all(self):
        """ Get all records from the data store. """

    @abstractmethod
    def filter(self, **kwargs):
        """ Get all records that match the filter criteria. """

    @abstractmethod
    def count(self):
        """ Get the count of records in the data store. """

    @abstractmethod
    def purge(self):
        """ Purge all records from the data store. """

    @abstractmethod
    def delete(self, key):
        """ Delete a specific record by key from the data store. """

    @abstractmethod
    def get_status(self):
        """ Get the status of the data store for health and connectivity. """

    def get_dependency(self, _):
        """ Return the dependency for nameko service dependency injection support. """
        return self
