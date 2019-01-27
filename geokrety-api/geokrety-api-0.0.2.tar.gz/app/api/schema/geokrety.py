from marshmallow import validates
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

import characterentities
# import bleach
from app.api.helpers.data_layers import GEOKRETY_TYPES_LIST
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.permission_manager import has_access
from app.api.helpers.utilities import dasherize


class TrackingCodeField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        # Is authenticated?
        if not has_access('auth_required'):
            return None

        if has_access('is_geokret_holder', geokret_id=obj.id) or \
                has_access('is_geokret_owner', geokret_id=obj.id) or \
                has_access('has_touched_geokret', geokret_id=obj.id):
            return obj.tracking_code


class GeokretSchemaPublic(Schema):

    @validates('name')
    def validate_name_blank(self, data):
        data = characterentities.decode(data).replace('\x00', '').strip()
        if not data:
            raise UnprocessableEntity("GeoKrety name cannot be blank",
                                      {'pointer': '/data/attributes/name'})

    @validates('type')
    def validate_geokrety_type_id_valid(self, data):
        if data not in GEOKRETY_TYPES_LIST:
            raise UnprocessableEntity("GeoKrety Type Id is invalid",
                                      {'pointer': '/data/relationships/type'})

    class Meta:
        type_ = 'geokret'
        self_view = 'v1.geokret_details'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.geokrety_list'
        inflect = dasherize
        ordered = True

    id = fields.Integer(as_string=True, dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    missing = fields.Boolean(dump_only=True)
    distance = fields.Integer(dump_only=True)
    archived = fields.Boolean(dump_only=True)
    caches_count = fields.Integer(dump_only=True)
    pictures_count = fields.Integer(dump_only=True)
    average_rating = fields.Float(dump_only=True)
    created_on_datetime = fields.Date(dump_only=True)
    updated_on_datetime = fields.Date(dump_only=True)

    owner = Relationship(
        attribute='owner',
        self_view='v1.geokret_owner',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_details',
        related_view_kwargs={'geokret_owned_id': '<id>'},
        schema='UserSchema',
        type_='user',
        include_resource_linkage=True,
    )

    holder = Relationship(
        attribute='holder',
        self_view='v1.geokret_holder',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_details',
        related_view_kwargs={'geokret_held_id': '<id>'},
        schema='UserSchema',
        type_='user',
        include_resource_linkage=True,
    )

    type = Relationship(
        attribute='type',
        self_view='v1.geokret_type',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.geokrety_type_details',
        related_view_kwargs={'geokret_id': '<id>'},
        schema='GeoKretyTypesSchema',
        type_='geokrety-type',
        include_resource_linkage=True,
    )

    moves = Relationship(
        self_view='v1.geokret_moves',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.moves_list',
        related_view_kwargs={'geokret_id': '<id>'},
        many=True,
        schema='DefaultMoveSchema',
        type_='move',
    )

    last_position = Relationship(
        attribute='last_position',
        self_view='v1.geokret_last_position',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.move_details',
        related_view_kwargs={'geokret_last_position_id': '<id>'},
        schema='DefaultMoveSchema',
        type_='move',
        include_resource_linkage=True,
    )

    last_move = Relationship(
        attribute='last_move',
        self_view='v1.geokret_last_move',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.move_details',
        related_view_kwargs={'geokret_last_move_id': '<id>'},
        schema='DefaultMoveSchema',
        type_='move',
        include_resource_linkage=True,
    )

    tracking_code = TrackingCodeField(attribute='tracking_code')


class GeokretSchema(GeokretSchemaPublic):

    class Meta:
        type_ = 'geokret'
        self_view = 'v1.geokret_details'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.geokrety_list'
        inflect = dasherize
        ordered = True

    tracking_code = fields.Str(dump_only=True)


class GeokretSchemaCreate(GeokretSchema):

    class Meta:
        type_ = 'geokret'
        self_view = 'v1.geokret_details'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.geokrety_list'
        inflect = dasherize
        ordered = True

    born_at_home = fields.Boolean()
