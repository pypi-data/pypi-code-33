from typing import List

import attr
from cortex_profiles.implicit.schema import implicit_attributes
from cortex_profiles.implicit.schema.implicit_groups import ImplicitGroups
from cortex_profiles.implicit.schema.implicit_tags import expand_tags_for_profile_attribute, ImplicitAttributeSubjects, \
    ImplicitTags, ImplicitTagTemplates, ImplicitTagLabels
from cortex_profiles.implicit.schema.utils import prepare_schema_config_variable_names
from cortex_profiles.types.schema import ProfileAttributeSchema, ProfileGroupSchema, ProfileSchema, ProfileTagSchema
from cortex_profiles.types.schema_config import SchemaConfig
from cortex_profiles.utils import utc_timestamp, unique_id, group_objects_by, dervie_set_by_element_id


def implicitly_generate_group_schemas(schema_config:SchemaConfig) -> List[ProfileGroupSchema]:
    all_groups = list(ImplicitGroups.values())
    all_tags = implicitly_generate_tag_schemas(schema_config)
    tags_grouped_by_group = group_objects_by(all_tags, lambda t: t.group)
    groups_grouped_by_id = group_objects_by(all_groups, lambda g: g.id)
    return [
        attr.evolve(
            group_schemas[0],
            tags=list(map(lambda x: x.id, tags_grouped_by_group[group_id]))
        )
        for group_id, group_schemas in groups_grouped_by_id.items()
    ]


def implicitly_generate_attribute_schemas(schema_config:SchemaConfig, include_tags) -> List[ProfileAttributeSchema]:
    return (
          implicit_attributes.schemas_for_universal_attributes(include_tags=include_tags)
        + implicit_attributes.schema_for_concept_specific_interaction_attributes(schema_config, include_tags=include_tags)
        + implicit_attributes.schema_for_concept_specific_duration_attributes(schema_config, include_tags=include_tags)
        + implicit_attributes.schema_for_interaction_attributes(schema_config, include_tags=include_tags)
        + implicit_attributes.schema_for_app_specific_attributes(schema_config, include_tags=include_tags)
    )


def implicitly_generate_tag_schemas(schema_config:SchemaConfig) -> List[ProfileTagSchema]:
    tags = [
        ImplicitTags.DECLARED,
        ImplicitTags.OBSERVED,
        ImplicitTags.INFERRED,
        ImplicitTags.ASSIGNED,
        ImplicitTags.RECENT,
        ImplicitTags.ETERNAL,
        ImplicitTags.INSIGHT_INTERACTIONS,
        ImplicitTags.APP_USAGE,
    ]

    used_lables = list(ImplicitTagLabels.values())

    interactions = list(map(
        lambda interaction: prepare_schema_config_variable_names({attr.fields(SchemaConfig).interaction_types.name: interaction}),
        list(dervie_set_by_element_id(schema_config.interaction_types + schema_config.timed_interaction_types, lambda x: x.id))
    ))

    for interaction in interactions:
        new_tag = ImplicitTagTemplates.INTERACTION(interaction, used_lables)
        used_lables.append(new_tag.label)
        tags.append(new_tag)

    apps = list(map(
        lambda app: prepare_schema_config_variable_names({attr.fields(SchemaConfig).apps.name: app}),
        schema_config.apps
    ))

    for app in apps:
        new_tag = ImplicitTagTemplates.APP_ASSOCIATED(app, used_lables)
        used_lables.append(new_tag.label)
        tags.append(new_tag)

    algos = list(map(
        lambda algo: prepare_schema_config_variable_names({attr.fields(SchemaConfig).insight_types.name: algo}),
        schema_config.insight_types
    ))

    for algo in algos:
        new_tag = ImplicitTagTemplates.ALGO_ASSOCIATED(algo, used_lables)
        used_lables.append(new_tag.label)
        tags.append(new_tag)

    concepts = list(map(
        lambda concept: prepare_schema_config_variable_names({attr.fields(SchemaConfig).concepts.name: concept}),
        schema_config.concepts
    ))

    for concept in concepts:
        new_tag = ImplicitTagTemplates.CONCEPT_ASSOCIATED(concept, used_lables)
        used_lables.append(new_tag.label)
        tags.append(new_tag)

    return tags


def implicity_generate_tag_oriented_profile_schema_from_config(schema_config:SchemaConfig, tenantId, environmentId) -> ProfileSchema:
    return ProfileSchema(
        id=unique_id(),
        tenantId=tenantId,
        environmentId=environmentId,
        createdAt=utc_timestamp(),
        attributes=implicitly_generate_attribute_schemas(schema_config, include_tags=True),
        tags=implicitly_generate_tag_schemas(schema_config),
        groups=implicitly_generate_group_schemas(schema_config)
    )


def implicity_generate_heirarchical_profile_schema_from_config(schema_config:SchemaConfig, tenantId, environmentId) -> ProfileSchema:
    return ProfileSchema(
        id=unique_id(),
        tenantId=tenantId,
        environmentId=environmentId,
        createdAt=utc_timestamp(),
        attributes=implicitly_generate_attribute_schemas(schema_config, include_tags=False),
        hierarchy=implicity_generate_heirarchical_profile_schema_from_config(schema_config)
    )

