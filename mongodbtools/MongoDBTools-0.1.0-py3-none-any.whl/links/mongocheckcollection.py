# **********************************************************************************
# * Project: Eskapade - A python-based package for data analysis                   *
# * Class  : MongoCheckCollection                                                  *
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


class MongoCheckCollection(Link):
    """
    Checks if all collections in the given collectionSet are present in the mongo database.
    """

    def __init__(self, name='MongoCheckCollection'):
        """
        Store the configuration of link MongoCheckCollection

        :param str name: name of link
        :param list collectionSet: the collections to be checked
        """

        Link.__init__(self, name)

        self.collectionSet = []
        return

    def initialize(self):
        """ Initialize MongoCheckCollection """

        return StatusCode.Success

    def execute(self):
        """ Execute MongoCheckCollection """

        process_manager.service(MongoConnection).set_config_info(process_manager.service(ConfigObject))
        self.mdb = process_manager.service(MongoConnection).database

        # check if collection names are in database
        all_colls = self.mdb.collection_names()
        for c in self.collectionSet:
            if c not in all_colls:
                raise Exception("%s is not a collection in the mongo database" % c)
        return StatusCode.Success

    def finalize(self):
        """ Finalizing MongoCheckCollection """

        return StatusCode.Success
