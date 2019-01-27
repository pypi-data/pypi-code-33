# -*- coding: utf-8 -*-

from marshmallow import validates
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

import characterentities
from app.api.helpers.data_layers import MOVE_COMMENT_TYPES_LIST
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.utilities import dasherize


class MoveCommentSchema(Schema):

    @validates('comment')
    def validate_comment_blank(self, data):
        data = characterentities.decode(data).replace('\x00', '').strip()
        if not data:
            raise UnprocessableEntity("Comment cannot be blank",
                                      {'pointer': '/data/attributes/comment'})

    @validates('type')
    def validate_type_value(self, data):
        if data not in MOVE_COMMENT_TYPES_LIST:
            raise UnprocessableEntity("Comment type is invalid",
                                      {'pointer': '/data/attributes/type'})

    class Meta:
        type_ = 'move-comment'
        self_view = 'v1.move_comment_details'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.move_comment_list'
        inflect = dasherize
        ordered = True

    id = fields.Integer(as_string=True, dump_only=True)
    comment = fields.Str(required=True)
    type = fields.Integer(allow_none=False)
    created_on_datetime = fields.Date(dump_only=True)
    updated_on_datetime = fields.Date(dump_only=True)

    author = Relationship(
        attribute='author',
        self_view='v1.move_comment_author',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_details',
        related_view_kwargs={'move_comment_id': '<id>'},
        schema='UserSchema',
        type_='user',
        include_resource_linkage=True,
    )

    move = Relationship(
        attribute='move',
        self_view='v1.move_comment_move',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.move_details',
        related_view_kwargs={'move_comment_id': '<id>'},
        schema='NewsSchema',
        type_='move',
        include_resource_linkage=True,
        required=True,
    )
