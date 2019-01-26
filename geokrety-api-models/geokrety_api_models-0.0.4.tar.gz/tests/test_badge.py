# -*- coding: utf-8 -*-

from nose.tools import assert_raises
from sqlalchemy.exc import OperationalError

from geokrety_api_models.badge import Badge
from geokrety_api_models.user import User

from . import DatabaseTest


class TestBadge(DatabaseTest):
    """Test badge"""

    def test_create(self):
        badge = Badge()
        self.session.add(badge)
        with assert_raises(OperationalError):
            self.session.commit()
        self.session.rollback()

    def test_create_ok(self):
        user = User(name="username", password="password", email="user@geokrety.org")
        self.session.add(user)

        badge = Badge()
        badge.name = "some name"
        badge.author = user
        self.session.add(badge)

        self.assertEqual(badge.name, "some name")
