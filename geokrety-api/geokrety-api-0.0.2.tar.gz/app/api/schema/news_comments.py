from marshmallow import validates
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

import characterentities
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.utilities import dasherize


class NewsCommentSchema(Schema):

    @validates('comment')
    def validate_comment_blank(self, data):
        data = characterentities.decode(data).replace('\x00', '').strip()
        if not data:
            raise UnprocessableEntity("Comment cannot be blank",
                                      {'pointer': '/data/attributes/comment'})

    class Meta:
        type_ = 'news-comment'
        self_view = 'v1.news_comment_details'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.news_comments_list'
        inflect = dasherize
        ordered = True

    id = fields.Integer(as_string=True, dump_only=True)
    comment = fields.Str(required=True)
    icon = fields.Integer(dump_only=True)
    created_on_datetime = fields.Date(dump_only=True)
    subscribe = fields.Boolean()

    author = Relationship(
        attribute='author',
        self_view='v1.news_comments_author',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_details',
        related_view_kwargs={'news_comment_id': '<id>'},
        schema='UserSchema',
        type_='user',
        include_resource_linkage=True,
        # required=True,
    )

    news = Relationship(
        attribute='news',
        self_view='v1.news_comments_news',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.news_details',
        related_view_kwargs={'news_comment_id': '<id>'},
        schema='NewsSchema',
        type_='news',
        required=True,
    )
