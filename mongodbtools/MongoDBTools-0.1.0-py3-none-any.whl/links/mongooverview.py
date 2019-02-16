# **********************************************************************************
# * Project: Eskapade - A python-based package for data analysis                   *
# * Class  : MongoOverview                                                         *
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


class MongoOverview(Link):
    """
    Prints the names of all mongo collections and the number of all documents per collection
    """

    def __init__(self, name='MongoOverview'):
        """
        Store the configuration of link MongoOverview

        @param name Name given to the link
        """

        Link.__init__(self, name)

        return

    def initialize(self):
        """ Initialize MongoOverview """

        return StatusCode.Success

    def execute(self):
        """ Execute MongoOverview """

        process_manager.service(MongoConnection).set_config_info(process_manager.service(ConfigObject))
        self.mdb = process_manager.service(MongoConnection).database
        # check if collection names are in database
        colls = self.mdb.collection_names()

        self.logger.info('Number of collections found in mongo database: {count:d}', count=len(colls))
        for coll in sorted(colls):
            self.logger.info('    Collection <{collection}> contains: {count:d} records.',
                             collection=coll, count=self.mdb[coll].count())

        return StatusCode.Success

    def finalize(self):
        """ Finalizing MongoOverview """

        return StatusCode.Success
