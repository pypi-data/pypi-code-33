# -*- coding: utf-8 -*-

from parameterized import parameterized

from app.models import db
from geokrety_api_models import NewsSubscription
from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.news_comment import NewsCommentPayload
from tests.unittests.utils.static_test_cases import (HTML_SUBSET_TEST_CASES_NO_BLANK,
                                                     UTF8_TEST_CASES)


class TestNewsCommentEdit(BaseTestCase):
    """Test NewsComment edit"""

    @request_context
    def test_authentication_required(self):
        news_comment = self.blend_news_comment()
        NewsCommentPayload().patch(news_comment.id, user=None, code=401)

    @parameterized.expand([
        ['user_1', 200],
        ['user_2', 403],
    ])
    @request_context
    def test_author_can_edit_his_comments(self, username, expected):
        user = getattr(self, username) if username else None
        news_comment = self.blend_news_comment(author=self.user_1)

        response = NewsCommentPayload(comment="New text comment")\
            .patch(news_comment.id, user=user, code=expected)
        if expected == 200:
            response.assertHasComment("New text comment")

    @request_context
    def test_admin_can_edit_any_comments(self):
        news_comment = self.blend_news_comment(author=self.user_1)

        NewsCommentPayload(comment="New text comment")\
            .patch(news_comment.id, user=self.admin)\
            .assertHasComment("New text comment")

    @parameterized.expand(HTML_SUBSET_TEST_CASES_NO_BLANK)
    @request_context
    def test_field_comment_cannot_be_blank(self, comment, expected):
        news_comment = self.blend_news_comment()

        NewsCommentPayload(comment=comment)\
            .patch(news_comment.id, user=self.admin)\
            .assertHasComment(expected)

    @parameterized.expand(UTF8_TEST_CASES)
    @request_context
    def test_field_comment_must_accept_unicode(self, comment, expected):
        news_comment = self.blend_news_comment()

        NewsCommentPayload(comment=comment)\
            .patch(news_comment.id, user=self.admin)\
            .assertHasComment(expected)

    @request_context
    def test_field_author_cannot_be_edited_by_users(self):
        news_comment = self.blend_news_comment(author=self.user_1)

        NewsCommentPayload()\
            .set_author(self.user_2)\
            .patch(news_comment.id, user=self.user_1, code=403)\
            .assertRaiseJsonApiError('/data/relationships/author/data')

    @request_context
    def test_field_author_can_be_edited_by_admin(self):
        news_comment = self.blend_news_comment(author=self.user_1)

        NewsCommentPayload()\
            .set_author(self.user_2)\
            .patch(news_comment.id, user=self.admin)\
            .assertHasRelationshipAuthorData(self.user_2)

    @request_context
    def test_field_creation_date_time_cannot_be_changed(self):
        news_comment = self.blend_news_comment()

        payload = NewsCommentPayload()\
            ._set_attribute('created_on_datetime', "2018-09-27T23:14:19")\
            .patch(news_comment.id, user=self.admin)
        self.assertEqual(payload.created_on_datetime, news_comment.created_on_datetime)

    @request_context
    def test_user_opted_in_to_subscribe_to_the_news(self):
        news_comment = self.blend_news_comment(author=self.user_1, subscribe=False)
        news_subscription = db.session \
            .query(NewsSubscription) \
            .filter(NewsSubscription.user_id == self.user_1.id, NewsSubscription.news_id == news_comment.news.id)
        self.assertEqual(news_subscription.count(), 0)

        NewsCommentPayload()\
            .set_subscribe(True)\
            .patch(news_comment.id, user=self.user_1)
        self.assertEqual(news_subscription.count(), 1)

        payload = NewsCommentPayload().set_subscribe(False)
        payload.patch(news_comment.id, user=self.user_1)
        self.assertEqual(news_subscription.count(), 0)

        # delete again
        payload.patch(news_comment.id, user=self.user_1)
        self.assertEqual(news_subscription.count(), 0)
