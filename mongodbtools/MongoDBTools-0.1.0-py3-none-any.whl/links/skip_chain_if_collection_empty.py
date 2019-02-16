# **********************************************************************************
# * Project: Eskapade - A python-based package for data analysis                   *
# * Class  : SkipChainIfCollectionEmpty                                            *
# * Created: 2017/02/27                                                            *
# * Description:                                                                   *
# *      Algorithm to skip to the next Chain if input dataset is empty             *
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


class SkipChainIfCollectionEmpty(Link):
    """
    Sents a SkipChain deenums.StatusCode signal when an appointed dataset is empty.

    This signal causes that the processsManager to step immediately to the next Chain.
    Input collections can be either mongo collections or dataframes in the datastore.
    """

    def __init__(self, **kwargs):
        """
        Skip to the next Chain if any of the input dataset is empty.

        :param str name: name of link
        :param list collectionSet: datastore keys holding the datasets to be checked. If any of these is empty,
            the chain is skipped.
        :param filterDict: filter to be applied on a mongo dataset (optional)
        :param bool skip_chain_when_key_not_in_ds: skip the chain as well if the dataframe is not present in
            the datastore. When True and if type is 'pandas.DataFrame', sents a SkipChain
            signal if key not in DataStore
        :param bool checkAtInitialize: perform dataset empty is check at initialize. Default is true.
        :param bool checkAtExecute: perform dataset empty is check at initialize. Default is false.
        """

        Link.__init__(self, kwargs.pop('name', 'SkipChainIfCollectionEmpty'))

        # process keyword arguments
        self._process_kwargs(kwargs, collectionSet=[], filterDict={}, skip_chain_when_key_not_in_ds=False,
                             checkAtInitialize=True, checkAtExecute=False)
        self.check_extra_kwargs(kwargs)

        return

    def initialize(self):
        """ Initialize SkipChainIfCollectionEmpty """

        mongo_conn = process_manager.service(MongoConnection)
        mongo_conn.set_config_info(process_manager.service(ConfigObject))
        self.mdb = mongo_conn.database

        if self.checkAtInitialize:
            return self.checkCollectionSet()

        return StatusCode.Success

    def execute(self):
        """ Execute SkipChainIfCollectionEmpty """

        if self.checkAtExecute:
            return self.checkCollectionSet()

        return StatusCode.Success

    def checkCollectionSet(self):
        """
        Check existence of collection in either mongo or datastore, and check that they are not empty.

        Collections need to be both present and not empty.

        - For mongo collections a dedicated filter can be applied before doing the count.
        - For pandas dataframes the additional option 'skip_chain_when_key_not_in_ds' exists.
            Meaning, skip the chain as well if the dataframe is not present in the datastore.
        """

        # check if collection names are in mongo database
        all_colls = self.mdb.collection_names()
        for c in self.collectionSet:
            if c not in all_colls:
                raise Exception("{collection} is not a collection in the mongo database.".format(collection=c))
            else:
                if c in self.filterDict:
                    if self.mdb[c].find(self.filterDict[c]).count() == 0:
                        self.logger.warning(
                            'Mongo collection <{collection}> with filter <{filter!s}> is empty. '
                            'Sending skip chain signal.', collection=c, filter=self.filterDict[c])
                        return StatusCode.SkipChain
                elif self.mdb[c].count() == 0:
                    self.logger.warning('Mongo collection <{collection}> is empty. Sending skip chain signal.',
                                        collection=c)
                    return StatusCode.SkipChain

        return StatusCode.Success
