from typing import List
from functools import reduce
from attr import attrs, asdict, evolve
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
        # a = asdict(self)
        # b = asdict(other)

        if not other:
            return self

        if not isinstance(other, ProfileGroupSchema):
            raise NotImplementedError("Cannot add {} and {} types.".format(ProfileGroupSchema.__name__, type(other).__name__))

        # Cant add ... if groupd ids are not the same ...
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
class ProfileSchema(object):
    tenantId = describableAttrib(type=str, description="Which tenant does this schema belong to?")
    environmentId = describableAttrib(type=str, description="Which environment was this schema created in?")
    # ----
    attributes = describableAttrib(type=List[ProfileAttributeSchema], converter=lambda l: list_converter(l, ProfileAttributeSchema), factory=list, description="What attributes are applicable to the profile schema?")
    tags = describableAttrib(type=List[ProfileTagSchema], converter=lambda l: list_converter(l, ProfileTagSchema), factory=list, description="What tags are applicable to attributes in the profile schema?")
    groups = describableAttrib(type=List[ProfileGroupSchema], converter=lambda l: list_converter(l, ProfileGroupSchema), factory=list, description="How does the schema define how tags are grouped?")
    profileType = describableAttrib(type=str, default=PROFILE_TYPES.END_USER, description="What type of profile adheres to this schema?")
    # ----
    id = describableAttrib(type=str, factory=unique_id, description="How can this piece of data be identified?")
    createdAt = describableAttrib(type=str, factory=utc_timestamp, description="When was this Profile Schema created?")
    version = describableAttrib(type=str, default=VERSION,
        description="What version of this piece of data's defining class is this piece of data based off of?")
    context = describableAttrib(type=str, default=CONTEXTS.PROFILE_SCHEMA,
        description="What is the type of this piece of data?")

    def __add__(self, other:'ProfileSchema') -> 'ProfileSchema':
        # a = asdict(self)
        # b = asdict(other)
        print("Adding {} and {}".format(ProfileSchemaSummary.from_profile_schema(self), ProfileSchemaSummary.from_profile_schema(other)))

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
        # Warn if duplicate attributes are detected ...

        unique_tags = merge_unique_objects_on(self.tags + other.tags, lambda x: x.id)
        # Warn if duplicate tags are detected ...

        unique_groups = merge_unique_objects_on(self.groups + other.groups, lambda x: x.id, lambda values: reduce(lambda x, y: x + y, values))
        # Warn if duplicate groups are detected ...

        return ProfileSchema(
            tenantId=self.tenantId,
            environmentId=self.environmentId,
            attributes=unique_attributes,
            groups=unique_groups,
            tags=unique_tags,
            profileType=self.profileType
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
