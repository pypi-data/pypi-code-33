# -*- coding: utf-8 -*-

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.badge import BadgePayload


class TestBadgeRelationships(BaseTestCase):
    """Test badge relationships"""

    @request_context
    def test_relationships_author(self):
        badge = self.blend_badge()
        BadgePayload(_url="/v1/badges/{}/relationships/author")\
            .get(badge.id)\
            .assertHasData('user', badge.author.id)
