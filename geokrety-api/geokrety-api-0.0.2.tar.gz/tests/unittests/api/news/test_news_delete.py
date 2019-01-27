# -*- coding: utf-8 -*-

from parameterized import parameterized

from app.models import db
from geokrety_api_models import NewsComment, NewsSubscription
from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.news import NewsPayload


class TestNewsDelete(BaseTestCase):
    """Test News delete"""

    @parameterized.expand([
        [None, 401],
        ['admin', 200],
        ['user_1', 403],
        ['user_2', 403],
    ])
    @request_context
    def test_as(self, username, expected):
        user = getattr(self, username) if username else None
        news = self.blend_news()
        NewsPayload().delete(news.id, user=user, code=expected)

    @request_context
    def test_news_comments_must_be_cleaned(self):
        news = self.blend_news()
        self.blend_news_comment(count=3)
        self.blend_news_comment(news=news, count=5)

        news_comment = db.session \
            .query(NewsComment) \
            .filter(NewsComment.news_id == news.id)
        self.assertEqual(news_comment.count(), 5)

        NewsPayload().delete(news.id, user=self.admin)
        self.assertEqual(news_comment.count(), 0)

    @request_context
    def test_news_subscription_must_be_cleaned(self):
        news = self.blend_news()
        self.blend_news_subscription(count=2)
        self.blend_news_subscription(news=news, count=4)

        news_subscription = db.session \
            .query(NewsSubscription) \
            .filter(NewsSubscription.news_id == news.id)
        self.assertEqual(news_subscription.count(), 4)

        NewsPayload().delete(news.id, user=self.admin)
        self.assertEqual(news_subscription.count(), 0)
