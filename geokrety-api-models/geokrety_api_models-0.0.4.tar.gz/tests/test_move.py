# -*- coding: utf-8 -*-

from geokrety_api_models import Geokret, Move, User
from geokrety_api_models.utilities.const import (GEOKRET_TYPE_TRADITIONAL,
                                                 MOVE_TYPE_GRABBED)

from . import DatabaseTest


class TestMove(DatabaseTest):
    """Test move"""

    def test_create(self):
        user = User(name="username", password="password", email="user@geokrety.org")
        geokret = Geokret(name="My GeoKret",
                          type=GEOKRET_TYPE_TRADITIONAL,
                          created_on_datetime="2019-01-19T22:46:44")
        move1 = Move(geokret=geokret,
                     moved_on_datetime="2019-01-19T22:46:44",
                     type=MOVE_TYPE_GRABBED,
                     author=user)

        self.session.add(move1)
        self.session.commit()
