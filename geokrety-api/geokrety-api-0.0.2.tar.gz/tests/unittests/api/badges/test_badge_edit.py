# -*- coding: utf-8 -*-

from parameterized import parameterized

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.badge import BadgePayload
from tests.unittests.utils.static_test_cases import (EMPTY_TEST_CASES,
                                                     HTML_SUBSET_TEST_CASES,
                                                     HTML_SUBSET_TEST_CASES_NO_BLANK,
                                                     UTF8_TEST_CASES)


class TestBadgeEdit(BaseTestCase):
    """Test badge edit"""

    @parameterized.expand([
        [None, 401],
        ['admin', 200],
        ['user_1', 403],  # author
        ['user_2', 403],
    ])
    @request_context
    def test_as_(self, username, expected):
        user = getattr(self, username) if username else None
        badge = self.blend_badge(author=self.admin)
        BadgePayload()\
            .set_name("Some other name")\
            .patch(badge.id, user=user, code=expected)

    @parameterized.expand(EMPTY_TEST_CASES)
    @request_context
    def test_field_name_cannot_be_emptied(self, name):
        badge = self.blend_badge()
        BadgePayload()\
            .set_name(name)\
            .patch(badge.id, user=self.admin, code=422)\
            .assertRaiseJsonApiError('/data/attributes/name')

    @parameterized.expand(HTML_SUBSET_TEST_CASES_NO_BLANK)
    @request_context
    def test_field_name_support_html_subset(self, name, expected):
        badge = self.blend_badge()
        BadgePayload()\
            .set_name(name)\
            .patch(badge.id, user=self.admin)\
            .assertHasName(expected)

    @parameterized.expand(UTF8_TEST_CASES)
    @request_context
    def test_field_name_support_utf8(self, name, expected):
        badge = self.blend_badge()
        BadgePayload()\
            .set_name(name)\
            .patch(badge.id, user=self.admin)\
            .assertHasName(expected)

    @parameterized.expand(EMPTY_TEST_CASES)
    @request_context
    def test_field_description_can_be_empty(self, description):
        badge = self.blend_badge()
        BadgePayload()\
            .blend()\
            .set_description(description)\
            .patch(badge.id, user=self.admin)\
            .assertHasDescription("")

    @parameterized.expand(HTML_SUBSET_TEST_CASES)
    @request_context
    def test_field_description_support_html_subset(self, description, expected):
        badge = self.blend_badge()
        BadgePayload()\
            .blend()\
            .set_description(description)\
            .patch(badge.id, user=self.admin)\
            .assertHasDescription(expected)

    @parameterized.expand(UTF8_TEST_CASES)
    @request_context
    def test_field_description_support_utf8(self, description, expected):
        badge = self.blend_badge()
        BadgePayload()\
            .blend()\
            .set_description(description)\
            .patch(badge.id, user=self.admin)\
            .assertHasDescription(expected)

    @request_context
    def test_relationships_author_can_be_overrided(self):
        badge = self.blend_badge()
        BadgePayload()\
            .set_author(self.user_2)\
            .patch(badge.id, user=self.admin)\
            .assertHasRelationshipAuthorData(self.user_2.id)
