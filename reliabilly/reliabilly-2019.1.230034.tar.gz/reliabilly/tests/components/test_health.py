import json
from unittest import TestCase
from reliabilly.components.health import HealthCheckProvider, HealthProvider
from reliabilly.settings import Constants


class DummyHealthComponent(HealthProvider):
    pass


class HealthTests(TestCase):
    def test_health_register(self):
        health = HealthCheckProvider()
        health.register_dependency(Constants.MONGO_HEALTH_ID, None)
        health.register_dependency(Constants.DYNAMO_HEALTH_ID, None)
        self.assertIsNotNone(health)
        self.assertEqual(health.get_dependency_count(), 2)

    def test_health_construct(self):
        health = HealthCheckProvider(mongo=None, dynamo=None)
        self.assertIsNotNone(health)
        self.assertEqual(health.get_dependency_count(), 2)

    def test_health_check(self):
        health = HealthCheckProvider(mongo=DummyHealthComponent(), dynamo=None)
        result = health.get_dependency_health(Constants.MONGO_HEALTH_ID)
        self.assertEqual(result, {Constants.HEALTH: Constants.HEALTH_UNKNOWN_MESSAGE})
        health_total = health.check_health()
        health_json = json.loads(health_total)
        self.assertEqual(health_json[Constants.MONGO_HEALTH_ID], {Constants.HEALTH: Constants.HEALTH_UNKNOWN_MESSAGE})
        self.assertAlmostEqual(
            health.check_health(), '{"mongo": {"health": "health unknown"}, "dynamo": {"health": "health unknown"}}')
