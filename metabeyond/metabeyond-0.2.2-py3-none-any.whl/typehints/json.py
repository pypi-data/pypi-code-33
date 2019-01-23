#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Useful JSON type aliases.

References:
    - RFC-4627_
    - https://github.com/python/typing/issues/182

.. _RFC-4627: https://tools.ietf.org/html/rfc4627
"""
from typing import Mapping, Optional, Sequence, TypeVar, Union

# Create a woolly basic definition to start, as MyPy doesn't support recursive hints yet.
#: Any valid JSON type that is **not** `null`
AnyJSON = Union["JSONBool", "JSONNumber", "JSONString", "JSONArray", "JSONObject"]

#: Any valid JSON type. This is allowed to be `null`.
OptionalAnyJSON = Optional[AnyJSON]

#: A null value in a JSON document.
JSONNull = None

#: A boolean value in a JSON document.
JSONBool = TypeVar("JSONBool", bound=bool)
#: A :attr:`JSONBool` that may be `null`.
OptionalJSONBool = Optional[JSONBool]

#: A number (int or float) in a JSON document.
JSONNumber = Union[float, int]

#: A :attr:`JSONNumber` that may be `null`.
OptionalJSONNumber = Optional[JSONNumber]

#: A string in a JSON document. This may be interpreted in Python as :class:`str` or :class:`bytes` objects.
JSONString = Union[str, bytes]

#: A :attr:`JSONString` that may be `null`.
OptionalJSONString = Optional[JSONString]

#: An array (sequence of :attr:`AnyJSON` elements) in a JSON document.
JSONArray = Sequence[OptionalAnyJSON]

#: A :attr:`JSONArray` that may be `null`.
OptionalJSONArray = Optional[JSONArray]

#: An object (mapping of non-null :attr:`JSONString` to :attr:`AnyJSON` elements) in a JSON document.
JSONObject = Mapping[JSONString, OptionalAnyJSON]

#: A :attr:`JSONObject` that may be `null`.
OptionalJSONObject = Optional[JSONObject]

#: A valid root element in a JSON document. As per RFC-4627_, this must be a non-`null` :attr:`JSONArray` or
#: :attr:`JSONObject` element.
RootJSON = Union[JSONArray, JSONObject]
