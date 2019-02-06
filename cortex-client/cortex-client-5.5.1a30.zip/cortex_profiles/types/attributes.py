import copy
from enum import auto, unique
from typing import List, Union

from attr import attrs, validators, Factory

from cortex_profiles.schemas.schemas import CONTEXTS, VERSION
from cortex_profiles.types.attribute_values import BaseAttributeValue
from cortex_profiles.types.attribute_values import PercentageAttributeValue, PercentileAttributeValue, \
    AverageAttributeValue, TotalAttributeContent, CounterAttributeContent, DimensionalAttributeContent
from cortex_profiles.types.attribute_values import load_profile_attribute_value_from_dict
from cortex_profiles.types.utils import describableAttrib, CONTEXT_DESCRIPTION
from cortex_profiles.utils import unique_id, converter_for_classes, EnumWithNamesAsDefaultValue, utc_timestamp


# TODO - EXTEND attribute union type with rest of primitives
ProfileAttributeValueTypes = (
    PercentageAttributeValue,
    PercentileAttributeValue,
    AverageAttributeValue,
    TotalAttributeContent,
    CounterAttributeContent,
    DimensionalAttributeContent
)

@unique
class ProfileAttributeClassifications(EnumWithNamesAsDefaultValue):
    inferred = auto()
    declared = auto()
    observed = auto()
    assigned = auto()


@attrs(frozen=True)
class ProfileAttribute(object):
    profileId = describableAttrib(type=str, description="Who is this attribute applicable to?")
    attributeKey = describableAttrib(type=str, description="What is the id of the attribute?")
    attributeValue = describableAttrib(
        type=Union[ProfileAttributeValueTypes],
        validator=[validators.instance_of(BaseAttributeValue)],
        converter=lambda x: converter_for_classes(x, BaseAttributeValue, dict_constructor=load_profile_attribute_value_from_dict),
        description="What value is associated with the profile attribute?"
    )
    context = describableAttrib(type=str, description="What is the type of the data being captured by this data type?")
    # With Defaults
    createdAt = describableAttrib(type=str, factory=utc_timestamp, description="When was this attribute created?")
    tenantId = describableAttrib(type=str, default=None, description="What tenant does this attribute belong to?")
    environmentId = describableAttrib(type=str, default=None, description="What environment was this attribute created in?")
    onLatestProfile = describableAttrib(type=bool, default=True, description="Is this attribute on the latest profile?")
    commits = describableAttrib(type=List[str], factory=list, description="What commits is this attribute associated with?")
    id = describableAttrib(type=str, default=Factory(unique_id), description="What is the id of this piece of data?")
    version = describableAttrib(type=str, default=VERSION, description="What version of the data type is being adhered to?")


@attrs(frozen=True)
class InferredProfileAttribute(ProfileAttribute):
    classification = describableAttrib(type=str, default=ProfileAttributeClassifications.inferred.name, description="What is the classification of this profile attribute?")
    context = describableAttrib(type=str, default=CONTEXTS.INFERRED_PROFILE_ATTRIBUTE, description=CONTEXT_DESCRIPTION)


@attrs(frozen=True)
class ObservedProfileAttribute(ProfileAttribute):
    classification = describableAttrib(type=str, default=ProfileAttributeClassifications.observed.name, description="What is the classification of this profile attribute?")
    context = describableAttrib(type=str, default=CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE, description=CONTEXT_DESCRIPTION)


@attrs(frozen=True)
class DeclaredProfileAttribute(ProfileAttribute):
    classification = describableAttrib(type=str, default=ProfileAttributeClassifications.declared.name, description="What is the classification of this profile attribute?")
    context = describableAttrib(type=str, default=CONTEXTS.DECLARED_PROFILE_ATTRIBUTE, description=CONTEXT_DESCRIPTION)


@attrs(frozen=True)
class AssignedProfileAttribute(ProfileAttribute):
    classification = describableAttrib(type=str, default=ProfileAttributeClassifications.assigned.name, description="What is the classification of this profile attribute?")
    context = describableAttrib(type=str, default=CONTEXTS.ASSIGNED_PROFILE_ATTRIBUTE, description=CONTEXT_DESCRIPTION)

# ProfileAttribute = Union[InferredProfileAttribute, DeclaredProfileAttribute, ObservedProfileAttribute]
# ProfileAttributeKinds = Union[
#     PercentageAttributeContent,
#     CounterAttributeContent,
#     DimensionalAttributeContent,
#     MultiDimensionalAttributeContent
# ]


def load_profile_attribute_from_dict(d: dict) -> ProfileAttribute:
    # updated_dict["attributeValue"] = load_profile_attribute_value_from_dict(updated_dict["attributeValue"])
    updated_dict = copy.deepcopy(d)
    # Deep Copy works as expected with Nones :: copy.deepcopy({"a": {"b": None}}) => Out[18]: {'a': {'b': None}}
    # print("Normal dict ", d)
    # print("Updated dict ", updated_dict)
    if d.get("context") == CONTEXTS.INFERRED_PROFILE_ATTRIBUTE:
        return InferredProfileAttribute(**updated_dict)
    if d.get("context") == CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE:
        return ObservedProfileAttribute(**updated_dict)
    if d.get("context") == CONTEXTS.DECLARED_PROFILE_ATTRIBUTE:
        return DeclaredProfileAttribute(**updated_dict)
    if d.get("context") == CONTEXTS.ASSIGNED_PROFILE_ATTRIBUTE:
        return AssignedProfileAttribute(**updated_dict)
    return None