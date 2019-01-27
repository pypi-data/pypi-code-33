# -*- coding: utf-8 -*-

from app.api.helpers.data_layers import MOVE_TYPE_SEEN
from base_test_coordinates_mandatory import _BaseTestCoordinatesMandatory


class TestMoveCreateSeen(_BaseTestCoordinatesMandatory):
    """Test Move create Seen"""

    move_type = MOVE_TYPE_SEEN
