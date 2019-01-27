# -*- coding: utf-8 -*-

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.news_subscription import \
    NewsSubscriptionPayload


class TestNewsSubscriptionCollection(BaseTestCase):
    """Test NewsSubscription collection"""

    @request_context
    def test_admin_can_list_all_subscriptions(self):
        news_subscriptions = self.blend_news_subscription(count=3)
        response = NewsSubscriptionPayload()\
            .get_collection(user=self.admin)\
            .assertCount(3)
        response.data[0].assertHasPublicAttributes(news_subscriptions[0])
        response.data[1].assertHasPublicAttributes(news_subscriptions[1])
        response.data[2].assertHasPublicAttributes(news_subscriptions[2])

    @request_context
    def test_subscriber_can_list_his_subscriptions(self):
        self.blend_news_subscription(count=3)
        news_subscription = self.blend_news_subscription(user=self.user_1)
        response = NewsSubscriptionPayload()\
            .get_collection(user=self.user_1)\
            .assertCount(1)
        response.data[0].assertHasPublicAttributes(news_subscription)

    @request_context
    def test_authenticated_cannot_list_others_subscriptions(self):
        self.blend_news_subscription(count=3)
        self.blend_news_subscription(user=self.user_1)
        NewsSubscriptionPayload()\
            .get_collection(user=self.user_2)\
            .assertCount(0)

    @request_context
    def test_anonymous_cannot_list_any_subscriptions(self):
        self.blend_news_subscription(count=3)
        NewsSubscriptionPayload()\
            .get_collection(user=None, code=401)
