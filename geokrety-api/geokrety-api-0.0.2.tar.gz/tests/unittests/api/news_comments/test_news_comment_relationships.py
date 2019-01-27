# -*- coding: utf-8 -*-

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.news_comment import NewsCommentPayload


class TestNewsCommentRelationships(BaseTestCase):
    """Test News Comment relationships"""

    @request_context
    def test_author_relationship(self):
        news_comment = self.blend_news_comment(author=self.user_1)
        NewsCommentPayload(_url="/v1/news-comments/{}/relationships/author")\
            .get(news_comment.id, user=self.user_2)\
            .assertHasData('user', self.user_1.id)

    @request_context
    def test_move_relationship(self):
        news_comment = self.blend_news_comment(author=self.user_1)
        NewsCommentPayload(_url="/v1/news-comments/{}/relationships/news")\
            .get(news_comment.id, user=self.user_2)\
            .assertHasData('news', news_comment.news.id)
