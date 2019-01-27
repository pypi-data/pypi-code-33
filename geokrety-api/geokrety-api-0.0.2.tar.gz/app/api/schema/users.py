
from marshmallow import post_dump, pre_load, validate, validates
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.helpers.data_layers import COUNTRIES, LANGUAGES
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.permission_manager import has_access
from app.api.helpers.utilities import dasherize
from app.views.regex import REG_LATITUDE, REG_LONGITUDE
from geokrety_api_models import User


def drop_private_attributes(item):
    item['attributes'].pop('email', None)
    item['attributes'].pop('password', None)
    item['attributes'].pop('latitude', None)
    item['attributes'].pop('longitude', None)
    item['attributes'].pop('daily-mails', None)
    item['attributes'].pop('observation-radius', None)
    item['attributes'].pop('hour', None)
    item['attributes'].pop('secid', None)
    item['attributes'].pop('statpic-id', None)
    item['attributes'].pop('last-update-datetime', None)
    item['attributes'].pop('last-mail-datetime', None)
    item['attributes'].pop('last-login-datetime', None)
    return item


class EmailOrBlank(fields.Email):
    """Field that serializes to a title case string and deserializes
    to a lower case string.
    """

    def _serialize(self, value, attr, obj, **kwargs):
        if value == '' or value is None:
            return value
        return super(EmailOrBlank, self)._serialize(value, attr, obj, **kwargs)

    # def _deserialize(self, value, attr, data, **kwargs):
    #     return value.lower()


class UserSchema(Schema):

    @post_dump(pass_many=True)
    def remove_private_attributes(self, data, many):
        if many:
            for item in data['data']:
                if not has_access('is_user_itself', user_id=item['id']):
                    item = drop_private_attributes(item)
            return data
        if not has_access('is_user_itself', user_id=data['data']['id']):
            data['data'] = drop_private_attributes(data['data'])
        return data

    @pre_load()
    def set_default_language(self, data):
        if 'language' not in data or not data['language']:
            data['language'] = 'en'

    @pre_load()
    def set_default_country(self, data):
        if 'country' not in data or not data['country']:
            data['country'] = None

    @validates('name')
    def validate_username_uniqueness(self, data):
        if User.query.filter_by(name=data).count():
            raise UnprocessableEntity("Username already taken",
                                      {'pointer': '/data/attributes/name'})

    @validates('email')
    def validate_email_uniqueness(self, data):
        if User.query.filter_by(email=data).count():
            raise UnprocessableEntity("Email already taken",
                                      {'pointer': '/data/attributes/email'})

    @validates('language')
    def validate_language_value(self, data):
        if data not in LANGUAGES.keys():
            raise UnprocessableEntity("Invalid language",
                                      {'pointer': '/data/attributes/language'})

    @validates('country')
    def validate_country_value(self, data):
        if data is not None and data not in COUNTRIES.keys():
            raise UnprocessableEntity("Invalid country",
                                      {'pointer': '/data/attributes/country'})

    @validates('observation_radius')
    def validate_observation_radius_value(self, data):
        if data is None:
            return
        if data < 0 or data > 10:
            raise UnprocessableEntity("Observation radius must be between 0 and 10",
                                      {'pointer': '/data/attributes/observation-radius'})

    @validates('hour')
    def validate_hour_value(self, data):
        if data is None:
            return
        if data < 0 or data > 23:
            raise UnprocessableEntity("Hour must be between 0 and 23",
                                      {'pointer': '/data/attributes/hour'})

    @validates('latitude')
    def validate_latitude_valid(self, data):
        if data is not None and not REG_LATITUDE.match(str(data)):
            raise UnprocessableEntity("Latitude is invalid",
                                      {'pointer': '/data/attributes/latitude'})

    @validates('longitude')
    def validate_longitude_valid(self, data):
        if data is not None and not REG_LONGITUDE.match(str(data)):
            raise UnprocessableEntity("Longitude is invalid",
                                      {'pointer': '/data/attributes/longitude'})

    class Meta:
        type_ = 'user'
        self_view = 'v1.user_details'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.users_list'
        inflect = dasherize
        ordered = True

    id = fields.Integer(as_string=True, dump_only=True)
    name = fields.Str(required=True)
    language = fields.Str(validate=validate.Length(max=2), allow_none=True)
    country = fields.Str(allow_none=True)
    join_datetime = fields.Date(dump_only=True)

    email = EmailOrBlank(required=True)
    password = fields.Str(load_only=True, required=True)
    latitude = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)
    daily_mails = fields.Boolean(allow_none=True)
    observation_radius = fields.Integer(allow_none=True)
    hour = fields.Integer(allow_none=True)
    secid = fields.Str(dump_only=True)
    # ip = fields.Str(dump_only=True)  # Do not use this field a all GDPR?
    statpic_id = fields.Integer()
    last_update_datetime = fields.Date(dump_only=True)
    last_mail_datetime = fields.Date(dump_only=True)
    last_login_datetime = fields.Date(dump_only=True)

    # statpic = Relationship()
    news = Relationship(
        self_view='v1.user_news',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.news_list',
        related_view_kwargs={'author_id': '<id>'},
        many=True,
        schema='NewsSchema',
        type_='news'
    )

    news_comments = Relationship(
        self_view='v1.user_news_comments',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.news_comments_list',
        related_view_kwargs={'author_id': '<id>'},
        many=True,
        schema='NewsCommentSchema',
        type_='news-comment',
        # include_resource_linkage=True
    )

    news_subscriptions = Relationship(
        self_view='v1.user_news_subscriptions',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.news_subscriptions_list',
        related_view_kwargs={'user_id': '<id>'},
        many=True,
        schema='NewsSubscriptionSchema',
        type_='news-subscription',
        # include_resource_linkage=True
    )

    geokrety_owned = Relationship(
        self_view='v1.user_geokrety_owned',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.geokrety_list',
        related_view_kwargs={'owner_id': '<id>'},
        many=True,
        schema='GeokretSchemaPublic',
        type_='geokret',
    )

    geokrety_held = Relationship(
        self_view='v1.user_geokrety_held',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.geokrety_list',
        related_view_kwargs={'holder_id': '<id>'},
        many=True,
        schema='GeokretSchemaPublic',
        type_='geokret',
    )

    moves = Relationship(
        self_view='v1.user_moves',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.moves_list',
        related_view_kwargs={'user_id': '<id>'},
        many=True,
        schema='MoveWithCoordinatesSchema',
        type_='move',
    )

    moves_comments = Relationship(
        self_view='v1.user_news_comments',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.move_comment_list',
        related_view_kwargs={'author_id': '<id>'},
        many=True,
        schema='MoveCommentSchema',
        type_='move-comment',
        # include_resource_linkage=True
    )
