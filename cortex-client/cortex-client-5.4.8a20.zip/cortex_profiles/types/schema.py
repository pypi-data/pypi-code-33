from typing import List

from attr import attrs

from cortex_profiles.schemas.schemas import CONTEXTS, VERSION
from cortex_profiles.types.utils import describableAttrib


# TODO ... clean up how we summarize an attribute values type ...
@attrs(frozen=True)
class ProfileValueTypeSummary(object):
    outerType = describableAttrib(type=str, description="What is the primary type of an attribute's value?")
    innerTypes = describableAttrib(type=List['ProfileValueTypeSummary'], factory=list, description="What are the inner types of an attribute's value?")


@attrs(frozen=True)
class ProfileTagSchema(object):
    id = describableAttrib(type=str, description="How can this piece of data be identified?")
    label = describableAttrib(type=str, description="What is a short symbol for this tag?")
    description = describableAttrib(type=str, description="What does it mean for attributes to be tagged with this tag?")
    group = describableAttrib(type=str, description="What group is this tag in?")
    version = describableAttrib(type=str, default=VERSION,
        description="What version of this piece of data's defining class is this piece of data based off of?")
    context = describableAttrib(type=str, default=CONTEXTS.PROFILE_ATTRIBUTE_TAG,
        description="What is the type of this piece of data?")


@attrs(frozen=True)
class ProfileGroupSchema(object):
    id = describableAttrib(type=str, description="How can this piece of data be identified?")
    label = describableAttrib(type=str, description="What is a short symbol for this group?")
    description = describableAttrib(type=str, description="What is similar about the tags in this group?")
    tags = describableAttrib(type=List[str], default=[], description="What are the id's of all the tags that apply to this group?")
    version = describableAttrib(type=str, default=VERSION,
        description="What version of this piece of data's defining class is this piece of data based off of?")
    context = describableAttrib(type=str, default=CONTEXTS.PROFILE_ATTRIBUTE_GROUP,
        description="What is the type of this piece of data?")


@attrs(frozen=True)
class ProfileAttributeSchema(object):
    name = describableAttrib(type=str, description="What is the name of the profile attribute?")
    type = describableAttrib(type=str, description="What is the type of the profile attribute?")
    valueType = describableAttrib(type=ProfileValueTypeSummary, description="What is the type of the profile attribute?")
    label = describableAttrib(type=str, description="What is a concise name for the attribute?")
    description = describableAttrib(type=str, description="What is the essential meaning of the attribute?")
    questions = describableAttrib(type=List[str], description="What questions is this attribute capable of answering?")
    tags = describableAttrib(type=List[str], description="What are the id's of all the tags that apply to this attribute?")


@attrs(frozen=True)
class ProfileSchema(object):
    id = describableAttrib(type=str, description="How can this piece of data be identified?")
    tenantId = describableAttrib(type=str, description="Which tenant does this schema belong to?")
    environmentId = describableAttrib(type=str, description="Which environment was this schema created in?")
    createdAt = describableAttrib(type=str, description="When was this Profile Schema created?")
    # ----
    attributes = describableAttrib(type=List[ProfileAttributeSchema], description="What attributes are applicable to the profile schema?")
    tags = describableAttrib(type=List[ProfileTagSchema], description="What tags are applicable to attributes in the profile schema?")
    groups = describableAttrib(type=List[ProfileGroupSchema], description="How does the schema define how tags are grouped?")
    profileType = describableAttrib(type=str, default=CONTEXTS.END_USER_PROFILE, description="What type of profile adheres to this schema?")
    # ----
    version = describableAttrib(type=str, default=VERSION,
        description="What version of this piece of data's defining class is this piece of data based off of?")
    context = describableAttrib(type=str, default=CONTEXTS.PROFILE_SCHEMA,
        description="What is the type of this piece of data?")
