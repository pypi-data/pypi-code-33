import time
from unittest import TestCase

from ....utils import APIClient, AppServer
from .common import AuthApp, AuthClient


class TestAuthBasic(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = AuthApp()
        cls.app.init()
        cls.server = AppServer(app=cls.app)
        cls.server.run()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()
        cls.app.deinit()

    def setUp(self):
        self.client = APIClient(api_url='http://localhost:12345/api')
        self.auth_client = AuthClient(self.client)

    def tearDown(self):
        pass

    def test_login_logout(self):
        self.assertIsNone(self.auth_client.me())
        with self.assertRaises(Exception):
            self.auth_client.login('admin', 'admin13')

        with self.assertRaises(Exception):
            self.auth_client.login('admin2', 'admin123')

        self.auth_client.login('admin', 'admin123')
        me = self.auth_client.me()
        self.assertEqual(me['username'], 'admin')

        self.auth_client.logout()
        self.assertIsNone(self.auth_client.me())

    def test_token_expire(self):
        self.auth_client.login('admin', 'admin123')
        me = self.auth_client.me()
        self.assertEqual(me['username'], 'admin')
        time.sleep(10)
        self.assertIsNone(self.auth_client.me())

    def test_token_refresh(self):
        self.auth_client.login('admin', 'admin123')
        me = self.auth_client.me()
        self.assertEqual(me['username'], 'admin')
        time.sleep(3)
        self.auth_client.refresh()
        time.sleep(3)
        self.assertEqual(me['username'], 'admin')
        self.auth_client.logout()
        self.assertIsNone(self.auth_client.me())

    def test_register(self):
        self.assertTrue(self.auth_client.register('user', 'userpass123'))
        self.auth_client.login('user', 'userpass123')
        me = self.auth_client.me()
        self.assertEqual(me['username'], 'user')

    def test_change_password(self):
        self.auth_client.login('admin', 'admin123')
        self.auth_client.change_password('admin123', 'admin234')
        self.auth_client.logout()

        with self.assertRaises(Exception):
            self.auth_client.login('admin', 'admin123')

        self.auth_client.login('admin', 'admin234')
        self.auth_client.logout()

        self.auth_client.change_password(
            'admin234', 'admin123', username='admin')
        self.auth_client.login('admin', 'admin123')
        self.auth_client.logout()
        self.assertFalse(self.auth_client.change_password(
            'admin234', 'admin123', username='admin'))

    def test_admin_powers(self):
        self.assertTrue(self.auth_client.register('testuser', 'userpass123'))
        self.auth_client.login('admin', 'admin123')
        self.auth_client.change_password(
            new_password='userpass234', username='testuser')
        self.auth_client.logout()
        self.auth_client.login('testuser', 'userpass234')
        me = self.auth_client.me()
        self.assertEqual(me['username'], 'testuser')
        self.assertFalse(self.auth_client.change_password(
            new_password='admin', username='admin'))

    def test_invalid_login(self):
        with self.assertRaises(Exception):
            self.auth_client.login('admin', '')

        with self.assertRaises(Exception):
            self.auth_client.login('', 'admin123')

        with self.assertRaises(Exception):
            self.auth_client.login('somerandomuser', 'admin123456')

    def test_duplicate_registration(self):
        self.assertFalse(self.auth_client.register('admin', 'admin'))
