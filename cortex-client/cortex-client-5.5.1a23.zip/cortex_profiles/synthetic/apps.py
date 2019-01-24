from typing import List

from cortex_profiles.synthetic.base import BaseProviderWithDependencies
from cortex_profiles.synthetic import defaults


class AppProvider(BaseProviderWithDependencies):

    def dependencies(self) -> List[type]:
        return []

    def __init__(self, *args, app_universe:List[str]=defaults.APPS, **kwargs):
        super(AppProvider, self).__init__(*args, **kwargs)
        self.apps = app_universe

    def appId(self, random_version=False) -> str:
        if random_version:
            version = self.symanticVersion()
        else:
            version = "1.0.0"
        return "{}:{}".format(self.fake.random.choice(self.apps), version)

    def appIds(self) -> List[str]:
        version = "1.0.0"
        return ["{}:{}".format(app, version) for app in self.apps]

    def detailedAppId(self):
        return "{}:{}".format(self.fake.random.choice(self.apps), self.symanticVersion())

    def symanticVersion(self):
        return self.fake.random.choice([
            "{}.{}.{}-alpha".format(self.fake.random.randint(0, 5), self.fake.random.randint(0, 10), self.fake.random.randint(0, 10)),
            "{}.{}.{}-alpha.{}".format(self.fake.random.randint(0, 5), self.fake.random.randint(0, 10), self.fake.random.randint(0, 100), self.fake.random.randint(0, 10)),
            "{}.{}.{}-alpha.beta".format(self.fake.random.randint(0, 5), self.fake.random.randint(0, 10), self.fake.random.randint(0, 10)),
            "{}.{}.{}-beta".format(self.fake.random.randint(0, 5), self.fake.random.randint(0, 10), self.fake.random.randint(0, 10)),
            "{}.{}.{}-beta.{}".format(self.fake.random.randint(0, 5), self.fake.random.randint(0, 10), self.fake.random.randint(0, 100), self.fake.random.randint(0, 10)),
            "{}.{}.{}-rc.{}".format(self.fake.random.randint(0, 5), self.fake.random.randint(0, 10), self.fake.random.randint(0, 100), self.fake.random.randint(0, 10)),
            "{}.{}.{}".format(self.fake.random.randint(0, 5), self.fake.random.randint(0, 10), self.fake.random.randint(0, 10)),
        ])


def test_app_provider(f):
    for x in range(0, 100):
        print(f.appId())


if __name__ == "__main__":
    from cortex_profiles.synthetic import create_profile_synthesizer
    test_app_provider(create_profile_synthesizer())
