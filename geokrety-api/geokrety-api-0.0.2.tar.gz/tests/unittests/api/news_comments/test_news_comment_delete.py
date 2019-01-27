# -*- coding: utf-8 -*-

from parameterized import parameterized

from app.models import db
from geokrety_api_models import NewsSubscription
from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.news_comment import NewsCommentPayload


class TestNewsCommentDelete(BaseTestCase):
    """Test NewsComment delete"""

    @parameterized.expand([
        [None, 401],
        ['admin', 200],
        ['user_1', 200],
        ['user_2', 403],
    ])
    @request_context
    def test_as(self, username, expected):
        user = getattr(self, username) if username else None
        news = self.blend_news()
        news_comment = NewsCommentPayload(news, comment="Some comment")\
            .post(user=self.user_1)
        NewsCommentPayload().delete(news_comment.id, user=user, code=expected)

    @request_context
    def test_news_comments_counter_must_be_decremented(self):
        news = self.blend_news()
        news_comment = NewsCommentPayload(news, comment="Some comment")\
            .post(user=self.admin)
        self.assertEqual(news.comments_count, 1)
        NewsCommentPayload().delete(news_comment.id, user=self.admin)
        self.assertEqual(news.comments_count, 0)

    @request_context
    def test_news_subscription_must_be_cleaned(self):
        news = self.blend_news()
        news_comment_payload = NewsCommentPayload(news, comment="Some comment")\
            .set_subscribe(True)

        news_comment = news_comment_payload.post(user=self.admin)
        news_comment_payload.post(user=self.user_1)
        self.assertEqual(news.comments_count, 2)

        news_subscription = db.session \
            .query(NewsSubscription) \
            .filter(
                NewsSubscription.user_id == self.admin.id,
                NewsSubscription.news_id == news.id
            )
        self.assertEqual(news_subscription.count(), 1)
        self.assertTrue(news_subscription.first().subscribed)

        news_comment_payload.delete(news_comment.id, user=self.admin)
        self.assertEqual(news.comments_count, 1)
        self.assertEqual(news_subscription.count(), 0)
