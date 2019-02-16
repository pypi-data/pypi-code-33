# **********************************************************************************
# * Project: Eskapade - A python-based package for data analysis                   *
# * Class  : MongoMergeLabels                                                      *
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

from escore import process_manager, ConfigObject, Link, StatusCode
from mongodbtools import MongoConnection


class MongoMergeLabels(Link):
    """
    Defines the content of link MongoMergeLabels
    """

    def __init__(self, name='MongoMergeLabels'):
        """
        Store the configuration of link MongoMergeLabels

        :param str name: name of link
        :param str read_key: key of data to read from data store
        """

        Link.__init__(self, name)

        self.read_key = None

        self.input_collection = ''
        self.merge_collection = ''
        self.output_collection = ''

        self.inputIdKey = 'record_id'
        self.copyInputFields = ['label']
        self.mergeIdKey = '_id'

        self.deleteInputCollection = True
        return

    def initialize(self):
        """ Initialize MongoMergeLabels """

        process_manager.service(MongoConnection).set_config_info(process_manager.service(ConfigObject))
        self.mdb = process_manager.service(MongoConnection).database
        colls = self.mdb.collection_names()

        if self.input_collection not in colls:
            raise Exception("Input collection <%s> is not a collection in the mongo database" % self.input_collection)
        if self.merge_collection not in colls:
            raise Exception("Merge collection <%s> is not a collection in the mongo database" % self.merge_collection)
        if self.output_collection not in colls:
            raise Exception("Output collection <%s> is not a collection in the mongo database" % self.output_collection)

        return StatusCode.Success

    def execute(self):
        """ Execute MongoMergeLabels """

        from bson import objectid

        filter = {self.inputIdKey: 1}
        for key in self.copyInputFields:
            filter[key] = 1

        data = self.mdb[self.input_collection].find({}, filter)
        for event in data:
            record_id = event[self.inputIdKey]
            mongo_merge_id = objectid.ObjectId(record_id)
            doc = self.mdb[self.merge_collection].find_one({self.mergeIdKey: mongo_merge_id})
            if doc is None:
                self.logger.debug('Record with id <{id}> not found in merge collection <{collection}>. Skip.',
                                  id=record_id, collection=self.merge_collection)
                continue

            for key in self.copyInputFields:
                val = event[key]
                doc[key] = val

            self.mdb[self.output_collection].insert_one(doc)
            # if self.deleteInputCollection:
            #    self.mdb[self.input_collection].delete_one({self.inputIdKey: record_id})

        if self.deleteInputCollection:
            self.mdb[self.input_collection].remove({})
        return StatusCode.Success

    def finalize(self):
        """ Finalizing MongoMergeLabels """

        return StatusCode.Success
