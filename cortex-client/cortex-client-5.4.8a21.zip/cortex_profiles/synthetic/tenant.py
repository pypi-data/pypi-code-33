from typing import List, Optional

from cortex_profiles.synthetic.base import BaseProviderWithDependencies
from cortex_profiles.utils import unique_id


class TenantProvider(BaseProviderWithDependencies):

    def __init__(self, *args, profile_universe:Optional[List[str]]=None, tenant_universe:Optional[List[str]]=None, environment_universe:Optional[List[str]]=None, **kwargs):
        super(TenantProvider, self).__init__(*args, **kwargs)
        self.profileIds = profile_universe
        self.tenantIds = tenant_universe
        self.environmentIds = environment_universe

    def dependencies(self) -> List[type]:
        return []

    def tenantId(self) -> str:
        return self.fake.random.choice(self.tenantIds) if self.tenantIds else "cogscale"

    def environmentId(self) -> str:
        return self.fake.random.choice(self.environmentIds) if self.environmentIds else "cortex/default"

    def profileId(self) -> str:
        return self.fake.random.choice(self.profileIds) if self.profileIds else unique_id()

    def profileType(self) -> str:
        return "cortex/end-user"


def test_cortex_provider(f):
    for x in range(0, 100):
        print(f.tenantId())


if __name__ == "__main__":
    # from cortex_profiles.synthetic.concepts import CortexConceptsProvider
    from faker import Factory
    f = Factory.create()
    f.add_provider(TenantProvider)
    test_cortex_provider(f)