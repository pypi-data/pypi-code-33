# -*- coding: utf-8 -*-

from app.api.helpers.data_layers import MOVE_TYPE_DIPPED
from base_test_coordinates_mandatory import _BaseTestCoordinatesMandatory


class TestMoveCreateDipped(_BaseTestCoordinatesMandatory):
    """Test Move create Dipped"""

    move_type = MOVE_TYPE_DIPPED
