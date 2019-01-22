# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import pulumi
import pulumi.runtime
from .. import utilities, tables

class GetTableResult(object):
    """
    A collection of values returned by getTable.
    """
    def __init__(__self__, arn=None, attributes=None, global_secondary_indexes=None, hash_key=None, local_secondary_indexes=None, range_key=None, read_capacity=None, server_side_encryption=None, stream_arn=None, stream_enabled=None, stream_label=None, stream_view_type=None, tags=None, ttl=None, write_capacity=None, id=None):
        if arn and not isinstance(arn, str):
            raise TypeError('Expected argument arn to be a str')
        __self__.arn = arn
        if attributes and not isinstance(attributes, list):
            raise TypeError('Expected argument attributes to be a list')
        __self__.attributes = attributes
        if global_secondary_indexes and not isinstance(global_secondary_indexes, list):
            raise TypeError('Expected argument global_secondary_indexes to be a list')
        __self__.global_secondary_indexes = global_secondary_indexes
        if hash_key and not isinstance(hash_key, str):
            raise TypeError('Expected argument hash_key to be a str')
        __self__.hash_key = hash_key
        if local_secondary_indexes and not isinstance(local_secondary_indexes, list):
            raise TypeError('Expected argument local_secondary_indexes to be a list')
        __self__.local_secondary_indexes = local_secondary_indexes
        if range_key and not isinstance(range_key, str):
            raise TypeError('Expected argument range_key to be a str')
        __self__.range_key = range_key
        if read_capacity and not isinstance(read_capacity, int):
            raise TypeError('Expected argument read_capacity to be a int')
        __self__.read_capacity = read_capacity
        if server_side_encryption and not isinstance(server_side_encryption, dict):
            raise TypeError('Expected argument server_side_encryption to be a dict')
        __self__.server_side_encryption = server_side_encryption
        if stream_arn and not isinstance(stream_arn, str):
            raise TypeError('Expected argument stream_arn to be a str')
        __self__.stream_arn = stream_arn
        if stream_enabled and not isinstance(stream_enabled, bool):
            raise TypeError('Expected argument stream_enabled to be a bool')
        __self__.stream_enabled = stream_enabled
        if stream_label and not isinstance(stream_label, str):
            raise TypeError('Expected argument stream_label to be a str')
        __self__.stream_label = stream_label
        if stream_view_type and not isinstance(stream_view_type, str):
            raise TypeError('Expected argument stream_view_type to be a str')
        __self__.stream_view_type = stream_view_type
        if tags and not isinstance(tags, dict):
            raise TypeError('Expected argument tags to be a dict')
        __self__.tags = tags
        if ttl and not isinstance(ttl, dict):
            raise TypeError('Expected argument ttl to be a dict')
        __self__.ttl = ttl
        if write_capacity and not isinstance(write_capacity, int):
            raise TypeError('Expected argument write_capacity to be a int')
        __self__.write_capacity = write_capacity
        if id and not isinstance(id, str):
            raise TypeError('Expected argument id to be a str')
        __self__.id = id
        """
        id is the provider-assigned unique ID for this managed resource.
        """

async def get_table(name=None, server_side_encryption=None, tags=None):
    """
    Provides information about a DynamoDB table.
    """
    __args__ = dict()

    __args__['name'] = name
    __args__['serverSideEncryption'] = server_side_encryption
    __args__['tags'] = tags
    __ret__ = await pulumi.runtime.invoke('aws:dynamodb/getTable:getTable', __args__)

    return GetTableResult(
        arn=__ret__.get('arn'),
        attributes=__ret__.get('attributes'),
        global_secondary_indexes=__ret__.get('globalSecondaryIndexes'),
        hash_key=__ret__.get('hashKey'),
        local_secondary_indexes=__ret__.get('localSecondaryIndexes'),
        range_key=__ret__.get('rangeKey'),
        read_capacity=__ret__.get('readCapacity'),
        server_side_encryption=__ret__.get('serverSideEncryption'),
        stream_arn=__ret__.get('streamArn'),
        stream_enabled=__ret__.get('streamEnabled'),
        stream_label=__ret__.get('streamLabel'),
        stream_view_type=__ret__.get('streamViewType'),
        tags=__ret__.get('tags'),
        ttl=__ret__.get('ttl'),
        write_capacity=__ret__.get('writeCapacity'),
        id=__ret__.get('id'))
