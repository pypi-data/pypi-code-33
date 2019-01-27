# -*- coding: utf-8 -*-

from parameterized import parameterized

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.news import NewsPayload
from tests.unittests.utils.static_test_cases import (EMPTY_TEST_CASES,
                                                     HTML_SUBSET_TEST_CASES_NO_BLANK,
                                                     NO_HTML_TEST_CASES,
                                                     UTF8_TEST_CASES)


class TestNewsCreate(BaseTestCase):
    """Test News create"""

    @request_context
    def test_as_anonymous(self):
        NewsPayload().post(user=None, code=401)

    @request_context
    def test_as_authenticated(self):
        NewsPayload().blend().post(user=self.user_1, code=403)

    @request_context
    def test_as_admin(self):
        NewsPayload().blend().post(user=self.admin)

    @request_context
    def test_field_author_can_be_overrided(self):
        NewsPayload().blend()\
            .set_author(self.user_1)\
            .post(user=self.admin)\
            .assertHasRelationshipAuthorData(self.user_1.id)

    @request_context
    def test_field_author_enforced_to_current_user_if_undefined(self):
        NewsPayload().blend()\
            ._del_relationships('author')\
            .post(user=self.admin)\
            .assertHasRelationshipAuthorData(self.admin.id)

    @request_context
    def test_field_username_can_be_overrided(self):
        NewsPayload().blend()\
            .set_username(self.user_1.name)\
            .post(user=self.admin)\
            .assertHasAttribute('username', self.user_1.name)

    @request_context
    def test_field_username_enforced_to_current_user_if_undefined(self):
        NewsPayload().blend()\
            ._del_attribute('username')\
            .post(user=self.admin)\
            .assertHasAttribute('username', self.admin.name)

    @request_context
    def test_field_title_is_mandatory(self):
        NewsPayload().blend()\
            ._del_attribute('title')\
            .post(user=self.admin, code=422)\
            .assertRaiseJsonApiError('/data/attributes/title')

    @request_context
    def test_field_content_is_mandatory(self):
        NewsPayload().blend()\
            ._del_attribute('content')\
            .post(user=self.admin, code=422)\
            .assertRaiseJsonApiError('/data/attributes/content')

    @parameterized.expand(EMPTY_TEST_CASES)
    @request_context
    def test_field_title_cannot_be_blank(self, title):
        NewsPayload().blend()\
            .set_title(title)\
            .post(user=self.admin, code=422)\
            .assertRaiseJsonApiError('/data/attributes/title')

    @parameterized.expand(EMPTY_TEST_CASES)
    @request_context
    def test_field_content_cannot_be_blank(self, content):
        NewsPayload().blend()\
            .set_content(content)\
            .post(user=self.admin, code=422)\
            .assertRaiseJsonApiError('/data/attributes/content')

    @request_context
    def test_field_creation_datetime_set_automatically(self):
        NewsPayload().blend()\
            ._del_attribute('created-on-datetime')\
            .post(user=self.admin)\
            .assertCreationDateTime()

    @parameterized.expand(UTF8_TEST_CASES)
    @request_context
    def test_field_title_accept_unicode(self, title, expected):
        NewsPayload().blend()\
            .set_title(title)\
            .post(user=self.admin)\
            .assertHasAttribute('title', expected)

    @parameterized.expand(UTF8_TEST_CASES)
    @request_context
    def test_field_content_accept_unicode(self, content, expected):
        NewsPayload().blend()\
            .set_content(content)\
            .post(user=self.admin)\
            .assertHasAttribute('content', expected)

    @parameterized.expand(UTF8_TEST_CASES)
    @request_context
    def test_field_username_accept_unicode(self, username, expected):
        NewsPayload().blend()\
            .set_username(username)\
            .post(user=self.admin)\
            .assertHasAttribute('username', expected)

    @parameterized.expand(NO_HTML_TEST_CASES)
    @request_context
    def test_field_title_doesnt_accept_html(self, title, expected):
        NewsPayload().blend()\
            .set_title(title)\
            .post(user=self.admin)\
            .assertHasAttribute('title', expected)

    @parameterized.expand(HTML_SUBSET_TEST_CASES_NO_BLANK)
    @request_context
    def test_field_content_accept_html_subset(self, content, expected):
        NewsPayload().blend()\
            .set_content(content)\
            .post(user=self.admin)\
            .assertHasAttribute('content', expected)

    @parameterized.expand(NO_HTML_TEST_CASES)
    @request_context
    def test_field_username_doesnt_accept_html(self, username, expected):
        NewsPayload().blend()\
            .set_username(username)\
            .post(user=self.admin)\
            .assertHasAttribute('username', expected)
