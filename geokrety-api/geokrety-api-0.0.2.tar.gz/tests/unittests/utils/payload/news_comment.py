# -*- coding: utf-8 -*-

from geokrety_api_models import News, User

from .base import BasePayload


class NewsCommentPayload(BasePayload):
    _url = "/v1/news-comments/{}"
    _url_collection = "/v1/news-comments"
    _response_type = 'NewsCommentResponse'
    _response_type_collection = 'NewsCommentCollectionResponse'

    def __init__(self, news=None, *args, **kwargs):
        super(NewsCommentPayload, self).__init__('news-comment', *args, **kwargs)

        if news is not None:
            self.set_news(news)

        if 'comment' in kwargs:
            self.set_comment(kwargs.pop('comment'))

    def set_comment(self, comment):
        self._set_attribute('comment', comment)
        return self

    def set_author(self, user):
        user_id = user.id if isinstance(user, User) else user
        self._set_relationships('author', 'user', user_id)
        return self

    def set_news(self, news):
        news_id = news.id if isinstance(news, News) else news
        self._set_relationships('news', 'news', news_id)
        return self

    def set_subscribe(self, subscribe):
        self._set_attribute('subscribe', subscribe)
        return self
