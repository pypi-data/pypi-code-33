from unittest import TestCase

from bson.objectid import ObjectId
from pymongo import MongoClient

from ....utils import APIClient, AppServer
from .common import AuthApp, AuthClient


class TestAuthOwnership(TestCase):
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

    def test_set_get_owner(self):
        objid1 = str(ObjectId())
        objid2 = str(ObjectId())
        self.auth_client.set_owner('blog.post', objid1, 'admin1')
        self.auth_client.set_owner('blog.post', objid2, 'admin2')
        self.assertEqual(
            self.auth_client.get_owner('blog.post', objid1), 'admin1')
        self.assertEqual(
            self.auth_client.get_owner('blog.post', objid2), 'admin2')
        self.auth_client.set_owner('blog.post', objid1, 'admin2')
        self.assertEqual(
            self.auth_client.get_owner('blog.post', objid1), 'admin2')
