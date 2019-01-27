from flask_rest_jsonapi.exceptions import ObjectNotFound
from mixer.backend.flask import mixer

from app import current_app as app
from app.api.helpers.db import get_count, get_or_create, safe_query, save_to_db
from app.models import db
from geokrety_api_models import User
from tests.unittests.utils.base_test_case import BaseTestCase


class TestDBHelperValidation(BaseTestCase):

    def test_save_to_db(self):
        """Check DBHelper: save to db"""
        with app.test_request_context():
            with mixer.ctx(commit=False):
                mixer.init_app(app)
                obj = mixer.blend(User)

            save_to_db(obj)
            user = db.session.query(User).filter(User.id == obj.id).first()
            self.assertEqual(obj.name, user.name)

    def test_safe_query(self):
        """Check DBHelper: safe query"""
        with app.test_request_context():
            mixer.init_app(app)
            user = mixer.blend(User)
            obj = safe_query(db, User, 'id', user.id, 'user_id')
            self.assertEqual(obj.name, user.name)

    def test_safe_query_exception(self):
        """Check DBHelper: safe query exception"""
        with app.test_request_context():
            self.assertRaises(ObjectNotFound, lambda: safe_query(db, User, 'id', 1, 'user_id'))

    def test_get_or_create(self):
        """Check DBHelper: get or create"""
        with app.test_request_context():
            mixer.init_app(app)
            with mixer.ctx(commit=False):
                user = mixer.blend(User)
            save_to_db(user)
            obj, is_created = get_or_create(User, name=user.name)
            self.assertEqual(user.id, obj.id)
            self.assertFalse(is_created)

            obj, is_created = get_or_create(User, name="new user", password="password", email="email2@email.email")
            self.assertNotEqual(user.id, obj.id)
            self.assertTrue(is_created)

    def test_get_count(self):
        """Check DBHelper: get count"""
        with app.test_request_context():
            with mixer.ctx(commit=False):
                user = mixer.blend(User)
            save_to_db(user)
            self.assertEqual(get_count(User.query), 1)
