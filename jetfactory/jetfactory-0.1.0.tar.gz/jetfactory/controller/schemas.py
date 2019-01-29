# -*- coding: utf-8 -*-

from marshmallow import fields, Schema, validate


class GetItem(Schema):
    """Get single record"""


class GetList(Schema):
    """Get multiple records"""


class QueryParams(GetList):
    """Get multiple records with filters"""

    _limit = fields.Integer(missing=100, validate=validate.Range(min=0))
    _offset = fields.Integer(missing=0, validate=validate.Range(min=0))
    _sort = fields.String(missing='')


class Count(Schema):
    """Returns number of records"""

    count = fields.Integer()


class Create(Schema):
    """Create a record using the provided payload"""


class Update(Schema):
    """Updates matching record with the provided payload"""


class Delete(Schema):
    """Deletes a record"""

    deleted = fields.Integer()
