"""Project: Eskapade - A python-based package for data analysis.

Created: 2017-08-08

Description:
    Collection of eskapade entry points

Authors:
    KPMG Advanced Analytics & Big Data team, Amstelveen, The Netherlands

Redistribution and use in source and binary forms, with or without
modification, are permitted according to the terms listed in the file
LICENSE.
"""

import os

from escore.logger import LogLevel, Logger, global_log_publisher, ConsoleHandler, ConsoleErrHandler

publisher = global_log_publisher
publisher.log_level = LogLevel.INFO
publisher.add_handler(ConsoleHandler())
publisher.add_handler(ConsoleErrHandler())

logger = Logger(__name__)

def mongo_reset_collections():

    import argparse

    from escore import process_manager, ConfigObject
    from escore.core import persistence
    from mongodbtools import resources
    from mongodbtools import MongoConnection

    parser = argparse.ArgumentParser('eskapade_mongo_reset_collections',
                                     description='Clean MongoDB collections.',
                                     epilog='Please note, only the collections \'proxy\' and \'roles\' will be kept.')
    parser.add_argument('--config', '-c', nargs='?', help='Path to custom MongoDB configuration file.')
    args = parser.parse_args()

    path = resources.config('mongo.cfg')
    if args.config and os.path.exists(args.config):
        path = args.config
    logger.info('Using MongoDB configuration from {path:s}'.format(path=path))

    settings = process_manager.service(ConfigObject)
    settings['analysisName'] = 'mongo_reset_collections'
    settings['version'] = 0

    settings['mongodb'] = resources.config('mongo.cfg')

    # Assert if the results are written to mongo
    process_manager.service(MongoConnection).set_config_info(settings)
    mdb = process_manager.service(MongoConnection).database

    # --- these collections you should keep (authorization data/proxy service)
    col_keep = ['proxy', 'roles']

    col_names = mdb.collection_names(False)
    for name in col_names:
        if mdb[name].name not in col_keep:
            mdb[name].remove({})
            mdb.drop_collection(name)

    logger.info('Cleared all MongoDB collections (except {cols})'.format(cols=col_keep))
