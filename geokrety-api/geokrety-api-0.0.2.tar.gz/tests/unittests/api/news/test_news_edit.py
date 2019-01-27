# -*- coding: utf-8 -*-

from parameterized import parameterized

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.news import NewsPayload
from tests.unittests.utils.static_test_cases import (EMPTY_TEST_CASES,
                                                     HTML_SUBSET_TEST_CASES_NO_BLANK,
                                                     NO_HTML_TEST_CASES,
                                                     UTF8_TEST_CASES)


class TestNewsEdit(BaseTestCase):
    """Test News edit"""

    @parameterized.expand([
        [None, 401],
        ['admin', 200],
        ['user_1', 403],
        ['user_2', 403],
    ])
    @request_context
    def test_as(self, username, expected):
        user = getattr(self, username) if username else None
        news = self.blend_news()
        NewsPayload().patch(news.id, user=user, code=expected)

    @request_context
    def test_field_title_can_be_edited(self):
        news = self.blend_news()
        NewsPayload()\
            .set_title("New title")\
            .patch(news.id, user=self.admin)\
            .assertHasAttribute('title', "New title")

    @request_context
    def test_field_content_can_be_edited(self):
        news = self.blend_news()
        NewsPayload()\
            .set_content("New content")\
            .patch(news.id, user=self.admin)\
            .assertHasAttribute('content', "New content")

    @request_context
    def test_field_username_can_be_edited(self):
        news = self.blend_news()
        NewsPayload()\
            .set_username("New username")\
            .patch(news.id, user=self.admin)\
            .assertHasAttribute('username', "New username")

    @request_context
    def test_field_author_can_be_edited(self):
        news = self.blend_news()
        NewsPayload()\
            .set_author(self.user_1.id)\
            .patch(news.id, user=self.admin)\
            .assertHasRelationshipAuthorData(self.user_1.id)

    @parameterized.expand(EMPTY_TEST_CASES)
    @request_context
    def test_field_title_cannot_be_blank(self, title):
        news = self.blend_news()
        NewsPayload()\
            .set_title(title)\
            .patch(news.id, user=self.admin, code=422)\
            .assertRaiseJsonApiError('/data/attributes/title')

    @parameterized.expand(EMPTY_TEST_CASES)
    @request_context
    def test_field_content_cannot_be_blank(self, content):
        news = self.blend_news()
        NewsPayload()\
            .set_content(content)\
            .patch(news.id, user=self.admin, code=422)\
            .assertRaiseJsonApiError('/data/attributes/content')

    @request_context
    def test_field_username_defaults_to_connected_username(self):
        news = self.blend_news()
        NewsPayload()\
            .set_username('')\
            .patch(news.id, user=self.admin)\
            .assertHasAttribute('username', self.admin.name)

    @parameterized.expand(UTF8_TEST_CASES)
    @request_context
    def test_field_name_accept_unicode(self, title, expected):
        news = self.blend_news()
        NewsPayload()\
            .set_title(title)\
            .patch(news.id, user=self.admin)\
            .assertHasAttribute('title', expected)

    @parameterized.expand(UTF8_TEST_CASES)
    @request_context
    def test_field_content_accept_unicode(self, content, expected):
        news = self.blend_news()
        NewsPayload()\
            .set_content(content)\
            .patch(news.id, user=self.admin)\
            .assertHasAttribute('content', expected)

    @parameterized.expand(UTF8_TEST_CASES)
    @request_context
    def test_field_username_accept_unicode(self, username, expected):
        news = self.blend_news()
        NewsPayload()\
            .set_username(username)\
            .patch(news.id, user=self.admin)\
            .assertHasAttribute('username', expected)

    @parameterized.expand(NO_HTML_TEST_CASES)
    @request_context
    def test_field_title_doesnt_accept_html(self, title, expected):
        news = self.blend_news()
        NewsPayload()\
            .set_title(title)\
            .patch(news.id, user=self.admin)\
            .assertHasAttribute('title', expected)

    @parameterized.expand(HTML_SUBSET_TEST_CASES_NO_BLANK)
    @request_context
    def test_field_content_accept_html_subset(self, content, expected):
        news = self.blend_news()
        NewsPayload()\
            .set_content(content)\
            .patch(news.id, user=self.admin)\
            .assertHasAttribute('content', expected)

    @parameterized.expand(NO_HTML_TEST_CASES)
    @request_context
    def test_field_username_doesnt_accept_html(self, username, expected):
        news = self.blend_news()
        NewsPayload()\
            .set_username(username)\
            .patch(news.id, user=self.admin)\
            .assertHasAttribute('username', expected)

    @request_context
    def test_geokret_patch_field_are_readonly(self):
        news = self.blend_news(
            comments_count=12,
            last_comment_datetime="2018-09-23T23:15:13",
            created_on_datetime="2018-09-23T23:15:14",
        )
        NewsPayload()\
            ._set_attribute('comments_count', 1000)\
            ._set_attribute('last_comment_datetime', "2018-09-23T23:13:36")\
            ._set_attribute('created_on_datetime', "2018-09-23T23:13:37")\
            .patch(news.id, user=self.admin)\
            .assertHasAttribute('comments-count', news.comments_count)\
            .assertHasAttributeDateTime('last-comment-datetime', news.last_comment_datetime)\
            .assertHasAttributeDateTime('created-on-datetime', news.created_on_datetime)
