#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Encode and decode objects into json.

This module exports generators for encoding and decoding
instances of the `collections.namedtuple` class using the JSON data format.
"""
import json


def strip_obj(obj):
    """Remove all keys who's values are False."""
    # we are ignoring return of expression we want the side affect
    # pylint: disable=expression-not-assigned
    [obj.pop(x) for x in list(obj.keys()) if obj[x] is None]
    # pylint: enable=expression-not-assigned


def generate_namedtuple_encoder(cls, mangle=strip_obj):
    """
    Return a namedtuple encoder for class cls.

    Generate a sub-class of ``json.JSONEncoder``, which encodes the instances of
    ``cls`` as a JSON object.
    """
    class NamedTupleEncoder(json.JSONEncoder):
        """Class to encode a cls into json."""

        def encode(self, o):
            """Encode the cls into a json hash."""
            if isinstance(o, cls):
                obj = o._asdict()
                mangle(obj)
                return json.dumps(obj)
            return json.JSONEncoder.default(self, o)
    return NamedTupleEncoder


def generate_namedtuple_decoder(cls):
    """
    Return a namedtuple decoder for the class cls.

    Generate a sub-class of ``json.JSONDecoder``, which decodes a JSON object into
    an instance of ``cls``.
    """
    class NamedTupleDecoder(json.JSONDecoder):
        """Class to decode a json string into a cls object."""

        # pylint: disable=arguments-differ
        def decode(self, str_obj):
            """Decode the string into a MetaObj object."""
            json_data = json.loads(str_obj)
            if isinstance(json_data, dict):
                return cls(**json_data)
            raise TypeError('Unable to turn {} into a dict'.format(str_obj))
        # pylint: enable=arguments-differ
    return NamedTupleDecoder
