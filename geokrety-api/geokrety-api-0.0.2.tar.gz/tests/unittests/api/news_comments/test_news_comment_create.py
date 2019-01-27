# -*- coding: utf-8 -*-


from parameterized import parameterized

from app.models import db
from geokrety_api_models import NewsSubscription
from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.news_comment import NewsCommentPayload
from tests.unittests.utils.static_test_cases import (EMPTY_TEST_CASES,
                                                     HTML_SUBSET_TEST_CASES_NO_BLANK,
                                                     UTF8_TEST_CASES)


class TestNewsCommentCreate(BaseTestCase):
    """Test NewsComment create"""

    @request_context
    def test_can_be_posted_as_anonymous(self):
        NewsCommentPayload().post(user=None, code=401)

    @parameterized.expand([
        ['admin', 201],
        ['user_1', 201],
        ['user_2', 201],
    ])
    @request_context
    def test_can_be_posted_as(self, username, expected):
        user = getattr(self, username) if username else None
        news = self.blend_news()
        NewsCommentPayload(news, comment="Some comment")\
            .post(user=user, code=expected)

    @request_context
    def test_field_author_defaults_to_current_user(self):
        news = self.blend_news()
        NewsCommentPayload(news, comment="Some comment")\
            .post(user=self.user_1)\
            .assertHasRelationshipAuthorData(self.user_1)

    @request_context
    def test_field_author_defaults_to_current_user_even_for_admin(self):
        news = self.blend_news()
        NewsCommentPayload(news, comment="Some comment")\
            .post(user=self.admin)\
            .assertHasRelationshipAuthorData(self.admin)

    @request_context
    def test_field_author_must_be_current_user(self):
        news = self.blend_news()
        NewsCommentPayload(news, comment="Some comment")\
            .set_author(self.user_2)\
            .post(user=self.user_1, code=403)\
            .assertRaiseJsonApiError('/data/relationships/author/data')

    @request_context
    def test_field_author_can_be_overrided_by_admin(self):
        news = self.blend_news()
        NewsCommentPayload(news, comment="Some comment")\
            .set_author(self.user_2)\
            .post(user=self.admin)\
            .assertHasRelationshipAuthorData(self.user_2)

    @request_context
    def test_field_creation_datetime_set_automatically(self):
        news = self.blend_news()
        NewsCommentPayload(news, comment="Some comment")\
            .set_author(self.user_1)\
            .post(user=self.admin)\
            .assertCreationDateTime()

    @request_context
    def test_field_comment_must_be_present(self):
        news = self.blend_news()
        NewsCommentPayload(news)\
            .post(user=self.admin, code=422)\
            .assertRaiseJsonApiError('/data/attributes/comment')

    @parameterized.expand(EMPTY_TEST_CASES)
    @request_context
    def test_field_comment_cannot_be_blank(self, comment):
        news = self.blend_news()
        NewsCommentPayload(news)\
            .set_comment(comment)\
            .post(user=self.admin, code=422)\
            .assertRaiseJsonApiError('/data/attributes/comment')

    @parameterized.expand(UTF8_TEST_CASES)
    @request_context
    def test_field_comment_must_accept_unicode(self, comment, expected=None):
        news = self.blend_news()
        NewsCommentPayload(news)\
            .set_comment(comment)\
            .post(user=self.admin)\
            .assertHasComment(expected)

    @parameterized.expand(HTML_SUBSET_TEST_CASES_NO_BLANK)
    @request_context
    def test_field_comment_must_accept_html_subset(self, comment, expected):
        news = self.blend_news()
        NewsCommentPayload(news)\
            .set_comment(comment)\
            .post(user=self.admin)\
            .assertHasComment(expected)

    @request_context
    def test_user_opted_in_to_subscribe_to_the_news(self):
        news = self.blend_news()
        NewsCommentPayload(news, comment="Some comment")\
            .set_subscribe(True)\
            .post(user=self.user_1)\
            .assertAttributeNotPresent('subscribe')

        news_subscription = db.session \
            .query(NewsSubscription) \
            .filter(NewsSubscription.user_id == self.user_1.id, NewsSubscription.news_id == news.id)
        self.assertEqual(news_subscription.count(), 1)
        self.assertTrue(news_subscription.first().subscribed)

    @request_context
    def test_user_did_not_opted_in_to_subscribe_to_the_news(self):
        news = self.blend_news()
        NewsCommentPayload(news, comment="Some comment")\
            .set_subscribe(False)\
            .post(user=self.user_1)\
            .assertAttributeNotPresent('subscribe')

        news_subscription = db.session \
            .query(NewsSubscription) \
            .filter(NewsSubscription.user_id == self.user_1.id, NewsSubscription.news_id == news.id)
        self.assertEqual(news_subscription.count(), 0)

    @request_context
    def test_news_comments_counter_must_be_incremented(self):
        news = self.blend_news()
        self.assertEqual(news.comments_count, 0)
        NewsCommentPayload(news, comment="Some comment")\
            .post(user=self.user_1)

        self.assertEqual(news.comments_count, 1)
