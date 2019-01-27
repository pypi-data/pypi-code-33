# -*- coding: utf-8 -*-

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.news_comment import NewsCommentPayload


class TestNewsCommentLinks(BaseTestCase):
    """Test News Comment links"""

    @request_context
    def test_news_comment_via_news(self):
        news_comment = self.blend_news_comment()
        response = NewsCommentPayload(_url_collection="/v1/news/{}/comments"
                                      .format(news_comment.news.id))\
            .get_collection(user=self.user_2)\
            .assertCount(1)
        response.data[0].assertHasPublicAttributes(news_comment)

    @request_context
    def test_news_comment_via_news_unexistent(self):
        self.blend_news_comment()
        NewsCommentPayload(_url_collection="/v1/news/{}/comments"
                           .format(666))\
            .get_collection(user=self.user_2, code=404)\
            .assertRaiseJsonApiError('news_id')

    @request_context
    def test_news_comment_via_author(self):
        news_comment = self.blend_news_comment(author=self.user_1)
        response = NewsCommentPayload(_url_collection="/v1/users/{}/news-comments"
                                      .format(self.user_1.id))\
            .get_collection(user=self.user_2)\
            .assertCount(1)
        response.data[0].assertHasPublicAttributes(news_comment)

    @request_context
    def test_news_comment_via_author_unexistent(self):
        self.blend_news_comment()
        NewsCommentPayload(_url_collection="/v1/users/{}/news-comments"
                           .format(666))\
            .get_collection(user=self.user_2, code=404)\
            .assertRaiseJsonApiError('author_id')
