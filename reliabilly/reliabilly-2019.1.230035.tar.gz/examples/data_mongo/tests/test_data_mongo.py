from unittest import TestCase
from examples.data_mongo.controllers.data_mongo_controller import DataMongoController
from examples.data_mongo.service import RUNNER


class DataMongoTests(TestCase):
    def test_all(self):
        controller = DataMongoController()
        self.assertIsNotNone(controller)

    def test_service(self):
        self.assertIsNotNone(RUNNER)
