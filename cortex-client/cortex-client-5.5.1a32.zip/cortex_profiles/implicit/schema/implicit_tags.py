from typing import List, Mapping, Any, Callable, Optional

import attr
from cortex_profiles.utils import AttrsAsDict
from cortex_profiles.implicit.schema.implicit_groups import ImplicitGroups
from cortex_profiles.implicit.schema.implicit_templates import tag_template, APP_ID, INSIGHT_TYPE, CONCEPT, TIMEFRAME, \
    INTERACTION_TYPE
from cortex_profiles.schemas.schemas import CONTEXTS
from cortex_profiles.schemas.schemas import TIMEFRAMES
from cortex_profiles.types.schema import ProfileTagSchema, ProfileGroupSchema
from cortex_profiles.utils import label_generator


def profile_tag_schema_in_group(tagId:str, group:ProfileGroupSchema, **kwargs:Mapping[str, Any]) -> ProfileTagSchema:
    return ProfileTagSchema(id="{}/{}".format(group.id, tagId), group=group.id, **kwargs)


class ImplicitAttributeSubjects(AttrsAsDict):
    INSIGHT_INTERACTIONS = "insight-interactions"
    APP_USAGE = "application-usage"


class ImplicitTagDescriptions(AttrsAsDict):
    DECLARED = "Which attributes are declared by the profile themself?"
    OBSERVED = "Which attributes are observed?"
    INFERRED = "Which attributes are inferred?"
    ASSIGNED = "Which attributes are assigned to the profile?"
    RECENT = "Which attributes were generated using only recent data?"
    ETERNAL = "Which attributes were generated using all available data?"
    INTERACTION = "Which attributes capture a specific user interaction?"
    INSIGHT_INTERACTIONS = "Which attributes capture a part of the profile's interactions with insights?"
    APP_USAGE = "Which attributes capture a part of the profile's application usage behavior?"


class ImplicitTagLabels(AttrsAsDict):
    DECLARED = "ICD"
    OBSERVED = "ICO"
    INFERRED = "ICI"
    ASSIGNED = "ICA"
    RECENT = "DLR"
    ETERNAL = "DLE"
    INSIGHT_INTERACTIONS = "SII"
    APP_USAGE = "SAU"


class ImplicitTags(AttrsAsDict):
    DECLARED = profile_tag_schema_in_group("declared",
        ImplicitGroups.INFO_CLASSIFICATIONS, label=ImplicitTagLabels.DECLARED, description=ImplicitTagDescriptions.DECLARED)
    OBSERVED = profile_tag_schema_in_group("observed",
        ImplicitGroups.INFO_CLASSIFICATIONS, label=ImplicitTagLabels.OBSERVED, description=ImplicitTagDescriptions.OBSERVED)
    INFERRED = profile_tag_schema_in_group("inferred",
        ImplicitGroups.INFO_CLASSIFICATIONS, label=ImplicitTagLabels.INFERRED, description=ImplicitTagDescriptions.INFERRED)
    ASSIGNED = profile_tag_schema_in_group("assigned",
        ImplicitGroups.INFO_CLASSIFICATIONS, label=ImplicitTagLabels.ASSIGNED, description=ImplicitTagDescriptions.ASSIGNED)
    RECENT   = profile_tag_schema_in_group("recent",
        ImplicitGroups.DATA_LIMITS, label=ImplicitTagLabels.RECENT, description=ImplicitTagDescriptions.RECENT)
    ETERNAL  = profile_tag_schema_in_group("eternal",
        ImplicitGroups.DATA_LIMITS, label=ImplicitTagLabels.ETERNAL, description=ImplicitTagDescriptions.ETERNAL)
    INSIGHT_INTERACTIONS = profile_tag_schema_in_group(
        ImplicitAttributeSubjects.INSIGHT_INTERACTIONS, ImplicitGroups.SUBJECTS,
        label=ImplicitTagLabels.INSIGHT_INTERACTIONS, description=ImplicitTagDescriptions.INSIGHT_INTERACTIONS)
    APP_USAGE = profile_tag_schema_in_group(
        ImplicitAttributeSubjects.APP_USAGE, ImplicitGroups.SUBJECTS,
        label=ImplicitTagLabels.APP_USAGE, description=ImplicitTagDescriptions.APP_USAGE)


class ImplicitTagTemplateNames(AttrsAsDict):
    INTERACTION = tag_template("{{{interaction_type}}}")
    APP_ASSOCIATED = tag_template("{{{app_id}}}")
    ALGO_ASSOCIATED = tag_template("{{{insight_type_id}}}")
    CONCEPT_ASSOCIATED = tag_template("{{{concept_id}}}")


def expand_template_for_tag(tag_template_name:str) -> Callable:
    def callable(candidate, used_tags:Optional[List[str]]=None) -> ProfileTagSchema:
        """
        :param candidate:
        :param used_tags: Used for automatic label generation ... dont want to reuse tag labels ...
        :return:
        """
        tag_name = ImplicitTagTemplateNames[tag_template_name].format(**candidate)
        tag = profile_tag_schema_in_group(
            tag_name.replace("/","-"),
            ImplicitGroups[tag_template_name],
            label=None,
            description=DescriptionTemplates[tag_template_name].format(**candidate)
        )
        if used_tags is not None:
            tag = attr.evolve(tag, label=label_generator(tag.id, used_tags))
        return tag
    return callable


# https://stackoverflow.com/questions/31907060/python-3-enums-with-function-values
class ImplicitTagTemplates(AttrsAsDict):
    INTERACTION = expand_template_for_tag("INTERACTION")
    APP_ASSOCIATED = expand_template_for_tag("APP_ASSOCIATED")
    ALGO_ASSOCIATED = expand_template_for_tag("ALGO_ASSOCIATED")
    CONCEPT_ASSOCIATED = expand_template_for_tag("CONCEPT_ASSOCIATED")
    # TODO ... CUSTOM SUBJECT TAG ...


class DescriptionTemplates(AttrsAsDict):
    INTERACTION = tag_template("Which attributes are associated with insights {{{interaction_statement}}} the profile?")
    APP_ASSOCIATED = tag_template("Which attributes are associated with the {{{app_name}}} ({{{app_symbol}}})?")
    ALGO_ASSOCIATED = tag_template("Which attributes are associated with the {{{insight_type}}} ({{{insight_type_symbol}}}) Algorithm?")
    CONCEPT_ASSOCIATED = tag_template("Which attributes are associated with {{{concepts}}}?")


def expand_tags_for_profile_attribute(cand:Mapping[str, str], attribute_context:str, subject:str) -> List[str]:
    """
    Determines which tags are applicable to a specific attribute ...

    :param cand:
    :param attribute_context:
    :param subject:
    :return:
    """

    timeframe_tag = {
        TIMEFRAMES.RECENT: ImplicitTags.RECENT.id,
        TIMEFRAMES.HISTORIC: ImplicitTags.ETERNAL.id
    }.get(cand[TIMEFRAME].id, None)
    # TODO ... add custom timeframe tags ...?
    interaction_tag = None if INTERACTION_TYPE not in cand else ImplicitTagTemplates.INTERACTION(cand).id
    app_association_tag = None if APP_ID not in cand else ImplicitTagTemplates.APP_ASSOCIATED(cand).id
    algo_association_tag = None if INSIGHT_TYPE not in cand else ImplicitTagTemplates.ALGO_ASSOCIATED(cand).id
    concept_association_tag = None if CONCEPT not in cand else ImplicitTagTemplates.CONCEPT_ASSOCIATED(cand).id
    classification_tag = {
        CONTEXTS.DECLARED_PROFILE_ATTRIBUTE: ImplicitTags.DECLARED.id,
        CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE: ImplicitTags.OBSERVED.id,
        CONTEXTS.INFERRED_PROFILE_ATTRIBUTE: ImplicitTags.INFERRED.id,
        CONTEXTS.ASSIGNED_PROFILE_ATTRIBUTE: ImplicitTags.ASSIGNED.id,
    }.get(attribute_context, None)
    subject_tag = None if not subject else "{}/{}".format(ImplicitGroups.SUBJECTS.id, subject)
    return list(filter(
        lambda x: x,
        [interaction_tag, timeframe_tag, app_association_tag, algo_association_tag, concept_association_tag, classification_tag, subject_tag]
    ))


if __name__ == '__main__':
    print(dict(ImplicitTagTemplates))