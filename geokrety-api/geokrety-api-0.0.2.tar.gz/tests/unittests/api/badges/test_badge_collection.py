# -*- coding: utf-8 -*-

from parameterized import parameterized

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.badge import BadgePayload


class TestBadgeCollection(BaseTestCase):
    """Test badge collection"""

    @parameterized.expand([
        [None],
        ['admin'],
        ['user_1'],
        ['user_2'],
    ])
    @request_context
    def test_has_public_attributes_as_(self, username):
        user = getattr(self, username) if username else None
        badges = self.blend_badge(count=3)
        response = BadgePayload()\
            .get_collection(user=user)\
            .assertCount(3)
        response.data[0].assertHasPublicAttributes(badges[0])
        response.data[1].assertHasPublicAttributes(badges[1])
        response.data[2].assertHasPublicAttributes(badges[2])

    @request_context
    def test_order_by(self):
        badges = self.blend_badge(count=3)

        response = BadgePayload()\
            .get_collection(args={'sort': '-id'})\
            .assertCount(3)
        response.data[0].assertHasId(badges[2].id)
        response.data[1].assertHasId(badges[1].id)
        response.data[2].assertHasId(badges[0].id)

    @request_context
    def test_pagination(self):
        badges = self.blend_badge(count=3)

        response = BadgePayload()\
            .get_collection(args={'page[size]': '1'})\
            .assertCount(3)\
            .assertHasPaginationLinks()
        self.assertEqual(len(response['data']), 1)

        response.data[0].assertHasId(badges[0].id)

    @request_context
    def test_filter_by_author(self):
        user = self.blend_user(name="someone")
        badge = self.blend_badge(author=user)
        self.blend_badge(count=3)

        response = BadgePayload()\
            .get_collection(args={'filter': '[{"name":"author__name","op":"has","val":"%s"}]' % user.name})\
            .assertCount(1)
        response.data[0].assertHasPublicAttributes(badge)

        self.blend_badge(count=3)
        response = BadgePayload()\
            .get_collection(args={'filter': '[{"name":"author__id","op":"has","val":"%s"}]' % user.id})\
            .assertCount(1)
        response.data[0].assertHasPublicAttributes(badge)

        response = BadgePayload()\
            .get_collection(args={'filter': '[{"name":"author","op":"has","val":{"name":"name","op":"like","val":"some%"}}]'})\
            .assertCount(1)
        response.data[0].assertHasPublicAttributes(badge)
