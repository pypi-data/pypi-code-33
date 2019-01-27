# -*- coding: utf-8 -*-

from app.api.helpers.data_layers import MOVE_TYPE_DROPPED, MOVE_TYPE_GRABBED
from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.user import UserPayload


class TestUsersDetails(BaseTestCase):
    """Test Users details"""

    @request_context
    def test_user_details_has_public_attributes_as_anonymous_user(self):
        UserPayload()\
            .get(self.user_1.id)\
            .assertHasPublicAttributes(self.user_1)

    @request_context
    def test_user_details_has_public_attributes_as_authenticated_user(self):
        UserPayload()\
            .get(self.user_1.id, user=self.user_2)\
            .assertHasPublicAttributes(self.user_1)

    @request_context
    def test_user_details_has_private_attributes_as_himself(self):
        UserPayload()\
            .get(self.user_1.id, user=self.user_1)\
            .assertHasPrivateAttributes(self.user_1)

    @request_context
    def test_user_details_has_private_attributes_as_admin(self):
        UserPayload()\
            .get(self.user_1.id, user=self.admin)\
            .assertHasPrivateAttributes(self.user_1)

    @request_context
    def test_user_details_has_relationships_data(self):
        news = self.blend_news(author=self.user_1, count=2)
        news_comments = self.blend_news_comment(author=self.user_1, count=2)
        news_subscriptions = self.blend_news_subscription(user=self.user_1, count=2)
        geokrety_owned = self.blend_geokret(owner=self.user_1, count=2)
        geokrety_held = self.blend_geokret(holder=self.user_1, type=MOVE_TYPE_GRABBED, count=2)
        moves = self.blend_move(author=self.user_1, type=MOVE_TYPE_DROPPED, count=2)

        UserPayload()\
            .get(self.user_1.id, user=self.admin, args={
                'include': 'news,news_comments,news_subscriptions,geokrety_owned,geokrety_held,moves'
            })\
            .assertHasRelationshipNewsDatas(news)\
            .assertHasRelationshipNewsCommentsDatas(news_comments)\
            .assertHasRelationshipNewsSubscriptionsAuthorDatas(news_subscriptions)\
            .assertHasRelationshipGeokretyOwnedDatas(geokrety_owned)\
            .assertHasRelationshipGeokretyHeldDatas(geokrety_held)\
            .assertHasRelationshipMovesDatas(moves)
