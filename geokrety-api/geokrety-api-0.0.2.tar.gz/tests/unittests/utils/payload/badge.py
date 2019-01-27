# -*- coding: utf-8 -*-

from mixer.backend.flask import mixer

from geokrety_api_models import User

from .base import BasePayload


class BadgePayload(BasePayload):
    _url = "/v1/badges/{}"
    _url_collection = "/v1/badges"
    _response_type = 'BadgeResponse'
    _response_type_collection = 'BadgeCollectionResponse'

    def __init__(self, *args, **kwargs):
        super(BadgePayload, self).__init__('badge', *args, **kwargs)

    def set_name(self, name):
        self._set_attribute('name', name)
        return self

    def set_description(self, description):
        self._set_attribute('description', description)
        return self

    def set_filename(self, filename):
        self._set_attribute('filename', filename)
        return self

    def set_author(self, user):
        user_id = user.id if isinstance(user, User) else user
        self._set_relationships('author', 'user', user_id)
        return self

    def set_obj(self, obj):
        self.set_name(obj.name)
        self.set_description(obj.description)
        self.set_filename(obj.filename)
        # self.set_created_on_datetime(obj.created_on_datetime)
        return self

    def blend(self, *args, **kwargs):
        with mixer.ctx(commit=False):
            self._blend = mixer.blend('geokrety_api_models.Badge')
            self.set_obj(self._blend)
            return self
