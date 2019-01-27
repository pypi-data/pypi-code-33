# -*- coding: utf-8 -*-

from parameterized import parameterized

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.news_subscription import \
    NewsSubscriptionPayload


class TestNewsSubscriptionEdit(BaseTestCase):
    """Test NewsSubscription edit"""

    @parameterized.expand([
        [None],
        ['admin'],
        ['user_1'],  # Owner
        ['user_2'],
    ])
    @request_context
    def test_subscriptions_cannot_be_edited(self, username):
        user = getattr(self, username) if username else None
        news_subscription = self.blend_news_subscription()

        NewsSubscriptionPayload()\
            .patch(news_subscription.id, user=user, code=405)
