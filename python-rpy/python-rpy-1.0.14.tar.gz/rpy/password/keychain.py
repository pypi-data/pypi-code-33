# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import os

from rpy.functions.api import fernet, json
from rpy.functions.datastructures import data
from rpy.functions.decorators import to_data
from rpy.functions.functional import first


@to_data
def _parse_settings(opts):

    if not opts:
        raise ValueError('KeyChain must specify at least one named key')

    for name, value in opts.items():
        if not isinstance(value, dict):
            l, p = value
            yield name, data(location = os.path.expanduser(l), password = p)
        else:
            yield name, data(location = os.path.expanduser(value['location']), password = value['password'])


class KeyChain(object):

    serializer = json
    cypher = fernet

    def __init__(self, **opts):
        self.settings = _parse_settings(opts)
        self.default_name = first(self.settings.keys())

    def loads(self, payload, password):
        return self.serializer.loads(
            self.cypher.loads(payload, password=password))

    def dumps(self, payload, password):
        return self.cypher.dumps(
            self.serializer.dumps(payload), password=password)

    def get_location(self, secret_name, *paths):
        return os.path.join(self.settings[secret_name or self.default_name].location,
                            *paths)

    def get_password(self, secret_name, *paths):
        return self.settings[secret_name or self.default_name].password

    def get_secret(self, key, secret_name=None):
        try:
            with open(self.get_location(secret_name, key), 'rb') as f:
                return self.loads(
                    f.read(), 
                    password=self.get_password(secret_name)
                )
        except FileNotFoundError:
            pass

    def delete_secret(self, key, secret_name=None):
        try:
            os.remove(self.get_location(secret_name, key))
        except FileNotFoundError:
            pass

    def set_secret(self, key, payload, secret_name=None):
        with open(self.get_location(secret_name, key), 'wb') as f:
            f.write(
                self.dumps(
                    payload, 
                    password=self.get_password(secret_name)
                )
            )

        return payload

    def list_secrets(self, secret_name=None):
        try:
            for file in os.scandir(self.get_location(secret_name)):
                if not file.is_dir() and not file.name.startswith('.'):
                    yield file.name
        except FileNotFoundError:
            pass
