from functools import reduce
from typing import List, Optional

from attr import attrs
from attr import evolve

from cortex_profiles.schemas.schemas import CONTEXTS, VERSION, PROFILE_TYPES
from cortex_profiles.types.utils import describableAttrib
from cortex_profiles.utils import list_converter
from cortex_profiles.utils import unique_id, utc_timestamp, merge_unique_objects_on


# TODO ... clean up how we summarize an attribute values type ...
# TODO ... figure out how to do a recursive type def ...
@attrs(frozen=True)
class ProfileValueTypeSummary(object):
    outerType = describableAttrib(type=str, description="What is the primary type of an attribute's value?")
    innerTypes = describableAttrib(type=List[dict], factory=list, description="What are the inner types of an attribute's value?")


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
    tags = describableAttrib(type=List[str], factory=list, description="What are the id's of all the tags that apply to this group?")
    version = describableAttrib(type=str, default=VERSION,
        description="What version of this piece of data's defining class is this piece of data based off of?")
    context = describableAttrib(type=str, default=CONTEXTS.PROFILE_ATTRIBUTE_GROUP,
        description="What is the type of this piece of data?")

    def __add__(self, other:'ProfileGroupSchema') -> 'ProfileGroupSchema':
        """
        Adding two groups together should effectively add their tags ...
        :param other:
        :return:
        """

        if not other:
            return self

        if not isinstance(other, ProfileGroupSchema):
            raise NotImplementedError("Cannot add {} and {} types.".format(ProfileGroupSchema.__name__, type(other).__name__))

        # Cant add ... if group ids are not the same ...
        if not self.id == other.id:
            raise NotImplementedError("Can not add groups with different ids.")

        if not self.version == other.version:
            raise NotImplementedError("Can not add groups with different versions.")

        unique_tags = list(set(self.tags + other.tags))
        return evolve(self, tags=unique_tags)


@attrs(frozen=True)
class ProfileAttributeSchema(object):
    name = describableAttrib(type=str, description="What is the name of the profile attribute?")
    type = describableAttrib(type=str, description="What is the type of the profile attribute?")
    valueType = describableAttrib(type=ProfileValueTypeSummary, description="What is the type of the profile attribute?")
    label = describableAttrib(type=str, description="What is a concise name for the attribute?")
    description = describableAttrib(type=str, description="What is the essential meaning of the attribute?")
    questions = describableAttrib(type=List[str], description="What questions is this attribute capable of answering?")
    tags = describableAttrib(type=List[str], description="What are the id's of all the tags that apply to this attribute?")


# def logging_identity(f):
#     def wrapper(*args, **kwargs):
#         print(args, kwargs)
#         return f(*args, **kwargs)
#     return wrapper
#
# def logging_expander(f):
#     def i(x):
#         print(x)
#         return f(**x)
#     return i


@attrs(frozen=True)
class ProfileHierarchySchema(object):
    name = describableAttrib(type=str, description="What is the name of the profile attribute?")
    description = describableAttrib(type=str, description="What is the essential meaning of this group?")
    attributes = describableAttrib(type=List[str], factory=list, description="What are the id's of all the attributes that fit within this group?")
    parents = describableAttrib(type=List[str], factory=list, description="What are the parents of this group of attributes ...?")
    children = describableAttrib(type=List[str], factory=list, description="What are the children of this group of attributes ...?")
    id = describableAttrib(type=str, factory=unique_id, description="What is the unique identifier for this group ...?")


@attrs(frozen=True)
class ProfileSchema(object):
    # ----
    attributes = describableAttrib(type=List[ProfileAttributeSchema], converter=lambda l: list_converter(l, ProfileAttributeSchema), factory=list, description="What attributes are applicable to the profile schema?")
    tags = describableAttrib(type=List[ProfileTagSchema], converter=lambda l: list_converter(l, ProfileTagSchema), factory=list, description="What tags are applicable to attributes in the profile schema?")
    groups = describableAttrib(type=List[ProfileGroupSchema], converter=lambda l: list_converter(l, ProfileGroupSchema), factory=list, description="How does the schema define how tags are grouped?")
    taxonomy = describableAttrib(type=List[ProfileHierarchySchema], converter=lambda l: list_converter(l, ProfileHierarchySchema), factory=list, description="How does the schema define how tags are grouped?")
    profileType = describableAttrib(type=str, default=PROFILE_TYPES.END_USER, description="What type of profile adheres to this schema?")
    # ----
    id = describableAttrib(type=str, factory=unique_id, description="How can this piece of data be identified?")
    createdAt = describableAttrib(type=str, factory=utc_timestamp, description="When was this Profile Schema created?")
    version = describableAttrib(type=str, default=VERSION,
        description="What version of this piece of data's defining class is this piece of data based off of?")
    context = describableAttrib(type=str, default=CONTEXTS.PROFILE_SCHEMA,
        description="What is the type of this piece of data?")
    # ----
    tenantId = describableAttrib(type=Optional[str], default=None, description="Which tenant does this schema belong to?")
    environmentId = describableAttrib(type=Optional[str], default=None, description="Which environment was this schema created in?")

    def __add__(self, other:'ProfileSchema') -> 'ProfileSchema':

        if not other:
            return self

        if not isinstance(other, ProfileSchema):
            raise NotImplementedError("Cannot add {} and {} types.".format(ProfileSchema.__name__, type(other).__name__))

        # Cant add ... if the profile types are not the same ...
        if not self.profileType == other.profileType:
            raise NotImplementedError("Can not add schemas with different profile types.")

        if not self.tenantId == other.tenantId:
            raise NotImplementedError("Can not add schemas with different tenants.")

        if not self.environmentId == other.environmentId:
            raise NotImplementedError("Can not add schemas within different environments.")

        unique_attributes = merge_unique_objects_on(self.attributes + other.attributes, lambda x: x.name)
        # TODO Warn if duplicate attributes are detected ...

        unique_tags = merge_unique_objects_on(self.tags + other.tags, lambda x: x.id)
        # TODO Warn if duplicate tags are detected ...

        unique_groups = merge_unique_objects_on(self.groups + other.groups, lambda x: x.id, lambda values: reduce(lambda x, y: x + y, values))
        # TODO Warn if duplicate groups are detected ...

        return evolve(self,
            attributes=unique_attributes,
            groups=unique_groups,
            tags=unique_tags,
        )


@attrs(frozen=True)
class ProfileSchemaSummary(object):
    """
    Summary of a schema ...
    """
    schemaId = describableAttrib(type=str, description="What is the id of the schema?")
    timestamp = describableAttrib(type=str, description="When was this schema created?")
    profileType = describableAttrib(type=str, description="What type of profile is this schema for?")
    attributes = describableAttrib(type=int, description="How many attributes are defined in the schema?")
    tags = describableAttrib(type=int, description="How many tags are defined in the schema?")
    groups = describableAttrib(type=int, description="How many groups are defined in the schema?")

    # ----

    @classmethod
    def from_profile_schema(cls, schema: ProfileSchema) -> 'ProfileSchemaSummary':
        return cls(
            schemaId=schema.id,
            timestamp=schema.createdAt,
            profileType=schema.profileType,
            attributes=None if schema.attributes is None else len(schema.attributes),
            tags=None if schema.tags is None else len(schema.tags),
            groups=None if schema.groups is None else len(schema.groups)
        )

@attrs(frozen=True)
class ProfileAttributeSchemaQuery(object):
    """
    """
    # ---------------
    attributesWithNames = describableAttrib(type=Optional[List[str]], default=None, description="...?")
    attributesWithAnyTags = describableAttrib(type=Optional[List[str]], default=None, description="...?")
    attributesWithAllTags = describableAttrib(type=Optional[List[str]], default=None, description="...?")
    attributesInAnyGroups = describableAttrib(type=Optional[List[str]], default=None, description="...?")
    attributesInAllGroups = describableAttrib(type=Optional[List[str]], default=None, description="...?")
    none = describableAttrib(type=Optional[bool], default=None, description="Should any attributes be queried?")
    all = describableAttrib(type=Optional[bool], default=None, description="Should all attributes be queried?")
    # ---------------
    intersection = describableAttrib(type=Optional[List['ProfileAttributeSchemaQuery']], default=None, description="Should this query intersect with another query?")
    union = describableAttrib(type=Optional[List['ProfileAttributeSchemaQuery']], default=None, description="How do I combine the results of multiple queries?")
    inverse = describableAttrib(type=Optional['ProfileAttributeSchemaQuery'], default=None, description="How do I invert the results of a query?")
    # ----------------
    intersection_as_default = describableAttrib(type=bool, default=True, description="If multiple options of the query are provided, will they be intersected by default?")


# TODO ... derive list of profile Hierarchy Schemas from recursive group ...
