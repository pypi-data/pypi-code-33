import pymongo
import socket

from escore.core.dbconnection import DbConnection
from mongodbtools import resources


class MongoConnection(DbConnection):
    """Process service for managing a Mongo connection"""

    def __init__(self, config_path=resources.config('mongo.cfg'), config_section='mongo', init_colls=None):
        """Initialize Mongo connection instance"""

        DbConnection.__init__(self, config_path=config_path, config_section=config_section)

        self._database = None
        self._init_colls = set()
        if init_colls:
            self.init_colls = init_colls

    def __del__(self):
        """ destructor """
        if self._conn is not None:
            self.close()

    @property
    def init_colls(self):
        """Initial columns in database"""

        return set(self._init_colls)

    @init_colls.setter
    def init_colls(self, colls):
        """Set initial columns in database"""

        try:
            self._init_colls = set(colls)
        except TypeError as exc:
            self.logger.fatal('Unable to set initial database columns.')
            raise exc

    def set_config_info(self, settings):
        """Extract config info from settings"""

        # get config file path
        path = settings.get('mongodb')
        if not path:
            raise RuntimeError('MongoDB config path not found in settings ("mongodb").')
        self.config_path = path

        # get config section
        sec = 'test' if settings.get('TESTING') else 'mongo'
        self.config_section = sec

        # get initial database columns
        init_colls = settings.get('all_mongo_collections', set())
        if init_colls:
            self.init_colls = init_colls

    def create_connection(self):
        """Create Mongo connection instance"""

        if self._conn:
            raise RuntimeError('Mongo connection already exists.')

        # get configuration
        cfg = self.get_config()

        # get connection properties
        uri = cfg.get(self.config_section, 'url')
        port = int(cfg.get(self.config_section, 'port'))

        # test if connection can be made
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        if sock.connect_ex((uri, port)) != 0:
            self.logger.fatal('Unable to open Mongo connection to {uri} on port {port}.', uri=uri, port=port)
            raise RuntimeError('Failed to open Mongo connection.')

        # create connection
        self._conn = pymongo.MongoClient(uri, port)

    @property
    def database(self):
        """Connection to database"""

        if not self._database:
            # get configuration
            cfg = self.get_config()

            # get database properties
            db_name = cfg.get(self.config_section, 'database')
            user = cfg.get(self.config_section, 'username')
            pwd = cfg.get(self.config_section, 'password')

            # authenticate to database
            self._database = self.connection[db_name]
            if user and pwd:
                self._database.authenticate(user, pwd)

            # create initial collections
            colls = self._database.collection_names()
            for coll in self.init_colls:
                if coll not in colls:
                    self._database.create_collection(coll)

        return self._database

    def close(self):
        """Close Mongo connection"""

        if not self._conn:
            raise RuntimeError('Not connected to any database.')
        self.logger.debug('Closing Mongo connection {address}.', address=self._conn.address)
        self._conn.close()
