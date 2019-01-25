#!/usr/bin/python
# -*- coding: utf-8 -*-
"""MetaData class to handle input and output of metadata format."""
from __future__ import absolute_import
import json
from collections import namedtuple
from .mjson import generate_namedtuple_encoder, generate_namedtuple_decoder


class MetaData(list):
    """
    Class to hold a list of MetaObj and FileObj objects.

    This class is a sub-class of ``list`` that implements
    the index protocol (``__getitem__``, ``__setitem__`` and ``__delitem__``) as a proxy
    to the indices of the value of the ``metaID`` field of the associated instance of
    the ``pacifica.uploader.metadata.MetaObj`` class.

    Instances of this class are upper-level objects that
    provide the metadata for interacting with the designated
    `Pacifica Ingest <https://github.com/pacifica/pacifica-ingest>`_ server.
    """

    def __init__(self, *args, **kwargs):
        """Call the super constructor and add a metaID index to it as well."""
        super(MetaData, self).__init__(*args, **kwargs)
        self._meta_index_map = {}
        if args:
            for key in range(len(args[0])):
                item = args[0][key]
                if getattr(item, 'metaID', False):
                    self._meta_index_map[item.metaID] = key

    def __delitem__(self, key):
        """Delete the item from the array and hash."""
        item = self[key]
        super(MetaData, self).__delitem__(key)
        if getattr(item, 'metaID', False):
            del self._meta_index_map[item.metaID]

    def __setitem__(self, key, value):
        """Set the item and if metaID exists save the index into a map."""
        old_val = self[key]
        if isinstance(key, int):
            true_key = key
        else:
            if getattr(value, 'metaID', False):
                true_key = int(self._meta_index_map[old_val.metaID])
            else:
                raise IndexError('No metaID {}'.format(
                    getattr(value, 'metaID', False)))
        super(MetaData, self).__setitem__(true_key, value)
        if getattr(old_val, 'metaID', False):
            del self._meta_index_map[old_val.metaID]
        if getattr(value, 'metaID', False):
            self._meta_index_map[value.metaID] = true_key

    def __getitem__(self, key):
        """Get the node based on metaID."""
        if isinstance(key, int):
            return super(MetaData, self).__getitem__(key)
        if key in self._meta_index_map:
            return self[self._meta_index_map[key]]
        raise IndexError('No such key {}'.format(key))

    def append(self, value):
        """Append the value to the list."""
        super(MetaData, self).append(value)
        if getattr(value, 'metaID', False):
            self._meta_index_map[value.metaID] = len(self) - 1

    def extend(self, iterable):
        """Extend the array from the values in iterable."""
        for value in iterable:
            self.append(value)

    def remove(self, value):
        """Remove the value from the list."""
        super(MetaData, self).remove(value)
        if getattr(value, 'metaID', False):
            del self._meta_index_map[value.metaID]

    def pop(self, key=-1):
        """Remove the key from the list and return it."""
        if key == -1:
            key = len(self) - 1
        value = super(MetaData, self).pop(key)
        if getattr(value, 'metaID', False):
            del self._meta_index_map[value.metaID]
        return value

    def insert(self, key, value):
        """Insert the value to the list."""
        super(MetaData, self).insert(key, value)
        for ikey, ivalue in self._meta_index_map.items():
            if ivalue >= key:
                self._meta_index_map[ikey] = ivalue + 1
        if getattr(value, 'metaID', False):
            self._meta_index_map[value.metaID] = key

    def is_valid(self):
        """Return true if all the values of MetaObjs are something."""
        return set([bool(obj.value) for obj in self if isinstance(obj, MetaObj)]) == set([True])


META_KEYS = [
    'sourceTable',
    'destinationTable',
    'metaID',
    'displayType',
    'displayTitle',
    'queryDependency',
    'valueField',
    'queryFields',
    'displayFormat',
    'key',
    'value',
    'directoryOrder',
    'query_results'
]
_MetaObj = namedtuple('MetaObj', META_KEYS)
# Set the defaults to None for these attributes
_MetaObj.__new__.__defaults__ = (None,) * len(_MetaObj._fields)


class MetaObj(_MetaObj):
    """
    MetaObj class holding a specific metadata element.

    Instances of this class represent units of metadata
    whose representation is disjoint to a file, i.e., units of metadata that are
    describe but are not stored as part of a file.
    """

    pass


FILE_KEYS = [
    'destinationTable',
    'name',
    'subdir',
    'size',
    'hashtype',
    'hashsum',
    'mimetype',
    'ctime',
    'mtime'
]
_FileObj = namedtuple('FileObj', FILE_KEYS)
# Set the defaults to None for these attributes
_FileObj.__new__.__defaults__ = (None,) * len(_FileObj._fields)


class FileObj(_FileObj):
    """
    FileObj class for holding file metadata.

    Instances of this class represent individual files,
    including both the data and metadata for the file. During a file upload,
    instances of this class are automatically associated
    with new instances of the ``pacifica.uploader.metadata.MetaData`` class.

    The above named fields are identical to those of the ``pacifica.metadata.orm.Files`` class,
    provided by the
    `Pacifica Metadata <https://github.com/pacifica/pacifica-metadata>`_ library.
    """

    pass


def file_or_meta_obj(**json_data):
    """Determine if this is a File or Meta object and return result."""
    if json_data.get('destinationTable') == 'Files':
        return FileObj(**json_data)
    return MetaObj(**json_data)


MetaObjEncoder = generate_namedtuple_encoder(MetaObj)
FileObjEncoder = generate_namedtuple_encoder(FileObj)
MetaObjDecoder = generate_namedtuple_decoder(file_or_meta_obj)


class MetaDataEncoder(json.JSONEncoder):
    """Class to encode a MetaData object into json."""

    def encode(self, o):
        """Encode the MetaData object into a json list."""
        if isinstance(o, MetaData):
            json_parts = []
            for mobj in o:
                if not hasattr(mobj, 'destinationTable'):
                    return json.JSONEncoder.default(self, o)
                encoder_class = FileObjEncoder if mobj.destinationTable == 'Files' else MetaObjEncoder
                json_parts.append(json.loads(
                    json.dumps(mobj, cls=encoder_class)))
            return json.dumps(json_parts)
        return json.JSONEncoder.default(self, o)


class MetaDataDecoder(json.JSONDecoder):
    """Class to decode a json string into a MetaData object."""

    # pylint: disable=arguments-differ
    def decode(self, s):
        """Decode the string into a MetaData object."""
        json_data = json.loads(s)
        if isinstance(json_data, list):
            return MetaData([MetaObjDecoder().decode(json.dumps(obj)) for obj in json_data])
        raise TypeError('Unable to turn {} into a list'.format(s))


def metadata_decode(json_str):
    """
    Decode the json string into MetaData object.

    This method deserializes the given
    JSON source, ``json_str``, and then returns a new instance of the
    ``pacifica.uploader.metadata.MetaData`` class.

    The new instance is automatically associated with new instances of the
    ``pacifica.uploader.metadata.MetaObj`` and ``pacifica.uploader.metadata.FileObj`` classes.
    """
    return json.loads(json_str, cls=MetaDataDecoder)


def metadata_encode(md_obj):
    """
    Encode the MetaData object into a json string.

    This method encodes the given
    instance of the ``pacifica.uploader.metadata.MetaData`` class, ``md_obj``, as a JSON object,
    and then returns its JSON serialization.

    Associated instances of the ``pacifica.uploader.metadata.MetaObj`` and
    ``pacifica.uploader.metadata.FileObj`` classes are automatically included in the JSON
    object and the resulting JSON serialization.
    """
    return json.dumps(md_obj, cls=MetaDataEncoder)
