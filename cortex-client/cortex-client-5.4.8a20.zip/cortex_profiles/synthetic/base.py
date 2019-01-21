from faker.providers import BaseProvider


class BaseProviderWithDependencies(BaseProvider):

    def validate_dependencies(self):
        dependencies = self.dependencies()
        available_providers = list(map(lambda x: type(x), self.fake.providers))
        missing_providers = [dep for dep in dependencies if dep not in available_providers]
        assert not missing_providers, "Faker missing the following dependencies [{}] for [{}]".format(missing_providers, type(self).__name__)

    def __init__(self, *args, **kwargs):
        super(BaseProviderWithDependencies, self).__init__(*args, **kwargs)
        self.fake = args[0]
        self.validate_dependencies()