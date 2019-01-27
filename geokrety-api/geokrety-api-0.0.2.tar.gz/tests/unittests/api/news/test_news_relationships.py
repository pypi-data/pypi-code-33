# -*- coding: utf-8 -*-

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.news import NewsPayload


class TestNewsRelationships(BaseTestCase):
    """Test News relationships"""

    @request_context
    def test_news_comments_relationship(self):
        news = self.blend_news(author=self.user_1)
        news_comment = self.blend_news_comment(news=news)
        NewsPayload(_url_collection="/v1/news/{}/relationships/comments".format(news.id))\
            .get_collection()\
            .assertHasDatas('news-comment', [news_comment.id])

    @request_context
    def test_author_relationship(self):
        news = self.blend_news(author=self.user_1)
        NewsPayload(_url="/v1/news/{}/relationships/author")\
            .get(news.id)\
            .assertHasData('user', news.author.id)

    @request_context
    def test_subscribed_users_relationship(self):
        news = self.blend_news(author=self.user_1)
        news_subscription = self.blend_news_subscription(news=news)

        NewsPayload(_url_collection="/v1/news/{}/relationships/subscriptions".format(news.id))\
            .get_collection()\
            .assertHasDatas('news-subscription', [news_subscription.id])
