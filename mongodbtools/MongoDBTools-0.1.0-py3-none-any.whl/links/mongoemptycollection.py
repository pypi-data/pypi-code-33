# **********************************************************************************
# * Project: Eskapade - A python-based package for data analysis                   *
# * Class  : MongoEmptyTheCollection                                               *
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


class MongoEmptyTheCollection(Link):
    """
    Deletes data in mongo.
    """

    def __init__(self, name='MongoEmptyTheCollection'):
        """
        Store the configuration of link MongoEmptyTheCollection

        :param str name: name of link
        :param list collectionSet: mongo collection names to remove data from.
        :param dict fiterDict: pymongo filter for the data to be removed. If empty dict, all data in the collection(s)
            is removed.
        """

        Link.__init__(self, name)

        self.collectionSet = []
        self.filterDict = {}
        return

    def initialize(self):
        """ Initialize MongoEmptyTheCollection """

        return StatusCode.Success

    def execute(self):
        """ Execute MongoEmptyTheCollection """

        process_manager.service(MongoConnection).set_config_info(process_manager.service(ConfigObject))
        self.mdb = process_manager.service(MongoConnection).database

        # check if collection names are in database
        all_colls = self.mdb.collection_names()
        for c in self.collectionSet:
            if c not in all_colls:
                raise Exception("%s is not a collection in the mongo database" % c)
            try:
                if c in self.filterDict:
                    self.mdb[c].remove(self.filterDict[c])
                else:
                    self.mdb[c].remove({})
                self.logger.info('Emptied mongo collection <{collection}>.', collection=c)
            except:
                raise Exception('Deletion of mongo collection %s failed' % c)

        return StatusCode.Success

    def finalize(self):
        """ Finalizing MongoEmptyTheCollection """

        return StatusCode.Success
