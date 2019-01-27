# -*- coding: utf-8 -*-

from mixer.backend.flask import mixer

from geokrety_api_models import User

from .base import BasePayload


class NewsPayload(BasePayload):
    _url = "/v1/news/{}"
    _url_collection = "/v1/news"
    _response_type = 'NewsResponse'
    _response_type_collection = 'NewsCollectionResponse'

    def __init__(self, *args, **kwargs):
        super(NewsPayload, self).__init__('news', *args, **kwargs)

    def set_title(self, title):
        self._set_attribute('title', title)
        return self

    def set_content(self, content):
        self._set_attribute('content', content)
        return self

    def set_username(self, username):
        self._set_attribute('username', username)
        return self

    def set_author(self, user):
        user_id = user.id if isinstance(user, User) else user
        self._set_relationships('author', 'user', user_id)
        return self

    def set_obj(self, obj):
        self.set_title(obj.title)
        self.set_content(obj.content)
        return self

    def blend(self):
        with mixer.ctx(commit=False):
            self.set_obj(mixer.blend('geokrety_api_models.News'))
            return self
