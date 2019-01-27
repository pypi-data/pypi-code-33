# -*- coding: utf-8 -*-

from mixer.backend.flask import mixer

from .base import BasePayload


class UserPayload(BasePayload):
    _url = "/v1/users/{}"
    _url_collection = "/v1/users"
    _response_type = 'UserResponse'
    _response_type_collection = 'UsersCollectionResponse'

    def __init__(self, *args, **kwargs):
        super(UserPayload, self).__init__('user', *args, **kwargs)

    def set_name(self, name):
        self._set_attribute('name', name)
        return self

    def set_is_admin(self, is_admin):
        self._set_attribute('is_admin', is_admin)
        return self

    def set_password(self, password):
        self._set_attribute('password', password)
        return self

    def set_email(self, email):
        self._set_attribute('email', email)
        return self

    def set_daily_mails(self, daily_mails):
        self._set_attribute('daily_mails', daily_mails)
        return self

    def set_ip(self, ip):
        self._set_attribute('ip', ip)
        return self

    def set_language(self, language):
        self._set_attribute('language', language)
        return self

    def set_latitude(self, latitude):
        self._set_attribute('latitude', latitude)
        return self

    def set_longitude(self, longitude):
        self._set_attribute('longitude', longitude)
        return self

    def set_observation_radius(self, observation_radius):
        self._set_attribute('observation_radius', observation_radius)
        return self

    def set_country(self, country):
        self._set_attribute('country', country)
        return self

    def set_hour(self, hour):
        self._set_attribute('hour', hour)
        return self

    def set_statpic_id(self, statpic_id):
        self._set_attribute('statpic_id', statpic_id)
        return self

    def set_join_datetime(self, join_datetime):
        self._set_attribute('join_datetime', join_datetime)
        return self

    def set_last_mail_datetime(self, last_mail_datetime):
        self._set_attribute('last_mail_datetime', last_mail_datetime)
        return self

    def set_last_login_datetime(self, last_login_datetime):
        self._set_attribute('last_login_datetime', last_login_datetime)
        return self

    def set_last_update_datetime(self, last_update_datetime):
        self._set_attribute('last_update_datetime', last_update_datetime)
        return self

    def set_secid(self, secid):
        self._set_attribute('secid', secid)
        return self

    def set_obj(self, obj):
        self.set_name(obj.name)
        self.set_is_admin(obj.is_admin)
        self.set_password(obj.password)
        self.set_email(obj.email)
        self.set_daily_mails(obj.daily_mails)
        self.set_ip(obj.ip)
        self.set_language(obj.language)
        self.set_latitude(obj.latitude)
        self.set_longitude(obj.longitude)
        self.set_observation_radius(obj.observation_radius)
        self.set_country(obj.country)
        self.set_hour(obj.hour)
        self.set_statpic_id(obj.statpic_id)
        self.set_join_datetime(obj.join_datetime)
        self.set_last_mail_datetime(obj.last_mail_datetime)
        self.set_last_login_datetime(obj.last_login_datetime)
        self.set_last_update_datetime(obj.last_update_datetime)
        self.set_secid(obj.secid)
        return self

    def blend(self):
        with mixer.ctx(commit=False):
            self._blend = mixer.blend('geokrety_api_models.User')
            self.set_obj(self._blend)
            return self
