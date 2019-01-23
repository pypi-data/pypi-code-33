import json

from nameko.extensions import DependencyProvider
from reliabilly.settings import Constants


class HealthProvider(DependencyProvider):
    health = Constants.HEALTH_UNKNOWN_MESSAGE

    def get_health(self):
        return {Constants.HEALTH: self.health}


class HealthCheckProvider(DependencyProvider):
    def __init__(self, **kwargs):
        self.dependencies = {}
        if kwargs:
            self.dependencies = kwargs

    def get_dependency_count(self):
        return len(self.dependencies)

    def register_dependency(self, dependency_name, dependency):
        self.dependencies[dependency_name] = dependency

    def check_health(self):
        health = {}
        for dependency_name in self.dependencies:
            health[dependency_name] = self.get_dependency_health(dependency_name)
        return json.dumps(health)

    def get_dependency_health(self, dependency_name):
        if self.dependencies[dependency_name]:
            return self.dependencies[dependency_name].get_health()
        return Constants.UNKNOWN_HEALTH_RESPONSE
