# -*- coding: utf-8 -*-

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.user import UserPayload


class TestUsersLinks(BaseTestCase):
    """Test Users details links"""

    @request_context
    def test_user_details_via_news_author(self):
        news = self.blend_news(author=self.user_1)
        payload = UserPayload(_url="/v1/news/{}/author")

        payload.get(news.id, user=self.user_2)\
            .assertHasPublicAttributes(news.author)
        payload.get(news.id, user=news.author)\
            .assertHasPrivateAttributes(news.author)
        payload.get(666, user=news.author, code=404)\
            .assertRaiseJsonApiError('news_id')

    @request_context
    def test_user_details_via_news_comment_author(self):
        news_comment = self.blend_news_comment(author=self.user_1)
        payload = UserPayload(_url="/v1/news-comments/{}/author")

        payload.get(news_comment.id, user=self.user_2)\
            .assertHasPublicAttributes(news_comment.author)
        payload.get(news_comment.id, user=news_comment.author)\
            .assertHasPrivateAttributes(news_comment.author)
        payload.get(666, user=news_comment.author, code=404)\
            .assertRaiseJsonApiError('news_comment_id')

    @request_context
    def test_user_details_via_geokret_owner(self):
        geokret = self.blend_geokret(owner=self.user_1)
        payload = UserPayload(_url="/v1/geokrety/{}/owner")

        payload.get(geokret.id, user=self.user_2)\
            .assertHasPublicAttributes(geokret.owner)
        payload.get(geokret.id, user=geokret.owner)\
            .assertHasPrivateAttributes(geokret.owner)
        payload.get(666, user=geokret.owner, code=404)\
            .assertRaiseJsonApiError('geokret_owned_id')

    @request_context
    def test_user_details_via_geokret_holder(self):
        geokret = self.blend_geokret(holder=self.user_1)
        payload = UserPayload(_url="/v1/geokrety/{}/holder")

        payload.get(geokret.id, user=self.user_2)\
            .assertHasPublicAttributes(geokret.holder)
        payload.get(geokret.id, user=geokret.holder)\
            .assertHasPrivateAttributes(geokret.holder)
        payload.get(666, user=geokret.holder, code=404)\
            .assertRaiseJsonApiError('geokret_held_id')

    @request_context
    def test_user_details_via_move_author(self):
        move = self.blend_move(author=self.user_1)
        payload = UserPayload(_url="/v1/moves/{}/author")

        payload.get(move.id, user=self.user_2)\
            .assertHasPublicAttributes(move.author)
        payload.get(move.id, user=move.author)\
            .assertHasPrivateAttributes(move.author)
        payload.get(666, user=move.author, code=404)\
            .assertRaiseJsonApiError('move_id')

    @request_context
    def test_user_details_via_news_subscription(self):
        news_subscription = self.blend_news_subscription(user=self.user_1)
        payload = UserPayload(_url="/v1/news-subscriptions/{}/user")

        payload.get(news_subscription.id, user=self.user_2)\
            .assertHasPublicAttributes(news_subscription.user)
        payload.get(news_subscription.id, user=news_subscription.user)\
            .assertHasPrivateAttributes(news_subscription.user)
        payload.get(666, user=news_subscription.user, code=404)\
            .assertRaiseJsonApiError('news_subscription_id')

    @request_context
    def test_user_details_via_move_comment(self):
        move_comment = self.blend_move_comment()
        payload = UserPayload(_url="/v1/moves-comments/{}/author")

        payload.get(move_comment.id)\
            .assertHasPublicAttributes(move_comment.author)
        payload.get(666, code=404)\
            .assertRaiseJsonApiError('move_comment_id')
