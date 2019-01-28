import itertools
import re
from enum import unique
from typing import List, Mapping, Any, Tuple, Callable, Optional

import attr
from cortex_profiles.implicit.schema.implicit_groups import ImplicitGroups
from cortex_profiles.implicit.schema.implicit_templates import tag_template, APP_ID, INSIGHT_TYPE, CONCEPT, TIMEFRAME, \
    INTERACTION_TYPE
from cortex_profiles.schemas.schemas import CONTEXTS
from cortex_profiles.types.schema import ProfileTagSchema
from cortex_profiles.utils import EnumWithNamesAsDefaultValue, label_generator


def profile_tag_schema_in_group(tagId:str, group:ImplicitGroups, **kwargs:Mapping[str, Any]) -> ProfileTagSchema:
    return ProfileTagSchema(id="{}/{}".format(group.value.id, tagId), group=group.value.id, **kwargs)


@unique
class ImplicitAttributeSubjects(EnumWithNamesAsDefaultValue):
    INSIGHT_INTERACTIONS = "insight-interactions"
    APP_USAGE = "application-usage"


@unique
class ImplicitTagDescriptions(EnumWithNamesAsDefaultValue):
    DECLARED = "Which attributes are declared by the profile themself?"
    OBSERVED = "Which attributes are observed?"
    INFERRED = "Which attributes are inferred?"
    ASSIGNED = "Which attributes are assigned to the profile?"
    RECENT = "Which attributes were generated using only recent data?"
    ETERNAL = "Which attributes were generated using all available data?"
    INTERACTION = "Which attributes capture a specific user interaction?"
    INSIGHT_INTERACTIONS = "Which attributes capture a part of the profile's interactions with insights?"
    APP_USAGE = "Which attributes capture a part of the profile's application usage behavior?"


@unique
class ImplicitTagLabels(EnumWithNamesAsDefaultValue):
    DECLARED = "ICD"
    OBSERVED = "ICO"
    INFERRED = "ICI"
    ASSIGNED = "ICA"
    RECENT = "DLR"
    ETERNAL = "DLE"
    INSIGHT_INTERACTIONS = "SII"
    APP_USAGE = "SAU"


@unique
class ImplicitTags(EnumWithNamesAsDefaultValue):
    DECLARED = profile_tag_schema_in_group("declared",
        ImplicitGroups.INFO_CLASSIFICATIONS, label=ImplicitTagLabels.DECLARED.value, description=ImplicitTagDescriptions.DECLARED.value)
    OBSERVED = profile_tag_schema_in_group("observed",
        ImplicitGroups.INFO_CLASSIFICATIONS, label=ImplicitTagLabels.OBSERVED.value, description=ImplicitTagDescriptions.OBSERVED.value)
    INFERRED = profile_tag_schema_in_group("inferred",
        ImplicitGroups.INFO_CLASSIFICATIONS, label=ImplicitTagLabels.INFERRED.value, description=ImplicitTagDescriptions.INFERRED.value)
    ASSIGNED = profile_tag_schema_in_group("assigned",
        ImplicitGroups.INFO_CLASSIFICATIONS, label=ImplicitTagLabels.ASSIGNED.value, description=ImplicitTagDescriptions.ASSIGNED.value)
    RECENT   = profile_tag_schema_in_group("recent",
        ImplicitGroups.DATA_LIMITS, label=ImplicitTagLabels.RECENT.value, description=ImplicitTagDescriptions.RECENT.value)
    ETERNAL  = profile_tag_schema_in_group("eternal",
        ImplicitGroups.DATA_LIMITS, label=ImplicitTagLabels.ETERNAL.value, description=ImplicitTagDescriptions.ETERNAL.value)
    INSIGHT_INTERACTIONS = profile_tag_schema_in_group(
        ImplicitAttributeSubjects.INSIGHT_INTERACTIONS.value, ImplicitGroups.SUBJECTS,
        label=ImplicitTagLabels.INSIGHT_INTERACTIONS.value, description=ImplicitTagDescriptions.INSIGHT_INTERACTIONS.value)
    APP_USAGE = profile_tag_schema_in_group(
        ImplicitAttributeSubjects.APP_USAGE.value, ImplicitGroups.SUBJECTS,
        label=ImplicitTagLabels.APP_USAGE.value, description=ImplicitTagDescriptions.APP_USAGE.value)



@unique
class ImplicitTagTemplateNames(EnumWithNamesAsDefaultValue):
    INTERACTION = tag_template("{{{interaction_type}}}")
    APP_ASSOCIATED = tag_template("{{{app_id}}}")
    ALGO_ASSOCIATED = tag_template("{{{insight_type_id}}}")
    CONCEPT_ASSOCIATED = tag_template("{{{concept_id}}}")



def expand_template_for_tag(template:ImplicitTagTemplateNames) -> Tuple[Callable]:
    def callable(candidate, used_tags:Optional[List[str]]=None):
        tag_name = template.value.format(**candidate)
        tag = profile_tag_schema_in_group(
            tag_name.replace("/","-"),
            ImplicitGroups[template.name],
            label=None,
            description=DescriptionTemplates[template.name].value.format(**candidate)
        )
        if used_tags is not None:
            tag = attr.evolve(tag, label=label_generator(tag.id, used_tags))
        return tag
    return (callable, )


@unique
# https://stackoverflow.com/questions/31907060/python-3-enums-with-function-values
class ImplicitTagTemplates(EnumWithNamesAsDefaultValue):
    INTERACTION = expand_template_for_tag(ImplicitTagTemplateNames.INTERACTION)
    APP_ASSOCIATED = expand_template_for_tag(ImplicitTagTemplateNames.APP_ASSOCIATED)
    ALGO_ASSOCIATED = expand_template_for_tag(ImplicitTagTemplateNames.ALGO_ASSOCIATED)
    CONCEPT_ASSOCIATED = expand_template_for_tag(ImplicitTagTemplateNames.CONCEPT_ASSOCIATED)
    # TODO ... CUSTOM SUBJECT TAG ...

    def __call__(self, *args, **kwargs):
        return self.value[0](*args, **kwargs)

@unique
class DescriptionTemplates(EnumWithNamesAsDefaultValue):
    INTERACTION = tag_template("Which attributes are associated with insights {{{interaction_statement}}} the profile?")
    APP_ASSOCIATED = tag_template("Which attributes are associated with the {{{app_name}}} ({{{app_symbol}}})?")
    ALGO_ASSOCIATED = tag_template("Which attributes are associated with the {{{insight_type}}} ({{{insight_type_symbol}}}) Algorithm?")
    CONCEPT_ASSOCIATED = tag_template("Which attributes are associated with {{{concepts}}}?")


def expand_tags_for_profile_attribute(cand:Mapping[str, str], attribute_context:str, subject:str) -> List[str]:
    timeframe_tag = None if TIMEFRAME not in cand else (
        ImplicitTags.ETERNAL.value.id if cand[TIMEFRAME].id == "eternal" else (ImplicitTags.RECENT.value.id if cand[TIMEFRAME].id == "recent" else None)
    )
    interaction_tag = None if INTERACTION_TYPE not in cand else ImplicitTagTemplates.INTERACTION(cand).id
    app_association_tag = None if APP_ID not in cand else ImplicitTagTemplates.APP_ASSOCIATED(cand).id
    algo_association_tag = None if INSIGHT_TYPE not in cand else ImplicitTagTemplates.ALGO_ASSOCIATED(cand).id
    concept_association_tag = None if CONCEPT not in cand else ImplicitTagTemplates.CONCEPT_ASSOCIATED(cand).id
    classification_tag = None if not attribute_context else (
        ImplicitTags.DECLARED.value.id if attribute_context == CONTEXTS.DECLARED_PROFILE_ATTRIBUTE else (
            ImplicitTags.OBSERVED.value.id if attribute_context == CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE else (
                ImplicitTags.INFERRED.value.id if attribute_context == CONTEXTS.INFERRED_PROFILE_ATTRIBUTE else (
                    ImplicitTags.ASSIGNED.value.id if attribute_context == CONTEXTS.ASSIGNED_PROFILE_ATTRIBUTE else (
                        None
                    )
                )
            )
        )
    )
    subject_tag = None if not subject else "{}/{}".format(ImplicitGroups.SUBJECTS.value.id, subject)
    return list(filter(
        lambda x: x,
        [interaction_tag, timeframe_tag, app_association_tag, algo_association_tag, concept_association_tag, classification_tag, subject_tag]
    ))
