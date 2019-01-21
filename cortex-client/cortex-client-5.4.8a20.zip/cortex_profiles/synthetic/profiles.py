from typing import List, Optional

from cortex_profiles.synthetic.tenant import TenantProvider
from cortex_profiles.synthetic.attributes import AttributeProvider
from cortex_profiles.synthetic.base import BaseProviderWithDependencies
from cortex_profiles.types.profiles import Profile
from cortex_profiles.utils import unique_id, utc_timestamp


class ProfileProvider(BaseProviderWithDependencies):

    def __init__(self, *args, **kwargs):
        super(ProfileProvider, self).__init__(*args, **kwargs)

    def dependencies(self) -> List[type]:
        return [
            TenantProvider,
            AttributeProvider
        ]

    def profile(self, profileId:Optional[str]=None) -> Profile:
        return Profile(
            id=self.fake.profileId() if not profileId else profileId,
            createdAt=utc_timestamp(),
            tenantId=self.fake.company_email().split("@")[1].split(".")[0],
            environmentId="cortex/default",
            commitId=unique_id(),
            attributes = self.fake.attributes(limit=1)
        )


def test_profiles_provider(f):
    for x in range(0, 100):
        print(f.profileId())


if __name__ == "__main__":
    from cortex_profiles.synthetic import create_profile_synthesizer
    f = create_profile_synthesizer()
    test_profiles_provider(f)