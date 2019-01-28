from unittest import TestCase

from bson.objectid import ObjectId
from pymongo import MongoClient

from ....utils import APIClient, AppServer
from .common import AuthApp, AuthClient


class TestAuthPermissions(TestCase):
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

        self.auth_client.register('user1', 'user123')
        self.auth_client.register('user2', 'user123')
        self.auth_client.register('user3', 'user123')
        self.auth_client.register('user4', 'user123')
        self.auth_client.register('user5', 'user123')

        self.auth_client.create_group('group1')
        self.auth_client.create_group('group2')
        self.auth_client.create_group('group3')

        self.auth_client.add_user_to_group('group1', 'user1')
        self.auth_client.add_user_to_group('group1', 'user2')
        self.auth_client.add_user_to_group('group1', 'user3')
        self.auth_client.add_user_to_group('group2', 'user3')
        self.auth_client.add_user_to_group('group2', 'user4')
        self.auth_client.add_user_to_group('group2', 'user5')
        self.auth_client.add_user_to_group('group3', 'user4')

        self.obj1 = str(ObjectId())
        self.obj2 = str(ObjectId())

        self.auth_client.permission_set('blog.category.create', 'user.user1')
        self.auth_client.permission_set('blog.category.create', 'group.group2')
        self.auth_client.permission_set('blog.category.create', 'user.user2')
        self.auth_client.permission_unset('blog.category.create', 'user.user2')
        self.auth_client.object_permission_set(
            'blog.post', self.obj1, 'blog.post.write', 'user.user1')
        self.auth_client.object_permission_set(
            'blog.post', self.obj1, 'blog.post.write', 'group.group2')
        self.auth_client.object_permission_set(
            'blog.post', self.obj2, 'blog.post.write', 'user.user5')

    def tearDown(self):
        self.auth_client.logout()

    def test_basic(self):
        self.assertTrue(
            self.auth_client.permission_check('blog.category.create', 'admin'))
        self.assertTrue(
            self.auth_client.permission_check('blog.category.create', 'user1'))
        self.assertTrue(
            self.auth_client.permission_check('blog.category.create', 'user4'))
        self.assertFalse(
            self.auth_client.permission_check('blog.category.create', 'user2'))

        self.assertTrue(
            self.auth_client.object_permission_check(
                'blog.post', self.obj1, 'blog.post.write', 'admin'))
        self.assertTrue(
            self.auth_client.object_permission_check(
                'blog.post', self.obj1, 'blog.post.write', 'user1'))
        self.assertTrue(
            self.auth_client.object_permission_check(
                'blog.post', self.obj1, 'blog.post.write', 'user4'))
        self.assertFalse(
            self.auth_client.object_permission_check(
                'blog.post', self.obj2, 'blog.post.write', 'user1'))

    def test_query(self):
        self.assertIn('blog.category.create',
                      self.auth_client.permission_list('user.user1'))
