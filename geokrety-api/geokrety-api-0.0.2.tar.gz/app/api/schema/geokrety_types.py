from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.helpers.utilities import dasherize


# Create logical data abstraction
class GeoKretyTypesSchema(Schema):
    class Meta:
        type_ = 'geokrety-type'
        self_view = 'v1.geokrety_type_details'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.geokrety_type_list'
        inflect = dasherize
        strict = True
        ordered = True

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)

    # # Seems not supported by framework
    # geokrety = Relationship(
    #     self_view='v1.geokrety_type_geokret',
    #     self_view_kwargs={'id': '<id>'},
    #     related_view='v1.geokrety_list',
    #     related_view_kwargs={'geokrety_type_id': '<id>'},
    #     many=True,
    #     schema='GeoKretySchema',
    #     type_='geokret',
    # )
