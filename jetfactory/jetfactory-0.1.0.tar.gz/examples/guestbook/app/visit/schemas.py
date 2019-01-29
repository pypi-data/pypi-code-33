# -*- coding: utf-8 -*-

from marshmallow import Schema, fields
from jetfactory.controller import schemas
from ..visitor.schemas import VisitorSchema
from .._common import _VisitPath


class VisitSchema(Schema):
    id = fields.Integer()
    visitor = fields.Nested(VisitorSchema)
    visited_on = fields.String(attribute='created_on')
    message = fields.String()

    class Meta:
        dump_only = ['id', 'visitor', 'visited_on']
        load_only = ['visit_id', 'visitor_id']


class _VisitCreateSchema(VisitSchema):
    message = fields.String(required=True)
    name = fields.String(required=True)


class Visit(Schema):
    path = fields.Nested(_VisitPath)
    response = fields.Nested(VisitSchema)


class Visits(Schema):
    query = fields.Nested(schemas.QueryParams)
    response = fields.List(fields.Nested(VisitSchema))


class VisitCount(Schema):
    response = fields.Nested(schemas.Count)


class VisitUpdate(Schema):
    path = fields.Nested(_VisitPath)
    body = fields.Nested(VisitSchema)
    response = fields.Nested(VisitSchema)


class VisitDelete(Schema):
    path = fields.Nested(_VisitPath)
    response = fields.Nested(schemas.Delete)


class VisitCreate(Schema):
    """Create a new guestbook entry"""
    body = fields.Nested(_VisitCreateSchema)
    response = fields.Nested(VisitSchema)
