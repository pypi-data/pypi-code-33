# -*- coding: utf-8 -*-

from parameterized import parameterized

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.badge import BadgePayload


class TestBadgeDelete(BaseTestCase):
    """Test badge delete"""

    @parameterized.expand([
        [None, 401],
        ['admin', 200],
        ['user_1', 403],
        ['user_2', 403],
    ])
    @request_context
    def test_as_(self, username, expected):
        user = getattr(self, username) if username else None
        badge = self.blend_badge()
        BadgePayload().delete(badge.id, user=user, code=expected)
