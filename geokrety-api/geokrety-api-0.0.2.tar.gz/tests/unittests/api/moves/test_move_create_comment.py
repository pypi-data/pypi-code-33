# -*- coding: utf-8 -*-

from parameterized import parameterized

from app.api.helpers.data_layers import MOVE_TYPE_COMMENT
from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.move import MovePayload


class TestMoveCreateComment(BaseTestCase):
    """Test Move create comment"""

    @parameterized.expand([
        [u'ééééé'],
        [u'<'],
        [u'\x01 '],
        [u'";!'],
        [u'ABC123'],
    ])
    @request_context
    def test_field_tracking_code_must_be_alphanumeric(self, tracking_code):
        geokret = self.blend_geokret()
        MovePayload(MOVE_TYPE_COMMENT, geokret=geokret)\
            .set_coordinates()\
            .set_tracking_code(tracking_code)\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/tracking-code')

    @request_context
    def test_field_tracking_code_must_be_present_if_id_not_given(self):
        geokret = self.blend_geokret()
        MovePayload(MOVE_TYPE_COMMENT, geokret=geokret)\
            ._del_attribute('tracking-code')\
            ._del_attribute('id')\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/tracking-code')

    @request_context
    def test_field_tracking_code_may_be_ommited_if_id_was_given(self):
        geokret = self.blend_geokret()
        MovePayload(MOVE_TYPE_COMMENT, geokret=geokret)\
            .set_geokret_id(geokret.id)\
            ._del_attribute('tracking-code')\
            .post(user=self.user_1)\
            .assertHasRelationshipGeokretData(geokret.id)

    @request_context
    def test_field_id_may_be_ommited_if_tracking_code_was_given(self):
        geokret = self.blend_geokret()
        MovePayload(MOVE_TYPE_COMMENT, geokret=geokret)\
            .set_tracking_code(geokret.tracking_code)\
            .post(user=self.user_1)\
            .assertHasRelationshipGeokretData(geokret.id)
