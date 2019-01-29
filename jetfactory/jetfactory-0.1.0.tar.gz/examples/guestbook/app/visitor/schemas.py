# -*- coding: utf-8 -*-

from marshmallow import Schema, fields
from jetfactory.controller import schemas
from .._common import _VisitorPath


class VisitorSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    location = fields.String()


class Visitor(schemas.GetItem):
    path = fields.Nested(_VisitorPath)
    response = fields.Nested(VisitorSchema)


class Visitors(schemas.GetList):
    query = fields.Nested(schemas.QueryParams)
    response = fields.List(fields.Nested(VisitorSchema))
