#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created on 1/12/19 by Pat Blair
"""
.. currentmodule:: elastalk.config
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Make things work the way you want!
"""
from functools import lru_cache
import importlib
import json
import logging
import os
from pathlib import Path
import uuid
from typing import Iterable, Dict, Set
import toml
from dataclasses import dataclass, field

#: the module logger
__logger__: logging.Logger = logging.getLogger(__name__)


class _Defaults:
    """
    Module-level default values.
    """
    blob_key: str = '_blob'  #: the default key for blobs


class ElastalkConfigException(Exception):
    """Raised when a configuration error is detected."""


@dataclass
class BlobConf:
    """
    Define blobbing parameters.
    """
    #: indicates whether or not blobbing is enabled.
    enabled: bool = None

    #: the excluded top-level document keys
    excluded: Set[str] = field(default_factory=set)

    #: the key that stores blobbed values in packed documents
    key: str = None

    def exclude(self, *keys: str):
        """
        Add to the set of excluded document keys.

        :param keys: the excluded document keys
        """
        self.excluded.update(keys)  # pylint: disable=no-member

    @classmethod
    def load(cls, dict_: Dict) -> 'BlobConf' or None:
        """
        Create an instance of the class from a dictionary.

        :param dict_: the dictionary
        :return: the instance
        """
        # If we don't get any input...
        if not dict_:
            # ...we give nothing back.
            return None
        # Get the attributes to be excluded from blobbing (if there are any).
        _excluded = dict_.get('excluded')
        # Compile a dictionary of constructor arguments.
        cargs = {
            k: v for k, v in
            {
                'enabled': dict_.get('enabled'),
                'excluded': set(_excluded) if _excluded else None,
                'key': dict_.get('key')
            }.items() if v is not None
        }
        # Create the instance and return it.
        return cls(**cargs)


@dataclass
class IndexConf:
    """
    Define index-specific configuration settings.
    """
    blobs: BlobConf = BlobConf()  #: blobbing configuration for the index
    #: the path to Elasticsearch mappings for the configuration
    mappings: str = None

    def mappings_document(self, root: Path = None) -> dict or None:
        """
        Get the contents of the index mapping document (if one is defined).

        :param root: the root path that contains the document file
        :return: the index mapping document (or `None` if one isn't defined)
        """
        # If no mapping document is defined...
        if not self.mappings:
            return None  # ...that's that.
        # Determine the mappings path.
        mappings_path: Path = Path(self.mappings)
        # Figure out what the full path to the document is.
        _root = root if root else Path.cwd()
        full_path = (
            mappings_path
            if mappings_path.is_absolute()
            else (_root / mappings_path).resolve()
        )
        # If a mapping document *is* defined, but the file doesn't exist...
        if not full_path.exists():
            __logger__.warning(f"{mappings_path} does not exist.")
            return None  # ..there isn't much more we can do.
        # Read the text in the mappings document.
        return json.loads(full_path.read_text())

    @classmethod
    def load(cls, dict_: Dict) -> 'IndexConf' or None:
        """
        Create an instance of the class from a dictionary.

        :param dict_: the dictionary
        :return: the instance
        """
        # If we don't get any input...
        if not dict_:
            # ...we give nothing back.
            return None
        # Get the value of the 'mappings' key.
        _mappings = dict_.get('mappings')
        # Compile a dictionary of constructor arguments.
        cargs = {
            k: v for k, v in
            {
                'blobs': BlobConf.load(dict_.get('blobs')),
                'mappings': _mappings if _mappings else None
            }.items() if v is not None
        }
        # Create the instance and return it.
        return cls(**cargs)


@dataclass
class ElastalkConf:  # pylint: disable=unsubscriptable-object, unsupported-assignment-operation
    """
    Configuration options for an Elastalk and the Elasticsearch client.

    .. seealso:

        * :py:func:`client`
        * `Sniffing <https://bit.ly/2UTKyHh>`_
        * `Mapping <https://bit.ly/2EAzfir>`_
    """
    seeds: Iterable[str] = field(
        default_factory=lambda: [
            s.strip()
            for s
            in os.environ.get('ES_HOSTS', '127.0.0.1').split(',')
        ]
    )  #: the Elasticsearch seed hosts
    sniff_on_start: bool = True  #: Start sniffing on startup?
    sniff_on_connection_fail: bool = True  #: Sniff when the connection fails?
    sniffer_timeout: int = 60  #: the sniffer timeout
    maxsize: int = 10  #: the maximum number of connections
    mapping_field_limit: int = 1000  #: the maximum number of mapped fields
    blobs: BlobConf = BlobConf()  #: global BLOB behavior configuration
    indexes: Dict[str, IndexConf] = field(
        default_factory=dict
    )  #: index-specific configurations

    @lru_cache(maxsize=128)
    def blobs_enabled(self, index: str = None) -> bool:
        """
        Determine whether or not blobbing is enabled for an index.

        :param index: the name of the index
        :return: `True` if blobbing is enabled, otherwise `False`
        """
        try:
            # Get the value configured for the index.
            idx_value = self.indexes[index].blobs.enabled
            # If the index has a configured value, use it.  Otherwise use the
            # global version.
            if idx_value is not None:
                return idx_value
        except KeyError:
            pass
        # If we got to this point, just return the configured value.
        return False if self.blobs.enabled is None else self.blobs.enabled

    @lru_cache(maxsize=128)
    def blob_exclusions(self, index: str = None) -> Set[str]:
        """
        Get the full set of top-level document properties that should be
        excluded from blobs for a given index.  If you don't supply the `index`
        parameter, the method returns the global exclusions.

        :param index: the name of the index
        :return: the set of excluded property names
        """
        if not index:
            return self.blobs.excluded
        try:
            return (
                self.blobs.excluded |
                self.indexes[index].blobs.excluded
            )
        except KeyError:
            return self.blobs.excluded

    def blob_key(self, index: str = None) -> str:
        """
        Get the configured document key for blobbed data.  (If you don't
        supply the index, the method returns the global configuration value.
        If there is no global configuration value, the method returns the
        default.)

        :param index: the name of the index
        :return: the blobbed data key
        """
        key: str = None
        try:
            key = self.indexes[index].blobs.key
        except KeyError:
            pass
        key = key if key else self.blobs.key
        return key if key else _Defaults.blob_key

    def from_object(self, o: str):
        """
        Update the configuration from an object.

        :param o: the configuration object
        """
        # Split up the parts of the configuration object name.
        name_parts = o.split('.')
        # Import the module.
        mod = importlib.import_module('.'.join(name_parts[:-1]))
        # Get the configuration class.
        cls = getattr(mod, name_parts[-1])

        # Retrieve the hosts (if there are any).
        es_hosts = getattr(cls, 'ES_HOSTS', None)
        # The seeds might already be a list (if they're defined in code) or
        # they might be expressed as a comma-separated list.  We'll account
        # for both...
        self.seeds = [
            h.strip() for h in es_hosts.split(',')
        ] if isinstance(es_hosts, str) else list(es_hosts)

        # Configure other parameters.
        for t in [
                ('ES_SNIFF_ON_START', '_sniff_on_start', bool),
                (
                    'ES_SNIFF_ON_CONNECTION_FAIL',
                    'sniff_on_connection_fail',
                    bool
                ),
                ('ES_SNIFFER_TIMEOUT', 'sniffer_timeout', int),
                ('ES_MAXSIZE', 'maxsize', int),
                ('ES_MAPPING_FIELD_LIMIT', 'mapping_field_limit', int),
        ]:
            o_val = getattr(cls, t[0], None)
            if o_val is not None:
                self_val = t[2](o_val)
                setattr(self, t[1], self_val)

        # Let's see if there are any blobbing directives.
        blobs = BlobConf.load(getattr(o, 'ES_BLOBS', None))
        # If there are...
        if blobs:
            # ...we'll use 'em.
            self.blobs = blobs

        # Look for index-specific settings.
        indexes: dict = getattr(o, 'ES_INDEXES', None)
        if indexes:
            for index in indexes.keys():
                self.indexes[index] = IndexConf.load(indexes[index])

    def from_toml(self, toml_: Path or str):
        """
        Update the configuration from a TOML configuration.

        :param toml_: the path to the file or the TOML configuration string
        """
        # Whether we were passed a string or file path, get the TOML text and
        # parse it.
        _toml: dict = toml.loads(
            toml_.read_text()
            if isinstance(toml_, Path)
            else toml_
        )
        # Let's see if there are any blobbing directives.
        blobs = BlobConf.load(_toml.get('blobs'))
        # If there are...
        if blobs:
            # ...we'll use 'em.
            self.blobs = blobs

        # Look for index-specific settings.
        indexes: dict = _toml.get('indexes')
        if indexes:
            for index in indexes.keys():
                self.indexes[index] = IndexConf.load(indexes[index])

        # Load the top-level configuration values.
        for att in [
                'sniff_on_start',
                'sniff_on_connection_fail',
                'sniffer_timeout',
                'maxsize',
                'mapping_field_limit'
        ]:
            value = _toml.get(att)
            if value is not None:
                setattr(self, att, value)

    def __hash__(self):
        try:
            return getattr(self, '_hash')
        except AttributeError:
            hsh = uuid.uuid4().int
            setattr(self, '_hash', hsh)
            return hsh

    def __eq__(self, other):
        return self.__hash__() == hash(other) if other else False

    def __ne__(self, other):
        return not self.__eq__(other)
