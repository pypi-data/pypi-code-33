from typing import List, Tuple

import pandas as pd

from cortex_profiles import implicit_attribute_builders
from cortex_profiles.synthetic.attribute_values import AttributeValueProvider
from cortex_profiles.synthetic.base import BaseProviderWithDependencies
from cortex_profiles.synthetic.tenant import TenantProvider
from cortex_profiles.synthetic.insights import InsightsProvider
from cortex_profiles.synthetic.interactions import InteractionsProvider
from cortex_profiles.synthetic.sessions import SessionsProvider
from cortex_profiles.types.attributes import ProfileAttribute, DeclaredProfileAttribute, InferredProfileAttribute, \
    ObservedProfileAttribute
from cortex_profiles.types.insights import Insight
from cortex_profiles.types.interactions import Session, InsightInteractionEvent
from cortex_profiles.utils import unique_id, utc_timestamp
from cortex_profiles.utils_for_dfs import list_of_attrs_to_df


value = ["duration", "count", "total", "distribution"]
app_specififity = ["app-specific", "app-agnostic"]
algo_specififity = ["algo-specific", "algo-agnostic",]
timeframe = ["{}{}".format(x, y) for x in range(0, 6) for y in ["week", "month", "year"]] + ["recent", "eternal"]
purpose = ["insight-interaction", "app-activity", "app-preferences", "algo-preferences", "user-declarations"]


class AttributeProvider(BaseProviderWithDependencies):

    def dependencies(self) -> List[type]:
        return [
            InsightsProvider,
            InteractionsProvider,
            SessionsProvider,
            AttributeValueProvider,
            TenantProvider
        ]

    def data_to_build_single_profile(self, profileId:str=None) -> Tuple[str, List[Session], List[Insight], List[InsightInteractionEvent]]:
        profileId = profileId if profileId else self.fake.profileId()
        sessions = self.fake.sessions(profileId=profileId)
        insights = self.fake.insights(profileId=profileId)
        interactions = self.fake.interactions(profileId, sessions, insights)
        return (profileId, sessions, insights, interactions)

    def dfs_to_build_single_profile(self, profileId:str=None) -> Tuple[str, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        profileId, sessions, insights, interactions = self.data_to_build_single_profile(profileId=profileId)
        return (
            profileId, list_of_attrs_to_df(sessions), list_of_attrs_to_df(insights), list_of_attrs_to_df(interactions)
        )

    def attributes_for_single_profile(self, profileId:str=None) -> List[ProfileAttribute]:
        """
        This returns a list of synthesized implicit attributes that cortex is capable of generating for profiles.
        :param profileId:
        :return:
        """
        (profileId, sessions_df, insights_df, interactions_df) = self.dfs_to_build_single_profile(profileId=profileId)
        return implicit_attribute_builders.derive_implicit_attributes(insights_df, interactions_df, sessions_df)

    def unique_attribute_key(self):
        return "value[{value}].app_specififity[{app_specififity}].algo_specififity[{algo_specififity}].timeframe[{timeframe}].purpose[{purpose}]".format(
            value=self.fake.random.choice(value),
            app_specififity=self.fake.random.choice(app_specififity),
            algo_specififity=self.fake.random.choice(algo_specififity),
            timeframe=self.fake.random.choice(timeframe),
            purpose=self.fake.random.choice(purpose)
        )

    def attribute(self):
        attr_class = self.fake.random.choice([DeclaredProfileAttribute, InferredProfileAttribute, ObservedProfileAttribute])
        attr_value = self.fake.random.choice([
            self.fake.dimensional_value, self.fake.object_value, self.fake.relationship_value, self.fake.numeric_value,
            self.fake.percentage_value, self.fake.percentile_value, self.fake.average_value, self.fake.counter_value, self.fake.total_value
        ])()
        return attr_class(
            id=unique_id(),
            profileId=self.fake.profileId(),
            createdAt=utc_timestamp(),
            attributeKey=self.unique_attribute_key(),
            attributeValue=attr_value,
            tenantId=self.fake.tenantId(),
            environmentId=self.fake.environmentId(),
            onLatestProfile=True,
            commits=[unique_id() for x in self.fake.range(0, 10)]
        )

    def attributes(self, limit=100) -> List[ProfileAttribute]:
        return [
            self.attribute() for x in self.fake.range(0, limit)
        ]


def test_attr_provider(f):
    print(f.attributes_for_single_profile())
    # for x in range(0, 100):
    #     print(f.attributes())

if __name__ == '__main__':
    from cortex_profiles.synthetic import create_profile_synthesizer
    test_attr_provider(create_profile_synthesizer())
