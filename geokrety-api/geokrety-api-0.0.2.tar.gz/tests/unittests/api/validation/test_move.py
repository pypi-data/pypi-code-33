# coding=utf-8
from mixer.backend.flask import mixer

from app import current_app as app
from app.api.helpers.data_layers import (MOVE_TYPE_ARCHIVED, MOVE_TYPE_COMMENT,
                                         MOVE_TYPE_DIPPED, MOVE_TYPE_DROPPED,
                                         MOVE_TYPE_GRABBED, MOVE_TYPE_SEEN)
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.schema.moves import MoveSchema
from geokrety_api_models import Geokret
from tests.unittests.utils.base_test_case import BaseTestCase


class TestMove(BaseTestCase):
    """Test Move Schema"""

    def test_validate_type(self):
        """Check Form Move: validates type"""
        with app.test_request_context():
            MoveSchema.validate_type(MoveSchema(), MOVE_TYPE_GRABBED)
            MoveSchema.validate_type(MoveSchema(), MOVE_TYPE_COMMENT)
            MoveSchema.validate_type(MoveSchema(), MOVE_TYPE_DROPPED)
            MoveSchema.validate_type(MoveSchema(), MOVE_TYPE_SEEN)
            MoveSchema.validate_type(MoveSchema(), MOVE_TYPE_ARCHIVED)
            MoveSchema.validate_type(MoveSchema(), MOVE_TYPE_DIPPED)

            with self.assertRaises(UnprocessableEntity):
                MoveSchema.validate_type(MoveSchema(), -1)
            with self.assertRaises(UnprocessableEntity):
                MoveSchema.validate_type(MoveSchema(), 1)
            with self.assertRaises(UnprocessableEntity):
                MoveSchema.validate_type(MoveSchema(), 6)
            with self.assertRaises(UnprocessableEntity):
                MoveSchema.validate_type(MoveSchema(), "-1")
            with self.assertRaises(UnprocessableEntity):
                MoveSchema.validate_type(MoveSchema(), "6")
            with self.assertRaises(UnprocessableEntity):
                MoveSchema.validate_type(MoveSchema(), "")
            with self.assertRaises(UnprocessableEntity):
                MoveSchema.validate_type(MoveSchema(), "100")
            with self.assertRaises(UnprocessableEntity):
                MoveSchema.validate_type(MoveSchema(), "A")
            with self.assertRaises(UnprocessableEntity):
                MoveSchema.validate_type(MoveSchema(), u"jeśli")

    def test_validate_tracking_code(self):
        """Check Form Move: validates tracking_code"""
        with app.test_request_context():
            mixer.init_app(app)
            geokret1 = mixer.blend(Geokret)

            MoveSchema.validate_tracking_code(MoveSchema(), geokret1.tracking_code)

            self.assertNotEqual(geokret1.tracking_code, "AAAAA")
            with self.assertRaises(UnprocessableEntity):
                MoveSchema.validate_tracking_code(MoveSchema(), "AAAAA")
            with self.assertRaises(UnprocessableEntity):
                MoveSchema.validate_tracking_code(MoveSchema(), "")
            with self.assertRaises(UnprocessableEntity):
                MoveSchema.validate_tracking_code(MoveSchema(), u"jeśli")
            with self.assertRaises(UnprocessableEntity):
                MoveSchema.validate_tracking_code(MoveSchema(), "1234567890")
