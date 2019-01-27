import json

from mixer.backend.flask import mixer

from app import current_app as app
from app.models import db
from geokrety_api_models import User
from tests.unittests.utils.base_test_case import BaseTestCase


class TestAuthentication(BaseTestCase):
    username = "kumy"
    password = "password"
    password_bad = "bad_password"

    def setUp(self):
        super(TestAuthentication, self).setUp()
        with app.test_request_context():
            mixer.init_app(app)
            with mixer.ctx(commit=False):
                user = mixer.blend(User, name=self.username, _password=self.password)
                db.session.add(user)
                db.session.commit()

    def _check_login(self, name, password):
        return self.app.post('/auth/session',
                             headers={
                                 'content-type': 'application/json'
                             },
                             data=json.dumps({
                                 "username": name,
                                 "password": password
                             }), follow_redirects=True)

    def test_auth_nonexistent_user(self):
        """
        Check Authentication: POST can't login with non-existent user
        """
        response = self._check_login("someone", "else")
        self.assertEqual(response.status_code, 401)

    def test_auth(self):
        """
        Check Authentication: POST can login with existent user
        """
        response = self._check_login(self.username, self.password)
        self.assertEqual(response.status_code, 200)

    def test_auth_bad_password(self):
        """
        Check Authentication: POST can't login with bad password
        """
        response = self._check_login(self.username, self.password_bad)
        self.assertEqual(response.status_code, 401)

    def test_auth_bad_username(self):
        """
        Check Authentication: POST can't login with bad username
        """
        response = self._check_login(self.username + "_bad", self.password)
        self.assertEqual(response.status_code, 401)
