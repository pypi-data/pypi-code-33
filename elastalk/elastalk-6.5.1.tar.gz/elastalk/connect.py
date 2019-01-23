#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created on 1/12/19 by Pat Blair
"""
.. currentmodule:: elastalk.client
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Start a conversation with Elasticsearch!
"""
import base64
import binascii
import json
import logging
from typing import Any, Dict
import elasticsearch
from .config import ElastalkConf, ElastalkConfigException


__logger__: logging.Logger = logging.getLogger(__name__)  #: the module logger


class ElastalkConnection(object):
    """
    Defines an Elasticsearch environment.
    """
    def __init__(self, config: ElastalkConf = None):
        """

        :param config: the configuration
        """
        self._config: ElastalkConf = (
            config if config else ElastalkConf()
        )  #: the configuration
        # The Elasticsearch client will be created on demand.
        self._client: elasticsearch.Elasticsearch = (
            None
        )  #: the Elasticsearch client

    @property
    def config(self) -> ElastalkConf:
        """
        Get the connection configuration.

        :return: the connection configuration
        """
        return self._config

    @config.setter
    def config(self, value: ElastalkConf):
        """
        Set the configuration object.  (Setting this property will
        :ref:`reset <:py:func:ElastalkConnection.reset>` the connection.

        :param value: the new configuration
        """
        self._config = value
        self.reset()

    @property
    def client(self) -> elasticsearch.Elasticsearch:
        """
        Get the Elasticsearch client.

        :return: the Elasticsearch client
        :raises ElasticsearchConfigurationException: if there is an error in
            the current configuration
        """
        # If we've already created the client...
        if self._client:
            return self._client  # ...just send it back.

        # Create a list of the configured seed hosts.
        if not self.config.seeds:
            raise ElastalkConfigException(
                'No seed hosts have been defined.'
            )

        # Otherwise we need to create it.
        self._client = elasticsearch.Elasticsearch(
            list(self.config.seeds),
            sniff_on_start=self.config.sniff_on_start,
            sniff_on_connection_fail=self.config.sniff_on_connection_fail,
            sniffer_timeout=self.config.sniffer_timeout,
            maxsize=self.config.maxsize
        )
        return self._client

    def reset(self):
        """Reset the connection."""
        self._client = None

    def pack(self, doc: Dict, index: str) -> Dict[str, Any]:
        """
        Convert a document object into a BLOB document.

        :param doc: the original document object
        :param index: the name of the index *(This is optional, but if you
            supply it the behavior configured for the index can be used.)*
        :return: the BLOB document
        """
        # If blobbing isn't enabled for this index...
        if not self.config.blobs_enabled(index=index):
            return doc  # ...we don't need to do anything further.

        # Get the key used to hold blobbed data.
        blob_key = self.config.blob_key(index=index)

        # Get the list of document properties that should be excluded from
        # blobbed data.
        blob_exclusions = self.config.blob_exclusions(index=index)

        # Create a dictionary to hold...
        blob_ = {}  # ...the blob-able keys, and another to hold...
        noblob_ = {}  # ...the excluded keys.

        # Sort out which keys will go in the blob and which are excluded.
        for k, v in doc.items():
            if k in blob_exclusions:
                noblob_[k] = v
            else:
                blob_[k] = v

        # Recombine the blobbed data with the un-blobbed data.
        return {
            **noblob_,
            blob_key: _encode(blob_)
        }

    def unpack(self, doc: Dict, index: str = None) -> Dict:
        """
        Convert a :py:func:`packed <pack>` document to its original form.

        :param doc: the packed document
        :param index: the name of the index for which the packed document came
        :return: the unpacked document
        """
        # Get the key we should use to store blobbed data.
        blob_key = self.config.blob_key(index=index)

        # Try to get the document.
        blob = doc.get(blob_key)
        # If there is no blob in the document...
        if not blob:
            return doc  # ...we can simply return the original document.

        # Decode the blob and combine it with the rest of the document.
        return {
            **{k: v for k, v in doc.items() if k != blob_key},
            **_decode(blob)
        }

    @staticmethod
    def default(cnx: 'ElastalkConnection' = None) -> 'ElastalkConnection':
        """
        Set and/or retrieve the default connection object.

        :param cnx: Provide a new connection object if you want to change the
            default.  Otherwise, leave this argument out to retrieve the
            current object.
        :return: the default connection object
        """
        if cnx:
            setattr(ElastalkConnection, '__default__', cnx)
            return cnx
        try:
            return getattr(ElastalkConnection, '__default__')
        except AttributeError:
            _cnx = ElastalkConnection()
            return ElastalkConnection.default(cnx=_cnx)


def _encode(doc: Dict) -> str:
    """
    Encode a dictionary (document) as a base64-encoded string.

    :param doc: the dictionary (document) object
    :return: the base64-encoded string
    """
    # Convert the object to a string.
    as_str: str = json.dumps(doc)
    # Encode the string using base64.
    enc_bytes: bytes = base64.b64encode(bytes(as_str, 'utf-8'))
    # Get the ASCII representation of the base64-encoded bytes.
    enc_ascii: bytes = binascii.b2a_base64(enc_bytes, newline=False)
    # Return the string form of the ASCII representation of the base-64
    # encoded bytes.
    return enc_ascii.decode('utf-8')


def _decode(encoded: str) -> Dict:
    """
    Decode an dictionary (document) encoded as a base64-encoded string.

    :param encoded: the base64-encoded string
    :return: the dictionary (document) object
    """
    dec_ascii: bytes = encoded
    dec_ascii_bytes: bytes = binascii.a2b_base64(dec_ascii)
    dec_bytes: bytes = base64.b64decode(dec_ascii_bytes)
    return json.loads(dec_bytes.decode('utf-8'))


class ElastalkMixin(object):
    """
    Mix this into your class to get easy access to the Elasticsearch client.
    """

    @property
    def es_cnx(self) -> ElastalkConnection:
        """
        Get the Elastalk connection object.

        :return: the Elastalk connection object
        """
        try:
            return getattr(self, '__elastalk_connection__')
        except AttributeError:
            _cnx = ElastalkConnection.default()
            setattr(self, '__elastalk_connection__', _cnx)
            return _cnx

    @es_cnx.setter
    def es_cnx(self, cnx: ElastalkConnection):
        """
        Set the mixin's Elastalk connection connection object.

        :param cnx: the object
        """
        setattr(self, '__elastalk_connection__', cnx)

    @property
    def es(self) -> elasticsearch.Elasticsearch:
        """Get the Elasticsearch client."""
        return self.es_cnx.client
