"""
Module providing a custom order for json-based Avro schemas.
"""
from collections import OrderedDict
from typing import Union

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"

from dataclasses import dataclass


@dataclass
class Avro:
    """
    Helper class to avoid plain strings as dictionary keys.
    """
    Name = 'name'
    Namespace = 'namespace'
    Type = 'type'
    Fields = 'fields'
    Items = 'items'
    Doc = 'doc'
    Record = 'record'
    Error = 'error'
    Enum = 'enum'
    Default = 'default'
    LogicalType = 'logicalType'

    Protocol = 'protocol'
    Messages = 'messages'
    Request = 'request'
    Response = 'response'
    Types = 'types'
    Errors = 'errors'

    Optional = 'nullable_optional'
    PartitionKey = 'partition-field'

    Null = 'null'
    Value = 'value'

    Node = Union[str, list, OrderedDict]
    Key = Union[slice, int, None]
