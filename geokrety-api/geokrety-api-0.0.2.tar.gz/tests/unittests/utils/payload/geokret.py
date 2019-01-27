# -*- coding: utf-8 -*-

from app.api.helpers.data_layers import GEOKRET_TYPE_TRADITIONAL
from geokrety_api_models import User

from .base import BasePayload


class GeokretPayload(BasePayload):
    _url = "/v1/geokrety/{}"
    _url_collection = "/v1/geokrety"
    _response_type = 'GeokretResponse'
    _response_type_collection = 'GeokretyCollectionResponse'

    def __init__(self, name=None, geokret_type=GEOKRET_TYPE_TRADITIONAL, *args, **kwargs):
        super(GeokretPayload, self).__init__('geokret', *args, **kwargs)

        if name is not None:
            self.set_name(name)

        if geokret_type is not None:
            self.set_geokret_type(geokret_type)

    def set_name(self, name):
        self._set_attribute('name', name)
        return self

    def set_description(self, description):
        self._set_attribute('description', description)
        return self

    def set_born_at_home(self, born_at_home=True):
        self._set_attribute('born_at_home', born_at_home)
        return self

    def set_owner(self, user):
        user_id = user.id if isinstance(user, User) else user
        self._set_relationships('owner', 'user', user_id)
        return self

    def set_holder(self, user):
        user_id = user.id if isinstance(user, User) else user
        self._set_relationships('holder', 'user', user_id)
        return self

    def set_geokret_type(self, geokrety_type):
        self._set_relationships('type', 'geokrety-type', geokrety_type)
        return self


class GeokretyInCachePayload(GeokretPayload):
    _url_collection = "/v1/geokrety/in-cache"
