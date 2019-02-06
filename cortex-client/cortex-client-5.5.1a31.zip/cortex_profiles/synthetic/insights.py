from typing import Mapping, List, Optional
from uuid import uuid4
import pydash
import arrow

from cortex_profiles.schemas.schemas import CONTEXTS
from cortex_profiles.synthetic import defaults
from cortex_profiles.synthetic.apps import AppProvider
from cortex_profiles.synthetic.base import BaseProviderWithDependencies
from cortex_profiles.synthetic.concepts import CortexConceptsProvider
from cortex_profiles.synthetic.tenant import TenantProvider
from cortex_profiles.types.insights import InsightTag, Link, Insight
from cortex_profiles.utils import pick_random_time_between


class InsightsProvider(BaseProviderWithDependencies):

    def __init__(self, *args,
                 insight_types:Mapping[str, List[str]]=defaults.INSIGHT_TYPES_PER_APP,
                 concept_limits_per_insight:Optional[Mapping[str, Mapping[str, int]]]=defaults.LIMITS_ON_COUNTS_CONCEPTS_OF_TYPE_PER_CONCEPT_SET,
                 **kwargs):
        super(InsightsProvider, self).__init__(*args, **kwargs)
        self.insight_types = insight_types
        self.concept_limits_per_insight = {
            concept: (limits["min"], limits["max"])
            for concept, limits in concept_limits_per_insight.items()
        }

    def dependencies(self) -> List[type]:
        return [
            CortexConceptsProvider,
            TenantProvider,
            AppProvider
        ]

    def insightId(self):
        return str(uuid4())

    def insightType(self, appId:str):
        return self.fake.random.choice(self.insightTypes(appId))

    def insightTypes(self, appId:str):
        return self.insight_types[appId.split(":")[0]]

    def tag(self, insightId:str, taggedOn:str, concept:Optional[Link]=None) -> InsightTag:
        concept = concept if concept else self.fake.concept()
        return InsightTag(
            id=str(uuid4()),
            insight=Link(
                id=insightId,
                context=CONTEXTS.INSIGHT
            ),
            tagged=taggedOn,
            concept=concept,
            relationship=Link(
                id=CONTEXTS.INSIGHT_TAG_RELATED_TO_RELATIONSHIP,
                context=CONTEXTS.INSIGHT_TAG_RELATIONSHIP,
            )
        )

    def tags(self, insightId:str, taggedOn:str, tagged_concepts:Optional[List[Link]]=None) -> List[InsightTag]:
        tagged_concepts = tagged_concepts if tagged_concepts is not None else [None]*10
        return [self.tag(insightId, taggedOn, concept=tagged_concept) for tagged_concept in tagged_concepts]

    def concepts_relevant_to_insight(self) -> List[Link]:
        return list(self.fake.set_of_concepts(self.concept_limits_per_insight))

    def insight(self, profileId) -> Insight:
        insightId = self.insightId()
        appId = self.fake.appId()
        dateGenerated = str(pick_random_time_between(self.fake, arrow.utcnow().shift(days=-30), arrow.utcnow()))
        return Insight(
            id=insightId,
            tags=self.tags(insightId, dateGenerated, tagged_concepts=self.concepts_relevant_to_insight()),
            insightType=self.insightType(appId=appId),
            profileId=profileId,
            dateGeneratedUTCISO=dateGenerated,
            appId=appId
        )

    def insights(self, profileId:str=None, floor:int=50, ceiling:int=250) -> List[Insight]:
        profileId = profileId if profileId else self.fake.profileId()
        return [
            self.insight(profileId=profileId)
            for x in range(0, self.fake.random.randint(floor, ceiling))
        ]


def test_insights_provider(f):
    import json
    print(json.dumps(f.concepts_relevant_to_insight(), indent=4))
    # for x in range(0, 100):
    #     print(f.insight(1))


if __name__ == "__main__":
    from cortex_profiles.synthetic import create_profile_synthesizer
    f = create_profile_synthesizer()
    test_insights_provider(f)


