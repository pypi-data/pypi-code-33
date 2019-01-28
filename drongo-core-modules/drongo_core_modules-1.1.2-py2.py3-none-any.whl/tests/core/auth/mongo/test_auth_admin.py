from unittest import TestCase

from pymongo import MongoClient

from ....utils import APIClient, AppServer
from .common import AuthApp, AuthClient


class TestAuthAdmin(TestCase):
    @classmethod
    def setUpClass(cls):
        db_client = MongoClient()
        db_client.drop_database('drongo_master')
        cls.app = AuthApp()
        cls.app.init()
        cls.server = AppServer(app=cls.app)
        cls.server.run()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def setUp(self):
        self.client = APIClient(api_url='http://localhost:12345/api')
        self.auth_client = AuthClient(self.client)
        self.auth_client.login('admin', 'admin123')

    def tearDown(self):
        self.auth_client.logout()

    def test_user_list(self):
        result = self.auth_client.get_user_list()
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)

    def test_group_create_delete_list(self):
        result = self.auth_client.get_group_list()
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 0)

        self.auth_client.create_group('testgroup')
        result = self.auth_client.get_group_list()
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.auth_client.delete_group('testgroup')

    def test_group_user_management(self):
        self.auth_client.create_group('testgroup')
        self.auth_client.delete_user_from_group('testgroup', 'admin')
        self.auth_client.add_user_to_group('testgroup', 'admin')
        self.assertEqual(
            self.auth_client.get_group_users('testgroup'), ['admin'])
        self.assertEqual(
            self.auth_client.get_user_groups('admin'), ['testgroup'])
        self.auth_client.delete_user_from_group('testgroup', 'admin')
        self.assertEqual(
            self.auth_client.get_group_users('testgroup'), [])
        self.auth_client.delete_group('testgroup')

    def test_duplicate_group(self):
        self.auth_client.create_group('testgroup')
        self.auth_client.create_group('testgroup')
        self.auth_client.delete_group('testgroup')

    def test_user_action_non_existant_group(self):
        self.auth_client.get_group_users('testgroupa')
        self.auth_client.add_user_to_group('testgroupa', 'admin')
        self.auth_client.delete_user_from_group('testgroupa', 'admin')
