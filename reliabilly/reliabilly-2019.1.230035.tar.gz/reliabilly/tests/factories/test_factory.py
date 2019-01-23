import warnings
from unittest import TestCase
from reliabilly.components.authorization import Authorization
from reliabilly.components.factories.factory import Factory, Components


class FactoryTests(TestCase):

    def setUp(self):
        warnings.filterwarnings("ignore", category=ResourceWarning)

    def test_dynamo_factory(self):
        client = Factory.create(Components.DataClients.DYNAMODB)
        self.assertIsNotNone(client)

    def test_auth_factory(self):
        client = Factory.create(Components.ServiceClients.AUTH)
        self.assertTrue(isinstance(client, Authorization))
