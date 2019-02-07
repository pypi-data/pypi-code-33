#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/dhardy92/thumbor_hbase/

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license

from cassandra.cluster import Cluster
from tornado.concurrent import return_future


def __conn__(context):
    cluster = Cluster([context.config.CASSANDRA_LOADER_SERVER_HOST],
                      port=context.config.CASSANDRA_LOADER_SERVER_PORT)
    session = cluster.connect()
    session.set_keyspace(context.config.CASSANDRA_LOADER_KEYSPACE)

    return session


@return_future
def load(context, url, callback):
    try:
        session = __conn__(context)
        image_id = url.split('/')[-1]
        query = context.config.CASSANDRA_LOADER_QUERY.format(context.config.CASSANDRA_LOADER_TABLE_NAME,
                                                             context.config.CASSANDRA_LOADER_TABLE_ID_COLUMN)
        rows = session.execute(query, [image_id])
        if not rows:
            callback(None)
        else:
            func = getattr(rows[0], context.config.CASSANDRA_LOADER_TABLE_BLOB_COLUMN)
            callback(func)
    except (KeyError, TypeError, AttributeError):
        callback(None)
