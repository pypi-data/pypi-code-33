# -*- coding: utf-8 -*-

from parameterized import parameterized

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.move import MovePayload
from tests.unittests.utils.static_test_cases import EMPTY_TEST_CASES


class _BaseTestMoveCreate(BaseTestCase):
    """Base tests with optional coordinates"""

    move_type = None

    def setUp(self):
        assert self.move_type is not None
        super(_BaseTestMoveCreate, self).setUp()

    @parameterized.expand([
        [u'ééééé'],
        [u'<'],
        [u'\x01 '],
        [u'";!'],
    ])
    @request_context
    def test_field_tracking_code_must_be_alphanumeric(self, tracking_code):
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret=geokret)\
            .set_coordinates()\
            .set_tracking_code(tracking_code)\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/tracking-code')

    @request_context
    def test_field_tracking_code_must_be_present(self):
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret=geokret)\
            ._del_attribute('tracking-code')\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/tracking-code')

    @parameterized.expand(EMPTY_TEST_CASES)
    @request_context
    def test_field_tracking_code_cannot_be_blank(self, tracking_code):
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret=geokret)\
            .set_tracking_code(tracking_code)\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/tracking-code')
