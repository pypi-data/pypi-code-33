# **********************************************************************************
# * Project: Eskapade - A python-based package for data analysis                   *
# * Created: 2016/11/08                                                            *
# * Description:                                                                   *
# *      Class and collection of Mongo utility functions used in Eskapade          *
# *      to establish connection to mongo database.                                *
# *                                                                                *
# * Authors:                                                                       *
# *      KPMG Big Data team, Amstelveen, The Netherlands                           *
# *                                                                                *
# * Redistribution and use in source and binary forms, with or without             *
# * modification, are permitted according to the terms listed in the file          *
# * LICENSE.                                                                       *
# **********************************************************************************

from pymongo.errors import BulkWriteError
import pandas as pd


def dostorage(mdb, docs, store_collections, clear_first, logger, read_key):
    """ Storage of the docs in mongo """

    for c in store_collections:
        if clear_first:
            mdb[c].delete_many({})
        try:
            mdb[c].insert_many(docs)
        except BulkWriteError as bwe:
            logger.error('Error writing to mongo: {details!s}' , details=bwe.details)

    logger.info('Stored collection "{key}" with length {length:d} into mongo: {collection!s}.',
                key=read_key, length=len(docs), collection=store_collections)


def reset_mongo_collections(mdb, keep_conf_colls=True):
    col_keep = ['proxy', 'roles'] if keep_conf_colls else []

    col_names = mdb.collection_names(False)
    for name in col_names:
        if mdb[name].name not in col_keep:
            mdb[name].remove({})
            mdb.drop_collection(name)


def flatten_columns(d):
    columns = []
    for key, value in d.items():
        if isinstance(value, dict):
            cs = flatten_columns(value)
            columns = columns + cs
        elif isinstance(value, list):
            columns = columns + value
        else:
            raise Exception('Nested fields has no valid structure. See %s key' % key)
    return columns


# TODO - GOSSIE: nice but slow... optimize some how some day?
def create_nested_df(d, df):
    l = []
    colls = []
    for key, v in d.items():
        if isinstance(v, dict):
            tmp_df = create_nested_df(v, df)
            l.append(list(tmp_df.T.to_dict().values()))
            colls.append(key)
        elif isinstance(v, list):
            l.append(list(df[v].T.to_dict().values()))
            colls.append(key)
        else:
            raise Exception('Nested fields has no valid structure. See %s key' % key)
    result = pd.DataFrame(l).T
    result.columns = colls
    return result


def orig_index(x, **kwargs):
    try:
        key = kwargs['key']
    except:
        return x
    try:
        val = x[key]
    except:
        return x
    return val


def check_fields_api(df):
    """
    MG: The data service API explicitly requires the following fields to be defined with the correct types:
    - version: integer
    - measurementTimestamp: numpy datetime64[ns], i.e. numpy.dtype('datetime64[ns]')
    otherwise the JBOSS service will fail to return results.
    See also: https://gitlab-nl.dna.kpmglab.com/kave/servicekave

    NOTE: for performance, we merely check if the conversion works if the fields exists - it does NOT
    guarantee that converted values are correct!
    """
    if 'version' in df:
        try:
            df['version'] = df['version'].astype(int)
        except:
            raise Exception("the 'version' field, reserved for the Data Service API, requires integers only!")

    if 'measurementTimestamp' in df:
        try:
            df['measurementTimestamp'] = df['measurementTimestamp'].astype('datetime64[ns]')
        except:
            raise Exception(
                "the 'measurementTimestamp' field, reserved for the Data Service API, requires datetime64[ns] only!")
    return df
