#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This is the metadata library.

The `pacifica.uploader.metadata` module exports classes and methods for manipulating and
serializing the metadata for bundles of files.

Encoding and decoding to the JSON data format is supported for compatible
objects (see `pacifica.uploader.metadata.Json` module for more information).
"""
from .metadata import MetaData, MetaObj, metadata_encode, metadata_decode, FileObj
from .metaupdate import MetaUpdate

__all__ = [
    'MetaData',
    'MetaObj',
    'FileObj',
    'MetaUpdate',
    'metadata_encode',
    'metadata_decode'
]
