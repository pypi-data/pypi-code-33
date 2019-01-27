# -*- coding: utf-8 -*-

from parameterized import parameterized

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.badge import BadgePayload


class TestBadgeDetails(BaseTestCase):
    """Test badge details"""

    @parameterized.expand([
        [None],
        ['admin'],
        ['user_1'],
        ['user_2'],
    ])
    @request_context
    def test_as_(self, username):
        user = getattr(self, username) if username else None
        badge = self.blend_badge()
        BadgePayload().get(badge.id, user=user)

    @request_context
    def test_has_public_attributes(self):
        badge = self.blend_badge()
        BadgePayload()\
            .get(badge.id)\
            .assertHasPublicAttributes(badge)
