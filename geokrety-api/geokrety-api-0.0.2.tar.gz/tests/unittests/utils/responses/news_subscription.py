# -*- coding: utf-8 -*-

from geokrety_api_models import News, User

from .base import BaseResponse
from .collections import BaseCollectionResponse


class NewsSubscriptionResponse(BaseResponse):

    def assertHasRelationshipUser(self):
        self.assertHasRelationshipSelf('user', '/v1/news-subscriptions/%s/relationships/user' % self.id)
        self.assertHasRelationshipRelated('user', '/v1/news-subscriptions/%s/user' % self.id)
        return self

    def assertHasRelationshipNews(self):
        self.assertHasRelationshipSelf('news', '/v1/news-subscriptions/%s/relationships/news' % self.id)
        self.assertHasRelationshipRelated('news', '/v1/news-subscriptions/%s/news' % self.id)
        return self

    def assertHasRelationshipUserData(self, user):
        user_id = user.id if isinstance(user, User) else user
        self.assertHasRelationshipData('user', user_id, 'user')
        return self

    def assertHasRelationshipNewsData(self, news):
        news_id = news.id if isinstance(news, News) else news
        self.assertHasRelationshipData('news', news_id, 'news')
        return self

    def assertHasPublicAttributes(self, obj):
        self.assertDateTimePresent('subscribed-on-datetime')
        self.assertHasAttributeDateTime('subscribed-on-datetime', obj.subscribed_on_datetime)
        self.assertHasRelationshipUser()
        self.assertHasRelationshipNews()
        return self


class NewsSubscriptionCollectionResponse(BaseCollectionResponse):

    def __init__(self, data):
        super(NewsSubscriptionCollectionResponse, self).__init__(data)
        datas = []
        for data_ in self.data:
            datas.append(NewsSubscriptionResponse(data_))
        self['data'] = datas
