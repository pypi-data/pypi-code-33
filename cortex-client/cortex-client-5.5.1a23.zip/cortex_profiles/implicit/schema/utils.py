from itertools import product
from typing import List, Any, Callable

import attr
import pydash
from cortex_profiles.implicit.schema.implicit_templates import tag_template, TIMEFRAME, APP_ID, INTERACTION_TYPE, INSIGHT_TYPE, CONCEPT

from cortex_profiles.schemas.schemas import CONTEXTS
from cortex_profiles.types.attribute_values import ObjectValue
from cortex_profiles.types.attributes import DeclaredProfileAttribute
from cortex_profiles.types.schema import ProfileAttributeSchema, ProfileTagSchema, ProfileValueTypeSummary
from cortex_profiles.types.schema_config import SchemaConfig


def determine_detailed_type_of_attribute_value(attribute) -> ProfileValueTypeSummary:
    if attribute["attributeValue"]["context"] == CONTEXTS.DIMENSIONAL_PROFILE_ATTRIBUTE_VALUE:
        return ProfileValueTypeSummary(
            outerType = attribute["attributeValue"]["context"],
            innerTypes = [
                ProfileValueTypeSummary(outerType=attribute["attributeValue"]["contextOfDimension"]),
                ProfileValueTypeSummary(outerType=attribute["attributeValue"]["contextOfDimensionValue"])
            ]
        )
    else:
        return ProfileValueTypeSummary(outerType=attribute["attributeValue"]["context"])


def find_tag_in_group_for(group, key):
    return "{}/{}".format(group, key) if key else None


def prepare_schema_config_variable_names(d:dict) -> dict:
    renamer = {
        attr.fields(SchemaConfig).timeframes.name: TIMEFRAME,
        attr.fields(SchemaConfig).apps.name: APP_ID,
        attr.fields(SchemaConfig).insight_types.name: INSIGHT_TYPE,
        attr.fields(SchemaConfig).concepts.name: CONCEPT,
    }
    if attr.fields(SchemaConfig).interaction_types.name in d:
        renamer[attr.fields(SchemaConfig).interaction_types.name] = INTERACTION_TYPE
    if attr.fields(SchemaConfig).timed_interaction_types.name in d:
        renamer[attr.fields(SchemaConfig).timed_interaction_types.name] = INTERACTION_TYPE
    return pydash.rename_keys(d, renamer)


def prepare_template_candidates_from_schema_fields(schema_config:SchemaConfig, attr_fields:List) -> List[dict]:
    relevant_schema = attr.asdict(schema_config, recurse=False, filter=lambda a, v: a in attr_fields)
    candidates = [
        prepare_schema_config_variable_names(dict(zip(relevant_schema.keys(), z)))
        for z in list(product(*[x for x in relevant_schema.values()]))
    ]
    return candidates


def custom_attributes(
        attributes:List[dict],
        schema_config:SchemaConfig,
        attributeType:str=DeclaredProfileAttribute,
        valueType:type=ObjectValue,
        additional_tags:List[ProfileTagSchema]=[],
        additional_tag_templates:List[Callable[[dict], ProfileTagSchema]]=[],
        specific_to_schema_fields:List[Any]=[]) -> List[ProfileAttributeSchema]:
    candidates = prepare_template_candidates_from_schema_fields(schema_config, specific_to_schema_fields)
    return [
        ProfileAttributeSchema(
            name=tag_template(attribute["name"]).format(**cand),
            type=attr.fields(attributeType).context.name,
            valueType=valueType.detailed_schema_type(),
            label=attribute["label"],
            description=attribute["description"],
            questions=[attribute["question"]],
            tags=list(map(lambda x: x.id, list(map(lambda temp: temp(cand), additional_tag_templates)) + additional_tags)),
        )
        for cand in candidates
        for attribute in attributes
    ]