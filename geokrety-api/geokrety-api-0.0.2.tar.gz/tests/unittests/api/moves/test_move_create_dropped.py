# -*- coding: utf-8 -*-

from app.api.helpers.data_layers import MOVE_TYPE_DROPPED
from base_test_coordinates_mandatory import _BaseTestCoordinatesMandatory


class TestMoveCreateDropped(_BaseTestCoordinatesMandatory):
    """Test Move create Dropped"""

    move_type = MOVE_TYPE_DROPPED
