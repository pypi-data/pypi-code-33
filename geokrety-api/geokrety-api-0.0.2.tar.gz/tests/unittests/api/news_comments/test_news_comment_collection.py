# -*- coding: utf-8 -*-

from parameterized import parameterized

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.news_comment import NewsCommentPayload


class TestNewsCommentCollection(BaseTestCase):
    """Test NewsComment collection"""

    @parameterized.expand([
        [None, 200],
        ['admin', 200],
        ['user_1', 200],  # Owner
        ['user_2', 200],
    ])
    @request_context
    def test_news_comment_collection_can_be_accessed_as(self, username, expected):
        news_comments = self.blend_news_comment(user=self.user_1, count=3)
        user = getattr(self, username) if username else None

        response = NewsCommentPayload()\
            .get_collection(user=user, code=expected)\
            .assertCount(3)

        response.data[0].assertHasPublicAttributes(news_comments[0])
        response.data[1].assertHasPublicAttributes(news_comments[1])
        response.data[2].assertHasPublicAttributes(news_comments[2])
