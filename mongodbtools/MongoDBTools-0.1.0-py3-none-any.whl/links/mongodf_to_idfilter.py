# **********************************************************************************
# * Project: Eskapade - A python-based package for data analysis                   *
# * Class  : MongoDFToIDFilter                                                     *
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

from escore import process_manager, DataStore, Link, StatusCode


class MongoDFToIDFilter(Link):
    """
    Creates a pymongo filter based on a pandas.DataFrame column.
    """

    def __init__(self, name='MongoDFToIDFilter'):
        """
        Store the configuration of link MongoDFToIDFilter

        :param str name: name of link
        :param str read_key: key of data to read from data store
        :param str store_key: key of data to store in data store
        :param str column: a column name of the pandas.DataFrame
        :param str mongoid: mongo id
        :param str store_key: datastore key of the pymongo filter
        :param dict mergewithfilter: pymongo filter to be added
        """

        Link.__init__(self, name)

        self.read_key = None
        self.column = ''
        self.mongoid = '_id'
        self.store_key = ''
        self.mergewithfilter = {}
        return

    def initialize(self):
        """ Initialize MongoDFToIDFilter """

        assert self.store_key != '', 'data store Key not set.'
        assert self.mongoid != '', 'mongo id variable not set.'
        assert self.column != '', 'dataframe column not set.'
        assert isinstance(self.mergewithfilter, dict), 'merge filter not of type dict.'
        return StatusCode.Success

    def execute(self):
        """ Execute MongoDFToIDFilter """

        ds = process_manager.service(DataStore)
        assert self.read_key in ds, 'Key <%s> not in DataStore.' % self.read_key

        df = ds[self.read_key]
        assert self.column in df.columns, 'Column <%s> not in dataframe <%s>.' % (self.column, self.read_key)

        if len(df) == 0:
            self.logger.warning('Input collection <{key}> is empty. No ID filter stored!', key=self.read_key)
            return StatusCode.Success

        ids = df[self.column].dropna()

        if len(ids) == 0:
            self.logger.warning('Input collection <{key}> column <{column}> is empty. No ID filter stored!',
                                key=self.read_key, column=self.column)
            return StatusCode.Success

        from bson import objectid
        if not isinstance(ids.iloc[0], objectid.ObjectId):
            def moid(x):
                return objectid.ObjectId(x)
            ids = ids.apply(moid)

        filter = {self.mongoid: {"$in": list(ids)}}

        for key, val in self.mergewithfilter.items():
            filter[key] = val

        ds[self.store_key] = filter
        self.logger.info('Put id list with length <{length:d}> under key <{key}>.', length=len(ids), key=self.store_key)
        return StatusCode.Success

    def finalize(self):
        """ Finalizing MongoDFToIDFilter """

        return StatusCode.Success
