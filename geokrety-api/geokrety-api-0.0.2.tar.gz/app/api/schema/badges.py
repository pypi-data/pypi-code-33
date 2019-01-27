from marshmallow import validates
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

import characterentities
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.utilities import dasherize


# Create logical data abstraction
class BadgeSchema(Schema):

    @validates('name')
    def validate_title_blank(self, data):
        data = characterentities.decode(data).replace('\x00', '').strip()
        if not data:
            raise UnprocessableEntity("Badge name cannot be blank",
                                      {'pointer': '/data/attributes/name'})

    class Meta:
        type_ = 'badge'
        self_view = 'v1.badge_details'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.badges_list'
        inflect = dasherize
        strict = True
        ordered = True
        dateformat = "%Y-%m-%dT%H:%M:%S"

    id = fields.Integer(as_string=True, dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    filename = fields.Str(dump_only=True)
    created_on_datetime = fields.Date(dump_only=True)
    upload_url = fields.Str(dump_only=True)

    author = Relationship(
        attribute='author',
        self_view='v1.badge_author',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_details',
        related_view_kwargs={'badge_author_id': '<id>'},
        schema='UserSchema',
        type_='user',
        include_resource_linkage=True
    )
