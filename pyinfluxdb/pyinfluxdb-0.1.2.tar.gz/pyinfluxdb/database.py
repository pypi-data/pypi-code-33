"""
@Time    : 2019/1/16 17:31
@Author  : Sam
@Project : pyinfluxdb
@FileName: database.py
@Software: PyCharm
@Blog    : https://blog.muumlover.com
"""
import logging

import pytz

from pyinfluxdb import measurement

logger = logging.getLogger(__name__)


class Database(object):
    def __init__(self, client, name, **kwargs):
        self.__name = str(name)
        self.__client = client
        self.__kwargs = kwargs

        self._measurements_list = self.get_list_measurements()
        logger.debug(self._measurements_list)

        pass

    def get_list_measurements(self):
        """Get the list of measurements in InfluxDB.

        :returns: all measurements in InfluxDB
        :rtype: list of dictionaries

        :Example:

        ::

            >> dbs = client.get_list_measurements()
            >> dbs
            [{u'name': u'measurements1'},
             {u'name': u'measurements2'},
             {u'name': u'measurements3'}]
        """
        return list(self.query("SHOW MEASUREMENTS").get_points())

    def get_measurement(self, name):
        tz = pytz.timezone('Asia/Shanghai')
        return measurement.Measurement(self, name, timezone=tz)

    def query(self, *args, **kwargs):
        return self.__client.query(database=self.__name, *args, **kwargs)

    def write_points(self, *args, **kwargs):
        return self.__client.write_points(database=self.__name, *args, **kwargs)

    def __getattr__(self, name):
        """Get a collection of this database by name.

        Raises InvalidName if an invalid collection name is used.

        :rtype: Measurement
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

        :rtype: Measurement
        :Parameters:
          - `name`: the name of the database to get
        """
        return self.get_measurement(name)

    def __repr__(self):
        return "Database(%r, %r)" % (self.__client, self.__name)
