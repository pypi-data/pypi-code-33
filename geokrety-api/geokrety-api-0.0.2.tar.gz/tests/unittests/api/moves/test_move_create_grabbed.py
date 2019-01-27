# -*- coding: utf-8 -*-

from app.api.helpers.data_layers import MOVE_TYPE_GRABBED
from base_test_coordinates_optional import _BaseTestCoordinatesOptional


class TestMoveCreateGrabbed(_BaseTestCoordinatesOptional):
    """Test Move create Grabbed"""

    move_type = MOVE_TYPE_GRABBED
