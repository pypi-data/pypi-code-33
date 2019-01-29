# -*- coding: utf-8 -*-

from os import environ as env
from multiprocessing import cpu_count
from marshmallow import Schema, fields, post_load
from jetfactory.utils import yaml_parse


class YamlSettings:
    content = {}

    def __init__(self, files):
        for file in files:
            self.content.update(dict(yaml_parse(file, keys_to_upper=True)).items())

    def __iter__(self):
        for k, v in self.content.items():
            yield k, v


class CoreSchema(Schema):
    listen_host = fields.String(missing='127.0.0.1')
    listen_port = fields.Integer(missing=5000)
    db_url = fields.String(missing=None)
    api_base = fields.String(missing='/api')
    debug = fields.Bool(missing=False)
    workers = fields.Integer(missing=cpu_count())
    logo = fields.String(allow_none=True, missing=None)
    request_max_size = fields.Integer(missing=1000000)
    request_timeout = fields.Integer(missing=60)

    @post_load
    def jet_fmt(self, data):
        """Converts keys to uppercase, to conform with Sanic standards.

        :param data: settings
        :return: settings with uppercase keys
        """

        transformed = {}
        for k, v in data.items():
            transformed[k.upper()] = v

        return transformed


class ApplicationSettings:
    def __init__(self, overrides):
        self._overrides = overrides

    @property
    def merged(self):
        schema = CoreSchema()
        settings = {}

        for name, field in CoreSchema._declared_fields.items():
            nu = name.upper()
            if nu in env:  # Prefer environ
                value = env.get(nu)
                if isinstance(field, fields.Integer):
                    value = int(value)
                if isinstance(field, fields.Boolean):
                    value = str(value).strip().lower() in ['1', 'true', 'yes']

                settings[name] = value
            elif nu in self._overrides:
                settings[name] = self._overrides[nu]

        return schema.load(settings)
