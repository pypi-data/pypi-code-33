#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license

from ._version import __version__

# CASSANDRA LOADER OPTIONS
from thumbor.config import Config
Config.define('CASSANDRA_LOADER_SERVER_HOST', 'localhost', 'Cassandra cluster Host for Loader', 'Cassandra Loader')
Config.define('CASSANDRA_LOADER_SERVER_PORT', 9042, 'Cassandra cluster Port for Loader', 'Cassandra Loader')
Config.define('CASSANDRA_LOADER_KEYSPACE', 'general', 'Cassandra cluster Keyspace for Loader', 'Cassandra Loader')
Config.define('CASSANDRA_LOADER_TABLE_NAME', 'images', 'Cassandra cluster reachable Tables for Loader', 'Cassandra Loader')
Config.define('CASSANDRA_LOADER_TABLE_ID_COLUMN', 'image_id', 'Cassandra cluster reachable Tables for Loader', 'Cassandra Loader')
Config.define('CASSANDRA_LOADER_TABLE_BLOB_COLUMN', "image_data", 'Cassandra cluster reachable Tables for Loader', 'Cassandra Loader')
Config.define('CASSANDRA_LOADER_QUERY', 'SELECT * FROM {0} WHERE {1}=%s', 'Cassandra cluster reachable Tables for Loader', 'Cassandra Loader')
