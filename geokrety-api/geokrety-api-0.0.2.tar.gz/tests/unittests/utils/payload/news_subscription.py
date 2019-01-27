# -*- coding: utf-8 -*-

from geokrety_api_models import News, User

from .base import BasePayload


class NewsSubscriptionPayload(BasePayload):
    _url = "/v1/news-subscriptions/{}"
    _url_collection = "/v1/news-subscriptions"
    _response_type = 'NewsSubscriptionResponse'
    _response_type_collection = 'NewsSubscriptionCollectionResponse'

    def __init__(self, news=None, *args, **kwargs):
        super(NewsSubscriptionPayload, self).__init__('news-subscription', *args, **kwargs)

        if news is not None:
            self.set_news(news)

    def set_user(self, user):
        user_id = user.id if isinstance(user, User) else user
        self._set_relationships('user', 'user', user_id)
        return self

    def set_news(self, news):
        news_id = news.id if isinstance(news, News) else news
        self._set_relationships('news', 'news', news_id)
        return self
