# -*- coding: utf-8 -*-

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.user import UserPayload


class TestUsersEdit(BaseTestCase):
    """Test Users edit"""

    @request_context
    def test_admin_can_edit_all_attributes(self):
        UserPayload()\
            .blend()\
            .patch(self.user_1.id, user=self.admin)
