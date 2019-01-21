from typing import List

import attr
from cortex_profiles.implicit.schema import implicit_attributes
from cortex_profiles.implicit.schema.implicit_groups import ImplicitGroups
from cortex_profiles.implicit.schema.implicit_tags import expand_tags_for_profile_attribute, ImplicitAttributeSubjects, \
    ImplicitTags, ImplicitTagTemplates
from cortex_profiles.implicit.schema.utils import prepare_schema_config_variable_names
from cortex_profiles.types.schema import ProfileAttributeSchema, ProfileGroupSchema, ProfileSchema, ProfileTagSchema
from cortex_profiles.types.schema_config import SchemaConfig
from cortex_profiles.utils import utc_timestamp, unique_id, group_objects_by, dervie_set_by_element_id


def implicitly_generate_group_schemas(schema_config:SchemaConfig) -> List[ProfileGroupSchema]:
    all_groups = list(map(lambda x: x.value, ImplicitGroups.__members__.values()))
    all_tags = implicitly_generate_tag_schemas(schema_config)
    tags_grouped_by_group = group_objects_by(all_tags, lambda t: t.group)
    groups_grouped_by_id = group_objects_by(all_groups, lambda g: g.id)
    return [
        attr.evolve(group_schemas[0], tags=tags_grouped_by_group[group_id])
        for group_id, group_schemas in groups_grouped_by_id.items()
    ]


def implicitly_generate_attribute_schemas(schema_config:SchemaConfig) -> List[ProfileAttributeSchema]:
    return (
          implicit_attributes.schemas_for_universal_attributes()
        + implicit_attributes.schema_for_concept_specific_interaction_attributes(schema_config)
        + implicit_attributes.schema_for_concept_specific_duration_attributes(schema_config)
        + implicit_attributes.schema_for_interaction_attributes(schema_config)
        + implicit_attributes.schema_for_app_specific_attributes(schema_config)
    )


def implicitly_generate_tag_schemas(schema_config:SchemaConfig) -> List[ProfileTagSchema]:
    tags = [
        ImplicitTags.DECLARED.value,
        ImplicitTags.OBSERVED.value,
        ImplicitTags.INFERRED.value,
        ImplicitTags.ASSIGNED.value,
        ImplicitTags.RECENT.value,
        ImplicitTags.ETERNAL.value,
        ImplicitTags.INSIGHT_INTERACTIONS.value,
        ImplicitTags.APP_USAGE.value,
    ]

    interactions = list(map(
        lambda interaction: prepare_schema_config_variable_names({attr.fields(SchemaConfig).interaction_types.name: interaction}),
        list(dervie_set_by_element_id(schema_config.interaction_types + schema_config.timed_interaction_types, lambda x: x.id))
    ))
    tags.extend([ImplicitTagTemplates.INTERACTION(interaction) for interaction in interactions])

    apps = list(map(
        lambda app: prepare_schema_config_variable_names({attr.fields(SchemaConfig).apps.name: app}),
        schema_config.apps
    ))
    tags.extend([ImplicitTagTemplates.APP_ASSOCIATED(app) for app in apps])

    algos = list(map(
        lambda algo: prepare_schema_config_variable_names({attr.fields(SchemaConfig).insight_types.name: algo}),
        schema_config.insight_types
    ))
    tags.extend([ImplicitTagTemplates.ALGO_ASSOCIATED(algo) for algo in algos])

    concepts = list(map(
        lambda concept: prepare_schema_config_variable_names({attr.fields(SchemaConfig).concepts.name: concept}),
        schema_config.concepts
    ))
    tags.extend([ImplicitTagTemplates.CONCEPT_ASSOCIATED(concept) for concept in concepts])

    return tags


def implicity_generate_profile_schema_from_config(schema_config:SchemaConfig, tenantId, environmentId) -> ProfileSchema:
    return ProfileSchema(
        id=unique_id(),
        tenantId=tenantId,
        environmentId=environmentId,
        createdAt=utc_timestamp(),
        attributes=implicitly_generate_attribute_schemas(schema_config),
        tags=implicitly_generate_tag_schemas(schema_config),
        groups=implicitly_generate_group_schemas(schema_config)
    )

