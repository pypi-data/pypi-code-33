"""
@Time    : 2019/1/16 17:29
@Author  : Sam
@Project : pyinfluxdb
@FileName: client.py
@Software: PyCharm
@Blog    : https://blog.muumlover.com
"""
import logging

from influxdb import InfluxDBClient

from pyinfluxdb import database
from pyinfluxdb.errors import ConfigurationError

logger = logging.getLogger(__name__)


class InfluxClient(InfluxDBClient):
    def __init__(self,
                 host='localhost',
                 port=8086,
                 username='root',
                 password='root',
                 timeout=10,
                 timezone='Asia/Shanghai',
                 **kwargs
                 ):

        super().__init__(host, port, username, password, timeout=timeout, **kwargs)
        self.__host = host
        self.__port = int(port)
        self.__username = username
        self.__password = password
        self.__timeout = timeout
        self.__timezone = timezone
        self.__kwargs = kwargs

        self._database_list = self.get_list_database()
        logger.debug(self._database_list)

    def get_database(self, name):
        if name is None:
            if self.__default_database_name is None:
                raise ConfigurationError('No default database defined')
            name = self.__default_database_name
        return database.Database(
            self, name, **self.__kwargs)

    def __getattr__(self, name):
        """Get a collection of this database by name.

        Raises InvalidName if an invalid collection name is used.

        :rtype: Database
        :Parameters:
          - `name`: the name of the collection to get
        """
        if name.startswith('_'):
            raise AttributeError(
                "Database has no attribute %r. To access the %s"
                " collection, use database[%r]." % (name, name, name))
        return self.__getitem__(name)

    def __getitem__(self, name):
        """Get a database by name.

        Raises :class:`~pymongo.errors.InvalidName` if an invalid
        database name is used.

        :rtype: Database
        :Parameters:
          - `name`: the name of the database to get
        """
        if {'name': name} not in self._database_list:
            self.create_database(name)
        return self.get_database(name)

    def _repr_helper(self):
        # Host first...
        options = ['host=%s:%d' % (self.__host, self.__port)]
        return ', '.join(options)

    def __repr__(self):
        return "InfluxClient(%s)" % (self._repr_helper(),)
