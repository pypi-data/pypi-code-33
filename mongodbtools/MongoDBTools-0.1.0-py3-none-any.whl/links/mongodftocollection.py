# **********************************************************************************
# * Project: Eskapade - A python-based package for data analysis                   *
# * Class  : MongoDFToCollection                                                   *
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

from copy import deepcopy
import pandas as pd

from escore import process_manager, ConfigObject, DataStore, Link, StatusCode
from mongodbtools import MongoConnection, etl_utils, etl_utils


class MongoDFToCollection(Link):
    """
    Adds data in a pandas.DataFrame to one or more mongo collections.
    """

    def __init__(self, name='MongoDfToCollection'):
        """
        Store the configuration of link MongoDFToCollection

        :param str name: name of link
        :param str read_key: key of data to read from data store
        :param dict nestedFields: nested structure of columns to be used in mongo. If string, datastore key of the
            nested structure.
        :param list store_collections: mongo collection names of the collections to store the data
        :param bool clearFirst: if True the mongo store_collections are cleared before storage
        :param dict columnsToAdd: columns to add to the pandas.DataFrame before storage. key = column name,
            value = column value
        :param checkFieldsAPI: check compatibility with the data service, i.e. field names that are reserved by the
            data service should not be used as column names in the dataframes. In case this is done anyway
            (don't do that!), the columns have to be of the type defined by the data service otherwise the data in this
            collection will not be processed by the service at all (just silence...)
        """

        # TODO - GOSSIE: use a smart structure with different levels to avoid collisions with reserved field names
        # (e.g. doc['record'] = record, doc['meta'] = reserved_fields_for_api)

        Link.__init__(self, name)

        self.read_key = None
        self.nestedFields = None
        self.store_collections = []
        self.clearFirst = False
        self.columnsToAdd = None
        self.checkFieldsAPI = False
        self.copy = True
        self.columns = []

        return

    def initialize(self):
        """ Initialize MongoDFToCollection """

        process_manager.service(MongoConnection).set_config_info(process_manager.service(ConfigObject))
        self.mdb = process_manager.service(MongoConnection).database

        assert isinstance(self.read_key, str) and len(self.read_key) > 0, 'read key not set.'
        if len(self.store_collections) == 0:
            self.store_collections.append(self.read_key)
        return StatusCode.Success

    def execute(self):
        """ Execute MongoDFToCollection """

        ds = process_manager.service(DataStore)

        if isinstance(self.nestedFields, dict):
            # assume set correctly
            pass
        elif isinstance(self.nestedFields, str) and self.nestedFields:
            assert self.nestedFields in ds, 'Key %s not in DataStore.' % self.nestedFields
            self.nestedFields = ds[self.nestedFields]

        df_orig = ds[self.read_key]

        if len(df_orig) == 0:
            self.logger.warning('Source collection "{key}" has zero length. Nothing to store in Mongo.',
                                key=self.read_key)
        else:
            # MB: May have to do some index magic below for nested fields (pandas v0.18 and greater)
            # We don't want to modify the user's DataFrame here, so we make a shallow copy
            if self.copy:
                df = df_orig.copy(deep=False)
            else:
                df = df_orig

            if self.columns:
                df = df[self.columns]

            if self.checkFieldsAPI:
                df = etl_utils.check_fields_api(df)

            if isinstance(self.nestedFields, dict):
                flattened_nested_columns = etl_utils.flatten_columns(self.nestedFields)
                for c in flattened_nested_columns:
                    if c not in df.columns:
                        raise Exception('Field %s from nestedFields not present in dataframe %s' % (c, self.read_key))
                other_columns = [c for c in df.columns if c not in flattened_nested_columns]

                # MB: utils.create_nested_df() screws up the original index in pandas v0.18
                # index_name is added to nested_df, so it can be merged later by original index
                index_name = '__index__' if df.index.name is None else '__index__' + df.index.name
                df[index_name] = df.index
                nestedFields = deepcopy(self.nestedFields)
                nestedFields[index_name] = [index_name]
                nested_df = etl_utils.create_nested_df(nestedFields, df)
                nested_df[index_name] = nested_df[index_name].apply(etl_utils.orig_index, key=index_name)
                nested_df.index = nested_df[index_name]
                nested_df.drop(index_name, axis=1, inplace=True)
                # ... and we have the original index again, so merging with other_columns works

                nested_df = pd.concat([nested_df, df[other_columns]], axis=1)
                if self.columnsToAdd is not None:
                    for k, v in self.columnsToAdd.items():
                        nested_df[k] = v
                self.logger.debug('Getting values from nested dataframe.')
                docs = list(nested_df.T.to_dict().values())
            else:
                if self.columnsToAdd is not None:
                    for k, v in self.columnsToAdd.items():
                        df[k] = v
                self.logger.debug('Getting values from dataframe.')
                docs = list(df.T.to_dict().values())

            self.logger.debug('Started doing storage')
            etl_utils.dostorage(self.mdb, docs, self.store_collections, self.clearFirst, self.logger, self.read_key)
        return StatusCode.Success
