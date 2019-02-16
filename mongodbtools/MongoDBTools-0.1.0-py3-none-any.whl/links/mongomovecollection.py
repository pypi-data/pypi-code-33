# **********************************************************************************
# * Project: Eskapade - A python-based package for data analysis                   *
# * Class  : MongoMoveCollection                                                   *
# * Created: 2016/11/08                                                            *
# * Description:                                                                   *
# *      Algorithm to do...(fill in here)                                          *
# *                                                                                *
# * Authors:                                                                       *
# *      KPMG Big Data team, Amstelveen, The Netherlands                           *
# *                                                                                *
# * Redistribution and use in source and binary forms, with or without             *
# * modification, are permitted according to the terms listed in the file          *
# * LICENSE.                                                                       *
# **********************************************************************************

import pandas as pd

from escore import process_manager, ConfigObject, DataStore, Link, StatusCode
from mongodbtools import MongoConnection


class MongoMoveCollection(Link):
    """
    Moves data from a mongo source collection to one or more mongo target collections.
    """

    def __init__(self, name='mongoCollectionMover'):
        """
        Store the configuration of link MongoMoveCollection

        :param str name: name of link
        :param str source_collection: mongo collection name of the source collection
        :param list target_collections: mongo collection name(s) of the target collecion(s)
        :param dict columnsToAdd: columns to add to the pandas.DataFrame before storage. key = column name,
            value = column value
        :param dict filter: pymongo filter for the query on the source collection
        :param bool copy: if True data in the source collection will not be removed
        """

        Link.__init__(self, name)

        self.source_collection = None
        self.target_collections = []
        self.columnsToAdd = None
        self.filter = None
        self.copy = False

        return

    def initialize(self):
        """ Initialize MongoMoveCollection """

        if self.filter is not None:
            self.logger.debug('Applying filter: {filter!s}.', filter=self.filter)

        return StatusCode.Success

    def execute(self):
        """ Execute MongoMoveCollection """

        process_manager.service(MongoConnection).set_config_info(process_manager.service(ConfigObject))
        self.mdb = process_manager.service(MongoConnection).database
        # check if collection names are in database
        colls = self.mdb.collection_names()
        if self.source_collection not in colls:
            raise Exception("%s is not a collection in the mongo database" % self.source_collection)

        if self.filter is not None:
            if isinstance(self.filter, dict):
                pass
            elif isinstance(self.filter, str):
                ds = process_manager.service(DataStore)
                assert self.filter in ds, 'Filter key <%s> not found in datastore.' % self.filter
                self.filter = ds[self.filter]
                assert isinstance(self.filter, dict), 'Filter with key <%s> is not a dict.' % self.filter
            else:
                raise Exception('Given filter of incorrect type.')

        if self.filter is not None:
            data = self.mdb[self.source_collection].find(self.filter)
        else:
            data = self.mdb[self.source_collection].find()
        df = pd.DataFrame(list(data))

        if len(df) == 0:
            self.logger.info('Source collection <{collection}> has zero length. Nothing to move.',
                                collection=self.source_collection)
            return StatusCode.Success

        if self.columnsToAdd is not None:
            for k, v in self.columnsToAdd.items():
                df[k] = v
        docs = list(df.T.to_dict().values())

        s = []
        for coll in self.target_collections:
            try:
                self.mdb[coll].insert_many(docs)
                s.append(coll)
                appliedstr = 'Copied' if self.copy else 'Moved'
                self.logger.info('{action} collection <{collection}> with length <{length}> to <{target}>.',
                                 action=appliedstr, collection=self.source_collection, length=len(docs), target=coll)
            except:
                for c in s:
                    self.mdb[c].delete_many(({'_id': {"$in": list(df._id)}}))
                raise Exception('Error in move: insertion in target collection %s failed' % coll)

        if not self.copy:
            try:
                self.mdb[self.source_collection].delete_many({'_id': {"$in": list(df._id)}})
            except:
                for c in s:
                    self.mdb[c].delete_many(({'_id': {"$in": list(df._id)}}))
                raise Exception('Error in move: deletion from source collection %s failed' % self.source_collection)

        return StatusCode.Success

    def finalize(self):
        """ Finalizing MongoMoveCollection """

        return StatusCode.Success
