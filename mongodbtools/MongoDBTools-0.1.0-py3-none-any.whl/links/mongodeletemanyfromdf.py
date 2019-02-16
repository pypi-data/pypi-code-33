# **********************************************************************************
# * Project: Eskapade - A python-based package for data analysis                   *
# * Class  : MongoDeleteManyFromDF                                                 *
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

from escore import process_manager, ConfigObject, DataStore, Link, StatusCode
from mongodbtools import MongoConnection


class MongoDeleteManyFromDF(Link):
    """
    Deletes records in a mongo collection with the same bson.objectId.ObjectId as in the '_id' column of the
    pandas.DataFrame
    """

    def __init__(self, name='MongoDeleteManyFromDF'):
        """
        Store the configuration of link MongoDeleteManyFromDF

        :param str name: name of link
        :param str read_key: key of data to read from data store
        """

        Link.__init__(self, name)

        self.read_key = None

        return

    def initialize(self):
        """ Initialize MongoDeleteManyFromDF """

        process_manager.service(MongoConnection).set_config_info(process_manager.service(ConfigObject))
        self.mdb = process_manager.service(MongoConnection).database
        colls = self.mdb.collection_names()
        if self.read_key not in colls:
            raise Exception("%s is not a collection in the mongo database" % self.read_key)

        return StatusCode.Success

    def execute(self):
        """ Execute MongoDeleteManyFromDF """

        ds = process_manager.service(DataStore)
        df = ds[self.read_key]
        import bson

        if '_id' not in df.columns:
            raise Exception('No _id column in dataframe %s' % self.read_key)
        elif df._id.dtype != bson.objectid.ObjectId:
            raise Exception('_id column not of the correct type. Type should be bson.objectId.ObjectId')

        try:
            self.mdb[self.read_key].delete_many({'_id': {"$in": list(df._id)}})
        except:
            self.mdb[self.read_key].delete_many(({'_id': {"$in": list(df._id)}}))
            raise Exception('Deletion in collection tobeprocessed failed')

        return StatusCode.Success

    def finalize(self):
        """ Finalizing MongoDeleteManyFromDF """

        return StatusCode.Success
