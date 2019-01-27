# -*- coding: utf-8 -*-

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.news import NewsPayload


class TestNewsLinks(BaseTestCase):
    """Test News links"""

    @request_context
    def test_news_details_via_news_comment(self):
        news_comment = self.blend_news_comment()
        NewsPayload(_url="/v1/news-comments/{}/news")\
            .get(news_comment.id, user=self.user_2)\
            .assertHasPublicAttributes(news_comment.news)

    @request_context
    def test_news_details_via_news_comment_unexistent(self):
        self.blend_news_comment()
        NewsPayload(_url="/v1/news-comments/{}/news")\
            .get(666, user=self.user_2, code=404)\
            .assertRaiseJsonApiError('news_comment_id')

    @request_context
    def test_news_details_via_news_subscriptions(self):
        news_subscription = self.blend_news_subscription()
        NewsPayload(_url="/v1/news-subscriptions/{}/news")\
            .get(news_subscription.id, user=self.user_2)\
            .assertHasPublicAttributes(news_subscription.news)

    @request_context
    def test_news_details_via_news_subscriptions_unexistent(self):
        self.blend_news_subscription()
        NewsPayload(_url="/v1/news-subscriptions/{}/news")\
            .get(666, user=self.user_2, code=404)\
            .assertRaiseJsonApiError('news_subscription_id')
