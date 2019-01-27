from app.api.helpers.utilities import dasherize
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema


# Create logical data abstraction
class MovesTypesSchema(Schema):
    class Meta:
        type_ = 'move-type'
        self_view = 'v1.move_type_details'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.moves_type_list'
        inflect = dasherize
        strict = True
        ordered = True

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
