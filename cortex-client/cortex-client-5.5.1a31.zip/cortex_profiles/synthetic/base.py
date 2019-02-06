from faker.providers import BaseProvider
from itertools import combinations
from typing import List


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

    def random_subset_of_list(self, l:List):
        return list(self.fake.random.choice(
            list(combinations(
                l, self.fake.random.randint(0, len(l))
            ))
        )) if l else l

    def range(self, min=0, max=100):
        return [x for x in range(min, self.fake.random.randint(1, max))]