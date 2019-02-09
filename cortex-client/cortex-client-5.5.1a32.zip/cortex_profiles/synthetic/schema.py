from typing import List, Optional

from cortex_profiles.builders.schema import ProfileSchemaBuilder
from cortex_profiles.schemas.schemas import DOMAIN_CONCEPTS
from cortex_profiles.synthetic.apps import AppProvider
from cortex_profiles.synthetic.base import BaseProviderWithDependencies
from cortex_profiles.synthetic.concepts import CortexConceptsProvider
from cortex_profiles.synthetic.defaults import INTERACTION_CONFIG
from cortex_profiles.synthetic.insights import InsightsProvider
from cortex_profiles.synthetic.interactions import InteractionsProvider
from cortex_profiles.synthetic.tenant import TenantProvider
from cortex_profiles.types.schema import ProfileSchema
from cortex_profiles.types.schema_config import SchemaConfig
from cortex_profiles.utils import split_camel_case, unique_id


class SchemaProvider(BaseProviderWithDependencies):

    def __init__(self, *args, **kwargs):
        super(SchemaProvider, self).__init__(*args, **kwargs)

    def dependencies(self) -> List[type]:
        return [
            CortexConceptsProvider,
            TenantProvider,
            AppProvider,
            InsightsProvider
        ]

    def profile_schema(self, tenantId:Optional[str]=None, schemaId:Optional[str]=None, environmentId:Optional[str]=None, additional_attributes:Optional[List]=[], additional_tags:Optional[List]=[]) -> ProfileSchema:
        # Schema Config ... per app ...
        # Change the builder to merge multiple schema configs ...
        # CLEANUP ... make sure we dont use anything from default ... and that it is comming from the fakers ...
        #   This way if someone creates their own synthesizer ... when they call profile schema ...
        #   they get a schema according to their synthesizer ... and not something else

        implicit_schema_configs = [
            SchemaConfig(
                apps = [
                    {"id": appId, "singular": appId.split(":")[0].upper(), "acronym": appId.split(":")[0].upper()}
                ],
                insight_types = [
                    {
                        "id": insightType, "singular": " ".join(split_camel_case(insightType)),
                        "plural": "{}s".format(" ".join(split_camel_case(insightType))),
                        "acronym": "".join(map(lambda x: x[0], split_camel_case(insightType)))
                    }
                    for insightType in self.fake.insightTypes(appId)
                ],
                concepts=[
                    {"id": DOMAIN_CONCEPTS.PERSON, "singular": "person", "plural": "people"},
                    {"id": DOMAIN_CONCEPTS.COMPANY, "singular": "company", "plural": "companies"},
                    {"id": DOMAIN_CONCEPTS.COUNTRY, "singular": "country", "plural": "countries"},
                    {"id": DOMAIN_CONCEPTS.CURRENCY, "singular": "currency", "plural": "currencies"},
                    {"id": DOMAIN_CONCEPTS.WEBSITE, "singular": "website", "plural": "websites"}
                ],
                interaction_types=[
                    {"id": interaction["interaction"], "verb": interaction["interaction"], "verbInitiatedBySubject": interaction["initiatedByProfile"]}
                    for interaction in INTERACTION_CONFIG if interaction["durationOrientedInteraction"] == False
                ],
                timed_interaction_types=[
                    {"id": interaction["interaction"], "verb": interaction["interaction"], "verbInitiatedBySubject": interaction["initiatedByProfile"]}
                    for interaction in INTERACTION_CONFIG if interaction["durationOrientedInteraction"] == True
                ]
            )
            for appId in self.fake.appIds()
        ]

        schema_builder = ProfileSchemaBuilder(
            tenantId=tenantId if tenantId else self.fake.tenantId(),
            environmentId=environmentId if environmentId else self.fake.environmentId(),
            schemaId=schemaId
        )
        for schema_config in implicit_schema_configs:
            schema_builder.append_tag_oriented_schema_from_config(schema_config)
        schema_builder.append_attributes(additional_attributes)
        schema_builder.append_tags(additional_tags)
        return schema_builder.get_schema()


if __name__ == '__main__':
    from cortex_profiles.synthetic.tests import test_insight_distribution, test_insight_interaction_events
    from cortex_profiles.synthetic import create_profile_synthesizer
    f = create_profile_synthesizer()
    print(f.profile_schema())



