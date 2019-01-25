#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This is the module for quering the Policy service.

This module exports classes and methods for interacting with the designated
`Pacifica Policy <https://github.com/pacifica/pacifica-policy>`_ server.
"""
from __future__ import absolute_import
import json
import logging
from collections import namedtuple
from .mjson import generate_namedtuple_encoder, generate_namedtuple_decoder
from .metadata import metadata_encode
from ..common import CommonBase

LOGGER = logging.getLogger(__name__)
QUERY_KEYS = [
    'user',
    'columns',
    'from_table',
    'where'
]
_PolicyQueryData = namedtuple('PolicyQueryData', QUERY_KEYS)
# Set the defaults to None for these attributes
_PolicyQueryData.__new__.__defaults__ = (None,) * len(_PolicyQueryData._fields)


class PolicyQueryData(_PolicyQueryData):
    """
    Policy query data elements for policy query requests.

    This class is a sub-class of the `collections.namedtuple` class. This class is used directly against the
    `Pacifica Uploader Policy <https://github.com/pacifica/pacifica-policy/tree/master/pacifica/policy/uploader/>`_
    endpoint.
    """

    pass


class PolicyQuery(CommonBase):
    """
    Handle quering the policy server.

    Instances of this class represent queries to the designated
    `Pacifica Policy <https://github.com/pacifica/pacifica-policy>`_ server.
    """

    pq_data = None
    user_id = None
    _proto = None
    _addr = None
    _port = None
    _uploader_path = None
    _ingest_path = None
    _uploader_url = None
    _ingest_url = None
    _auth = None

    def set_user(self, user):
        """Set the user for the current PolicyQuery."""
        try:
            self.user_id = int(user)
        except ValueError:
            id_check = PolicyQuery(
                user=-1,
                columns=['_id'],
                from_table='users',
                where={'network_id': user},
                auth=self._auth
            )
            self.user_id = id_check.get_results()[0]['_id']

    def get_user(self):
        """Get the user id."""
        return self.user_id

    def _set_url_from_parts(self):
        """Set the url from the parts in self."""
        for url_part in ['uploader', 'ingest']:
            if not getattr(self, '_{}_url'.format(url_part)):
                url_str = '{}://{}:{}{}'.format(
                    self._proto,
                    self._addr,
                    self._port,
                    getattr(self, '_{}_path'.format(url_part))
                )
                setattr(self, '_{}_url'.format(url_part), url_str)

    def __init__(self, user, *args, **kwargs):
        """
        Set the policy server url and define any data for the query.

        The HTTP end-point for the policy server is
        automatically pulled either from the system environment or from the keyword
        arguments, `**kwargs`.
        """
        self._server_url(
            [
                ('proto', 'http'),
                ('port', 8181),
                ('addr', '127.0.0.1'),
                ('uploader_path', '/uploader'),
                ('ingest_path', '/ingest'),
                ('uploader_url', None),
                ('ingest_url', None)
            ],
            'POLICY',
            kwargs
        )
        self._set_url_from_parts()
        self._setup_requests_session()
        self._auth = kwargs.pop('auth', {})
        LOGGER.debug('Policy URL %s auth %s', self._uploader_url, self._auth)
        # global sential value for userid
        if user != -1:
            self.set_user(user)
            self.pq_data = PolicyQueryData(
                user=self.get_user(), *args, **kwargs)
        else:
            self.pq_data = PolicyQueryData(user=-1, **kwargs)

    def tojson(self):
        """Export self to json."""
        return json.dumps(self.pq_data, cls=PolicyQueryDataEncoder)

    @staticmethod
    def fromjson(json_str):
        """Import json string to self."""
        pq_data = json.loads(json_str, cls=PolicyQueryDataDecoder)
        pq_dict = pq_data._asdict()
        user = pq_dict.pop('user', -1)
        return PolicyQuery(user, **pq_dict)

    def get_results(self):
        """
        Get results from the Policy server for the query.

        This method returns a JSON object that is the result set for a query to the
        `Pacifica Policy <https://github.com/pacifica/pacifica-policy>`_ server, i.e., the
        entities that match the criteria that is represented by the associated instance
        of the ``pacifica.uploader.metadata.PolicyQuery.PolicyQueryData`` class.
        """
        headers = {'content-type': 'application/json'}
        LOGGER.debug('Policy Query Uploader %s', self.tojson())
        reply = self.session.post(
            self._uploader_url, headers=headers, data=self.tojson(), **self._auth)
        LOGGER.debug('Policy Result Uploader %s', reply.content)
        return reply.json()

    def valid_metadata(self, md_obj):
        """
        Check the metadata object against the ingest API.

        This method validates the given instance of ``pacifica.uploader.metadata.MetaData``,
        ``md_obj``, against the
        `Pacifica Policy <https://github.com/pacifica/pacifica-policy>`_ server endpoint.
        """
        headers = {'content-type': 'application/json'}
        LOGGER.debug('Policy Query Ingest %s', metadata_encode(md_obj))
        reply = self.session.post(
            self._ingest_url, headers=headers, data=metadata_encode(md_obj), **self._auth)
        LOGGER.debug('Policy Result Ingest %s', reply.content)
        return reply.json()


#####################################################################
# The from key in the json data is for the policy server.
# It's also a keyword in python so it needs to be handled correctly
#####################################################################
def _mangle_encode(obj):
    """Move the from_table to just from."""
    obj['from'] = obj.pop('from_table')


def _mangle_decode(**json_data):
    """Mangle the decode of the policy query object."""
    json_data['from_table'] = json_data.pop('from')
    return PolicyQueryData(**json_data)


PolicyQueryDataEncoder = generate_namedtuple_encoder(
    PolicyQueryData, _mangle_encode)
PolicyQueryDataDecoder = generate_namedtuple_decoder(_mangle_decode)
