# -*- coding: utf-8 -*-

from parameterized import parameterized

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.news_subscription import \
    NewsSubscriptionPayload


class TestNewsSubscriptionDelete(BaseTestCase):
    """Test NewsSubscription delete"""

    @parameterized.expand([
        [None, 401],
        ['admin', 200],
        ['user_1', 200],
        ['user_2', 403],
    ])
    @request_context
    def test_unsubscribe_as(self, username, expected):
        user = getattr(self, username) if username else None
        news_subscription = self.blend_news_subscription(user=self.user_1)

        NewsSubscriptionPayload()\
            .delete(news_subscription.id, user=user, code=expected)
