from enum import Enum, auto, unique
from typing import List

from cortex_profiles.implicit.schema.implicit_tags import expand_tags_for_profile_attribute, ImplicitAttributeSubjects, ImplicitTags
from cortex_profiles.implicit.schema.implicit_templates import CONCEPT, attr_template, attr_name_template
from cortex_profiles.implicit.schema.utils import prepare_template_candidates_from_schema_fields
from cortex_profiles.schemas.schemas import CONTEXTS
from cortex_profiles.schemas.schemas import UNIVERSAL_ATTRIBUTES
from cortex_profiles.types.attribute_values import DimensionalAttributeContent, CounterAttributeContent, \
    TotalAttributeContent, AverageAttributeValue
from cortex_profiles.types.attribute_values import ListValue
from cortex_profiles.types.schema import ProfileValueTypeSummary, ProfileAttributeSchema
from cortex_profiles.types.schema_config import SchemaConfig, CONCEPT_SPECIFIC_INTERACTION_FIELDS, \
    CONCEPT_SPECIFIC_DURATION_FIELDS, APP_SPECIFIC_FIELDS, INTERACTION_FIELDS
from cortex_profiles.utils import EnumWithCamelCasedNamesAsDefaultValue, EnumWithNamesAsDefaultValue, merge_enum_values


@unique
class Metrics(EnumWithCamelCasedNamesAsDefaultValue):
    COUNT_OF = auto()
    TOTAL_DURATION = auto()
    DURATION_OF = auto()
    AVERAGE_COUNT_OF = auto()
    AVERAGE_DURATION_OF = auto()


@unique
class AttributeSections(Enum):
    INSIGHTS            = attr_name_template("insights[{{{insight_type}}}]")
    INTERACTED_WITH     = attr_name_template("interactedWith[{{{interaction_type}}}]")
    INPUT_TIMEFRAME     = attr_name_template("inputTimeframe[{{{timeframe}}}]")
    RELATED_TO_CONCEPT  = attr_name_template("relatedToConcept[{{{concept_title}}}]")
    LOGINS              = attr_name_template("logins[{{{app_id}}}]")
    DAILY_LOGINS        = attr_name_template("dailyLogins[{{{app_id}}}]")


@unique
class Patterns(EnumWithNamesAsDefaultValue):
    TYPE = auto()
    COUNT_OF_INSIGHT_INTERACTIONS = auto()
    COUNT_OF_CONCEPT_SPECIFIC_INSIGHT_INTERACTIONS = auto()
    TOTAL_DURATION_ON_CONCEPT_SPECIFIC_INSIGHT = auto()
    COUNT_OF_APP_SPECIFIC_LOGINS = auto()
    TOTAL_DURATION_OF_APP_SPECIFIC_LOGINS = auto()
    COUNT_OF_DAILY_APP_SPECIFIC_LOGINS = auto()
    TOTAL_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS = auto()
    AVERAGE_COUNT_OF_DAILY_APP_SPECIFIC_LOGINS = auto()
    AVERAGE_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS = auto()


@unique
class NameTemplates(Enum):
    TYPE = UNIVERSAL_ATTRIBUTES.TYPES
    COUNT_OF_INSIGHT_INTERACTIONS = merge_enum_values([Metrics.COUNT_OF, AttributeSections.INSIGHTS, AttributeSections.INTERACTED_WITH, AttributeSections.INPUT_TIMEFRAME])
    COUNT_OF_CONCEPT_SPECIFIC_INSIGHT_INTERACTIONS = merge_enum_values([Metrics.COUNT_OF, AttributeSections.INSIGHTS,  AttributeSections.INTERACTED_WITH, AttributeSections.RELATED_TO_CONCEPT, AttributeSections.INPUT_TIMEFRAME])
    TOTAL_DURATION_ON_CONCEPT_SPECIFIC_INSIGHT = merge_enum_values([Metrics.TOTAL_DURATION, AttributeSections.INSIGHTS,  AttributeSections.INTERACTED_WITH, AttributeSections.RELATED_TO_CONCEPT, AttributeSections.INPUT_TIMEFRAME])
    COUNT_OF_APP_SPECIFIC_LOGINS = merge_enum_values([Metrics.COUNT_OF, AttributeSections.LOGINS, AttributeSections.INPUT_TIMEFRAME])
    TOTAL_DURATION_OF_APP_SPECIFIC_LOGINS = merge_enum_values([Metrics.DURATION_OF, AttributeSections.LOGINS, AttributeSections.INPUT_TIMEFRAME])
    COUNT_OF_DAILY_APP_SPECIFIC_LOGINS = merge_enum_values([Metrics.COUNT_OF, AttributeSections.DAILY_LOGINS, AttributeSections.INPUT_TIMEFRAME])
    TOTAL_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS = merge_enum_values([Metrics.DURATION_OF, AttributeSections.DAILY_LOGINS, AttributeSections.INPUT_TIMEFRAME])
    AVERAGE_COUNT_OF_DAILY_APP_SPECIFIC_LOGINS = merge_enum_values([Metrics.AVERAGE_COUNT_OF, AttributeSections.DAILY_LOGINS, AttributeSections.INPUT_TIMEFRAME])
    AVERAGE_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS = merge_enum_values([Metrics.AVERAGE_DURATION_OF, AttributeSections.DAILY_LOGINS, AttributeSections.INPUT_TIMEFRAME])


@unique
class QuestionTemplates(EnumWithNamesAsDefaultValue):
    TYPE = "What are the different roles the profile adheres to?"
    COUNT_OF_INSIGHT_INTERACTIONS = attr_template("How many {{{insight_type}}} have been {{{optional_timeframe_adverb}}} {{{interaction_type}}} the profile?")
    COUNT_OF_CONCEPT_SPECIFIC_INSIGHT_INTERACTIONS = attr_template("How many {{{insight_type}}} related to a specific {{{singular_concept_title}}} have been {{{optional_timeframe_adverb}}} {{{interaction_type}}} the profile?")
    TOTAL_DURATION_ON_CONCEPT_SPECIFIC_INSIGHT = attr_template("How much time did the profile {{{optional_timeframe_adverb}}} spend on {{{insight_type}}} insights related to a specific {{{singular_concept_title}}}?")
    COUNT_OF_APP_SPECIFIC_LOGINS = attr_template("How many times did the profile {{{optional_timeframe_adverb}}} log into the {{{app_title}}} app?")
    TOTAL_DURATION_OF_APP_SPECIFIC_LOGINS = attr_template("How much time did the profile {{{optional_timeframe_adverb}}} spend logged into the {{{app_title}}} app?")
    COUNT_OF_DAILY_APP_SPECIFIC_LOGINS = attr_template("On a daily basis, how many times did the profile {{{optional_timeframe_adverb}}} log into the {{{app_title}}} App?")
    TOTAL_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS = attr_template("On a daily basis, how much time did the profile {{{optional_timeframe_adverb}}} spend logged into the {{{app_title}}} app?")
    AVERAGE_COUNT_OF_DAILY_APP_SPECIFIC_LOGINS = attr_template("On average, how many daily logins into the the {{{app_title}}} App did the profile {{{optional_timeframe_adverb}}} initiate?")
    AVERAGE_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS = attr_template("On average, how much time did the profile {{{optional_timeframe_adverb}}} spend daily logged into the {{{app_title}}} App?")


@unique
class DescriptionTemplates(EnumWithNamesAsDefaultValue):
    TYPE = "Different Types Profile Adheres to."
    COUNT_OF_INSIGHT_INTERACTIONS = attr_template("Total {{{insight_type}}} insights {{{optional_timeframe_adverb}}} {{{interaction_type}}} profile.")
    COUNT_OF_CONCEPT_SPECIFIC_INSIGHT_INTERACTIONS = attr_template("Total {{{insight_type}}} insights related to {{{plural_concept_title}}} {{{optional_timeframe_adverb}}} {{{interaction_type}}} profile.")
    TOTAL_DURATION_ON_CONCEPT_SPECIFIC_INSIGHT = attr_template("Total time {{{optional_timeframe_adverb}}} spent by profile on {{{insight_type}}} insights related to {{{plural_concept_title}}}.")
    COUNT_OF_APP_SPECIFIC_LOGINS = attr_template("Total times profile {{{optional_timeframe_adverb}}} logged into {{{app_title}}} app.")
    TOTAL_DURATION_OF_APP_SPECIFIC_LOGINS = attr_template("Total time profile {{{optional_timeframe_adverb}}} spent logged into {{{app_title}}} app")
    COUNT_OF_DAILY_APP_SPECIFIC_LOGINS = attr_template("Total times per day profile {{{optional_timeframe_adverb}}} logged into {{{app_title}}} app")
    TOTAL_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS = attr_template("Total time per day profile {{{optional_timeframe_adverb}}} spent logged into {{{app_title}}} app")
    AVERAGE_COUNT_OF_DAILY_APP_SPECIFIC_LOGINS = attr_template("Daily average of {{{optional_timeframe_adjective}}} logins for profile on {{{app_title}}} app.")
    AVERAGE_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS = attr_template("Daily average time profile {{{optional_timeframe_adverb}}} spent logged into {{{app_title}}} app ")


@unique
class TitleTemplates(EnumWithNamesAsDefaultValue):
    TYPE = "Profile Types"
    COUNT_OF_INSIGHT_INTERACTIONS = attr_template("Insights {{{interaction_type}}}")
    COUNT_OF_CONCEPT_SPECIFIC_INSIGHT_INTERACTIONS = attr_template("{{{plural_concept_title}}} {{{interaction_type}}}")
    TOTAL_DURATION_ON_CONCEPT_SPECIFIC_INSIGHT = attr_template("Duration on {{{plural_concept_title}}}")
    COUNT_OF_APP_SPECIFIC_LOGINS = "Total Logins"
    TOTAL_DURATION_OF_APP_SPECIFIC_LOGINS = "Duration of Logins"
    COUNT_OF_DAILY_APP_SPECIFIC_LOGINS = "Daily Login Count"
    TOTAL_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS = "Daily Login Durations"
    AVERAGE_COUNT_OF_DAILY_APP_SPECIFIC_LOGINS = "Average Daily Logins"
    AVERAGE_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS = "Average Login Duration"

# So do I want the tags and groups to be driven by the ones that appear in attributes ...
# If a tag or group does not appear in an attribute then its not part of the schema ... dont think that is what we are going for!
# Should expand the potential tags!
# Should have validation code to validate that attributes are not tagged with tags that dont exist ...
# And that all tags belong to a group

def expand_profile_attribute_schema(
            attribute_pattern: Patterns,
            attribute_filers:dict,
            valueType:ProfileValueTypeSummary,
            subject:str=None,
            attributeContext:str=CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE
        ) -> ProfileAttributeSchema:
    return ProfileAttributeSchema(
        name=NameTemplates[attribute_pattern.name].value.format(**{k: v.id for k, v in attribute_filers.items()}),
        type=attributeContext,
        valueType=valueType,
        label=TitleTemplates[attribute_pattern.name].value.format(**attribute_filers),
        description=DescriptionTemplates[attribute_pattern.name].value.format(**attribute_filers),
        questions=[QuestionTemplates[attribute_pattern.name].value.format(**attribute_filers)],
        tags=expand_tags_for_profile_attribute(attribute_filers, attributeContext, subject)
    )


def schema_for_concept_specific_interaction_attributes(schema_config:SchemaConfig) -> List[ProfileAttributeSchema]:
    candidates = prepare_template_candidates_from_schema_fields(schema_config, CONCEPT_SPECIFIC_INTERACTION_FIELDS)
    return [
        expand_profile_attribute_schema(
            Patterns.COUNT_OF_CONCEPT_SPECIFIC_INSIGHT_INTERACTIONS, cand,
            DimensionalAttributeContent.detailed_schema_type(cand[CONCEPT].id, CounterAttributeContent),
            subject=ImplicitAttributeSubjects.INSIGHT_INTERACTIONS.value,
            attributeContext=CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE
        )
        for cand in candidates
    ]


def schema_for_concept_specific_duration_attributes(schema_config: SchemaConfig) -> List[ProfileAttributeSchema]:
    candidates = prepare_template_candidates_from_schema_fields(schema_config, CONCEPT_SPECIFIC_DURATION_FIELDS)
    return [
        expand_profile_attribute_schema(
            Patterns.TOTAL_DURATION_ON_CONCEPT_SPECIFIC_INSIGHT, cand,
            DimensionalAttributeContent.detailed_schema_type(cand[CONCEPT].id, TotalAttributeContent),
            subject=ImplicitAttributeSubjects.INSIGHT_INTERACTIONS.value,
            attributeContext=CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE
        )
        for cand in candidates
    ]


def schema_for_interaction_attributes(schema_config: SchemaConfig) -> List[ProfileAttributeSchema]:
    candidates = prepare_template_candidates_from_schema_fields(schema_config, INTERACTION_FIELDS)
    return [
        expand_profile_attribute_schema(
            Patterns.COUNT_OF_INSIGHT_INTERACTIONS, cand,
            CounterAttributeContent.detailed_schema_type(),
            subject=ImplicitAttributeSubjects.INSIGHT_INTERACTIONS.value,
            attributeContext=CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE
        )
        for cand in candidates
    ]


def schema_for_app_specific_attributes(schema_config:SchemaConfig) -> List[ProfileAttributeSchema]:
    candidates = prepare_template_candidates_from_schema_fields(schema_config, APP_SPECIFIC_FIELDS)
    return (
        [
            expand_profile_attribute_schema(
                attribute_pattern, cand,
                CounterAttributeContent.detailed_schema_type(),
                subject=ImplicitAttributeSubjects.APP_USAGE.value,
                attributeContext=CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE
            )
            for attribute_pattern in [Patterns.COUNT_OF_APP_SPECIFIC_LOGINS, Patterns.COUNT_OF_DAILY_APP_SPECIFIC_LOGINS] for cand in candidates
        ]
        +
        [
            expand_profile_attribute_schema(
                attribute_pattern, cand,
                TotalAttributeContent.detailed_schema_type(),
                subject=ImplicitAttributeSubjects.APP_USAGE.value,
                attributeContext=CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE
            )
            for attribute_pattern in [Patterns.TOTAL_DURATION_OF_APP_SPECIFIC_LOGINS, Patterns.TOTAL_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS] for cand in candidates
        ]
        +
        [
            expand_profile_attribute_schema(
                attribute_pattern, cand,
                AverageAttributeValue.detailed_schema_type(),
                subject=ImplicitAttributeSubjects.APP_USAGE.value,
                attributeContext=CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE
            )
            for attribute_pattern in [Patterns.AVERAGE_COUNT_OF_DAILY_APP_SPECIFIC_LOGINS, Patterns.AVERAGE_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS] for cand in candidates
        ]
    )


def schemas_for_universal_attributes() -> List[ProfileAttributeSchema]:
    return [
        ProfileAttributeSchema(
            name=UNIVERSAL_ATTRIBUTES.TYPES,
            type=CONTEXTS.ASSIGNED_PROFILE_ATTRIBUTE,
            valueType=ListValue.detailed_schema_type("str"),
            label=TitleTemplates[Patterns.TYPE.name].value,
            description=DescriptionTemplates[Patterns.TYPE.name].value,
            questions=[QuestionTemplates[Patterns.TYPE.name].value],
            tags=[ImplicitTags.ASSIGNED.value]
        )
    ]