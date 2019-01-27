# -*- coding: utf-8 -*-

from parameterized import parameterized

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.news_subscription import \
    NewsSubscriptionPayload


class TestNewsSubscriptionDetails(BaseTestCase):
    """Test NewsSubscription details"""

    @parameterized.expand([
        [None, 401],
        ['admin', 200],
        ['user_1', 200],  # Owner
        ['user_2', 403],
    ])
    @request_context
    def test_can_be_accessed_as(self, username, expected):
        user = getattr(self, username) if username else None
        news_subscription = self.blend_news_subscription(user=self.user_1)
        NewsSubscriptionPayload()\
            .get(news_subscription.id, user=user, code=expected)

    @parameterized.expand([
        ['admin'],
        ['user_1'],  # Owner
    ])
    @request_context
    def test_has_normal_attributes_as(self, username):
        user = getattr(self, username) if username else None
        news_subscription = self.blend_news_subscription(user=self.user_1)
        NewsSubscriptionPayload()\
            .get(news_subscription.id, user=user)\
            .assertHasPublicAttributes(news_subscription)
