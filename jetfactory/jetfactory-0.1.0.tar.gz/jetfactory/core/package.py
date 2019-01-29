# -*- coding: utf-8 -*-

import re
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from typing import Type, List
from logging import getLogger
from peewee import Model
from marshmallow import Schema, fields, ValidationError
from jetfactory.controller import BaseController
from jetfactory.service import VanillaService


def validate_meta_name(value):
    if not re.match(r'^[a-zA-Z0-9-]*$', value):
        raise ValidationError(
            f'Invalid name "{value}", package names may only contain alphanumeric and hyphen characters.'
        )


class MetaSchema(Schema):
    name = fields.String(required=True, validate=validate_meta_name)
    description = fields.String(required=True)
    version = fields.Raw(required=True)


class Jetpack:
    def __init__(
            self,
            meta: dict,
            controller: Type[BaseController] = None,
            services: List[VanillaService] = None,
            models: List[Type[Model]] = None,
            **kwargs
    ):
        self.controller = controller
        self.services = services or []
        self.models = models or []

        self.meta = MetaSchema().load(meta)
        self.name = self.meta['name']
        self.path = kwargs.pop('path', f'/{self.name}')

        self.spec = APISpec(
            title=self.name.capitalize(),
            info={
                'description': meta['description'],
            },
            version=meta['version'],
            openapi_version='2.0',
            plugins=[MarshmallowPlugin()]
        )

        if not re.match(r'^/[a-zA-Z0-9-]*$', self.path):
            raise Exception(f'Package {self.name} path must be a valid resource, example: /my-package-1')

        self.log = getLogger(f'pkg.{self.name}')

    def __repr__(self):
        return f'<{self.__class__.__name__} [{self.name}] at {hex(id(self))}>'
