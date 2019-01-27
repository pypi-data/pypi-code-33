# -*- coding: utf-8 -*-


from parameterized import parameterized

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.news_comment import NewsCommentPayload


class TestNewsCommentDetails(BaseTestCase):
    """Test NewsComment details"""

    @parameterized.expand([
        [None, 200],
        ['admin', 200],
        ['user_1', 200],  # Owner
        ['user_2', 200],
    ])
    @request_context
    def test_news_comment_details_can_be_accessed_as(self, username, expected):
        user = getattr(self, username) if username else None
        news_comment = self.blend_news_comment()

        NewsCommentPayload().get(
            news_comment.id, user=user, code=expected,
            args={'include': 'news'}
        ).assertHasPublicAttributes(news_comment)
