# -*- coding: utf-8 -*-

from .base import BaseResponse
from .collections import BaseCollectionResponse


class UserResponse(BaseResponse):

    def assertHasRelationshipNews(self):
        self.assertHasRelationshipSelf('news', '/v1/users/%s/relationships/news' % self.id)
        self.assertHasRelationshipRelated('news', '/v1/users/%s/news' % self.id)
        return self

    def assertHasRelationshipNewsComments(self):
        self.assertHasRelationshipSelf('news_comments', '/v1/users/%s/relationships/news-comments' % self.id)
        self.assertHasRelationshipRelated('news_comments', '/v1/users/%s/news-comments' % self.id)
        return self

    def assertHasRelationshipNewsSubscriptions(self):
        self.assertHasRelationshipSelf('news_subscriptions', '/v1/users/%s/relationships/news-subscription' % self.id)
        self.assertHasRelationshipRelated('news_subscriptions', '/v1/users/%s/news-subscription' % self.id)
        return self

    def assertHasRelationshipGeokretyOwned(self):
        self.assertHasRelationshipSelf('geokrety_owned', '/v1/users/%s/relationships/geokrety-owned' % self.id)
        self.assertHasRelationshipRelated('geokrety_owned', '/v1/users/%s/geokrety-owned' % self.id)
        return self

    def assertHasRelationshipGeokretyHeld(self):
        self.assertHasRelationshipSelf('geokrety_held', '/v1/users/%s/relationships/geokrety-held' % self.id)
        self.assertHasRelationshipRelated('geokrety_held', '/v1/users/%s/geokrety-held' % self.id)
        return self

    def assertHasRelationshipMoves(self):
        self.assertHasRelationshipSelf('moves', '/v1/users/%s/relationships/moves' % self.id)
        self.assertHasRelationshipRelated('moves', '/v1/users/%s/moves' % self.id)
        return self

    def assertHasRelationshipNewsDatas(self, user_id):
        self.assertHasRelationshipDatas('news', user_id, 'news')
        return self

    def assertHasRelationshipNewsCommentsDatas(self, user_id):
        self.assertHasRelationshipDatas('news_comments', user_id, 'news-comment')
        return self

    def assertHasRelationshipNewsSubscriptionsAuthorDatas(self, user_id):
        self.assertHasRelationshipDatas('news_subscriptions', user_id, 'news-subscription')
        return self

    def assertHasRelationshipGeokretyOwnedDatas(self, user_id):
        self.assertHasRelationshipDatas('geokrety_owned', user_id, 'geokret')
        return self

    def assertHasRelationshipGeokretyHeldDatas(self, user_id):
        self.assertHasRelationshipDatas('geokrety_held', user_id, 'geokret')
        return self

    def assertHasRelationshipMovesDatas(self, user_id):
        self.assertHasRelationshipDatas('moves', user_id, 'move')
        return self

    def assertHasPublicAttributes(self, obj):
        self.assertHasAttribute('name', obj.name)
        self.assertHasAttribute('language', obj.language)
        self.assertHasAttribute('country', obj.country)
        self.assertHasAttributeDateTime('join_datetime', obj.join_datetime)
        self.assertHasRelationshipNews()
        self.assertHasRelationshipNewsComments()
        self.assertHasRelationshipGeokretyOwned()
        self.assertHasRelationshipGeokretyHeld()
        self.assertHasRelationshipMoves()
        with self.assertRaises(AssertionError):
            self.get_attribute('email')
        with self.assertRaises(AssertionError):
            self.get_attribute('password')
        with self.assertRaises(AssertionError):
            self.get_attribute('latitude')
        with self.assertRaises(AssertionError):
            self.get_attribute('longitude')
        with self.assertRaises(AssertionError):
            self.get_attribute('daily_mails')
        with self.assertRaises(AssertionError):
            self.get_attribute('observation_radius')
        with self.assertRaises(AssertionError):
            self.get_attribute('hour')
        with self.assertRaises(AssertionError):
            self.get_attribute('secid')
        with self.assertRaises(AssertionError):
            self.get_attribute('statpic_id')
        with self.assertRaises(AssertionError):
            self.get_attribute('last_update_datetime')
        with self.assertRaises(AssertionError):
            self.get_attribute('last_mail_datetime')
        with self.assertRaises(AssertionError):
            self.get_attribute('last_login_datetime')
        return self

    def assertHasPrivateAttributes(self, obj):
        self.assertHasAttribute('name', obj.name)
        self.assertHasAttribute('language', obj.language)
        self.assertHasAttribute('country', obj.country)
        self.assertHasAttributeDateTime('join_datetime', obj.join_datetime)
        self.assertHasAttribute('email', obj.email)
        with self.assertRaises(AssertionError):
            self.assertHasAttribute('password', obj.password)
        self.assertHasAttribute('latitude', obj.latitude)
        self.assertHasAttribute('longitude', obj.longitude)
        self.assertHasAttribute('daily_mails', obj.daily_mails)
        self.assertHasAttribute('observation_radius', obj.observation_radius)
        self.assertHasAttribute('hour', obj.hour)
        self.assertHasAttribute('secid', obj.secid)
        self.assertHasAttribute('statpic_id', obj.statpic_id)
        self.assertHasAttributeDateTimeOrNone('last_update_datetime', obj.last_update_datetime)
        self.assertHasAttributeDateTimeOrNone('last_mail_datetime', obj.last_mail_datetime)
        self.assertHasAttributeDateTimeOrNone('last_login_datetime', obj.last_login_datetime)
        self.assertHasRelationshipNews()
        self.assertHasRelationshipNewsComments()
        self.assertHasRelationshipGeokretyOwned()
        self.assertHasRelationshipGeokretyHeld()
        self.assertHasRelationshipMoves()
        self.assertHasRelationshipNewsSubscriptions()
        return self


class UsersCollectionResponse(BaseCollectionResponse):

    def __init__(self, data):
        super(UsersCollectionResponse, self).__init__(data)
        datas = []
        for data_ in self.data:
            datas.append(UserResponse(data_))
        self['data'] = datas
