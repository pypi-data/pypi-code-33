# **********************************************************************************
# * Project: Eskapade - A python-based package for data analysis                   *
# * Class  : MongoCollectionToDF                                                   *
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


def get_basic_nested_structure(y):
    if not type(y) is dict:
        return {}
    structure = {}
    for k, v in y.items():
        if not type(v) is dict:
            continue
        structure[k] = []
        for key, value in v.items():
            if isinstance(value, (list, dict)):
                continue
            else:
                structure[k].append(key)
    return structure


def flatten_json(y, addprefix=True):
    out = {}

    def flatten(x, name='', addprefix=True):
        if type(x) is dict:
            for a in x:
                newname = name + a + '_' if addprefix else a + '_'
                flatten(x[a], newname, addprefix)
        elif type(x) is list:
            for i, a in enumerate(x):
                flatten(a, name + str(i) + '_', addprefix)
        else:
            out[str(name[:-1])] = x

    flatten(y, addprefix=addprefix)
    return out


class MongoCollectionToDF(Link):
    """
    Retrieves data from a mongo collection and stores it in the datastore in the form of a pandas.DataFrame.
    """

    skipIfInDatastore = False

    def __init__(self, name='MongoCollectionToDF'):
        """
        Store the configuration of link MongoCollectionToDF

        :param str name: name of link
        :param str store_key: key of data to store in data store
        :param str collection: name of the mongo collection
        :param dict/str filter: Filter applied on the mongo query (optional). If string, datastore key of the filter
        :param dict/list columns: Columns to retrieve from mongo. If string, datastore key of the columns
        :param dict columnsToAdd: columns to add to the pandas.DataFrame. key = column name, value = column value
        :param bool store_if_empty: if True and the retrieved data from mongo is empty an empty pandas.DataFrame is
            stored
        :param bool flatten_json: if True the flatten_json method is applied on the retrieved data from mongo
        :param bool flatten_json_addprefix: if True and when flattening, a prefix is added
        :param bool storeNestedStructure: if True the nesting structure is stored in the datastore as a dict with key:
            <self.collection>_nestedstructure
        """

        Link.__init__(self, name)

        self.collection = None
        self.store_key = None
        self.filter = None
        self.columns = None
        self.columnsToAdd = None
        self.store_if_empty = False
        self.flatten_json = True
        self.flatten_json_addprefix = False
        self.storeNestedStructure = True
        return

    def initialize(self):
        """ Initialize MongoCollectionToDF """

        assert isinstance(self.collection, str) and self.collection, 'mongo collection key not set.'
        if self.store_key is not None:
            assert isinstance(self.store_key, str) and self.store_key, 'datastore storage key not set correctly.'
        else:
            self.store_key = self.collection

        process_manager.service(MongoConnection).set_config_info(process_manager.service(ConfigObject))
        self.mdb = process_manager.service(MongoConnection).database
        colls = self.mdb.collection_names()
        if self.collection not in colls:
            raise Exception("%s is not a collection in the mongo database" % self.collection)
        return StatusCode.Success

    def execute(self):
        """ Execute MongoCollectionToDF """

        ds = process_manager.service(DataStore)

        if MongoCollectionToDF.skipIfInDatastore and self.store_key in ds:
            self.logger.warning('Storekey <{key}> already in DataStore. Skipping data reading.', key=self.store_key)
            return StatusCode.Success

        if self.filter is not None:
            if isinstance(self.filter, dict):
                pass
            elif isinstance(self.filter, str):
                assert self.filter in ds, 'Filter key "{key}" not found in datastore.'.format(key=self.filter)
                self.filter = ds[self.filter]
                assert isinstance(self.filter, dict), 'Filter with key "{key}" is not a dict.'.format(key=self.filter)
            else:
                raise Exception('Given filter of incorrect type.')

        if self.columns is not None:
            if isinstance(self.columns, dict):
                pass
            elif isinstance(self.columns, list):
                colselection = {}
                for col in self.columns:
                    if isinstance(col, str):
                        colselection[col] = 1
                self.columns = colselection
            elif isinstance(self.columns, str):
                assert self.columns in ds, 'Columns key <%s> not found in datastore.' % self.columns
                self.columns = ds[self.columns]
                assert isinstance(self.columns, dict), 'Retrieved columns with key <%s> is not a dict.' % self.columns
            else:
                raise Exception('Given columns of incorrect type.')

        # filter and column selection
        if self.filter is not None:
            if self.columns is not None:
                data = self.mdb[self.collection].find(self.filter, self.columns)
            else:
                data = self.mdb[self.collection].find(self.filter)
        else:
            if self.columns is not None:
                data = self.mdb[self.collection].find({}, self.columns)
            else:
                data = self.mdb[self.collection].find()

        self.logger.debug('Length of Mongo collection <{collection> is <{count:d}>.',
                          collection=self.collection, count=data.count())

        if data.count() == 0:
            self.logger.warning('Mongo collection <{collection}> has zero length. Nothing stored in data store.',
                                collection=self.collection)
            if not self.store_if_empty:
                return StatusCode.Success

        # determine nested structure, for possible later use.
        if self.flatten_json and self.storeNestedStructure is True:
            storeNestedStructureKey = self.collection + '_nestedstructure'
            structure = {}
            if data.count() > 0:
                structure = get_basic_nested_structure(data[0])
            if len(structure) > 0:
                ds[storeNestedStructureKey] = structure
                self.logger.info('Nested structure has been stored in: {key}.', key=storeNestedStructureKey)

        # flatten any json substructures
        if self.flatten_json:
            # number of iterations is equal to the total number of nested columns
            datalist = [flatten_json(x, self.flatten_json_addprefix) for x in list(data)]
        else:
            datalist = list(data)

        df = pd.DataFrame(datalist)

        if self.columnsToAdd is not None:
            for k, v in self.columnsToAdd.items():
                df[k] = v

        ds[self.store_key] = df
        ds['n_' + self.store_key] = len(df.index)
        self.logger.info('Put dataframe "{key}" with length {length:d} into data store.',
                         key=self.store_key, length=len(df))

        return StatusCode.Success

    def finalize(self):
        """ Finalizing MongoCollectionToDF """

        return StatusCode.Success
