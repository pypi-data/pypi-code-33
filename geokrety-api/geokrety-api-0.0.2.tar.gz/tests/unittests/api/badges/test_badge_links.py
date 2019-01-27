# -*- coding: utf-8 -*-

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.user import UserPayload


class TestBadgeLinks(BaseTestCase):
    """Test badge links"""

    @request_context
    def test_links_author(self):
        badge = self.blend_badge()
        UserPayload(_url="/v1/badges/{}/author")\
            .get(badge.id)\
            .assertHasPublicAttributes(badge.author)

    @request_context
    def test_links_author_unexistent(self):
        UserPayload(_url="/v1/badges/{}/author")\
            .get(666, code=404)\
            .assertRaiseJsonApiError('badge_author_id')
