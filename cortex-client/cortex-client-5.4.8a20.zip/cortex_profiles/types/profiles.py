from typing import List, Optional

from attr import attrs, Factory

from cortex_profiles.schemas.schemas import CONTEXTS, VERSION
from cortex_profiles.types.attributes import ProfileAttribute, load_profile_attribute_from_dict
from cortex_profiles.types.utils import get_types_of_union
from cortex_profiles.utils import merge_dicts, unique_id, utc_timestamp
from cortex_profiles.types.utils import describableAttrib, CONTEXT_DESCRIPTION, VERSION_DESCRIPTION, ID_DESCRIPTION


@attrs(frozen=True)
class ProfileAttributeMapping(object):
    """
    A pointer that links attributes in a profiles to specific attribute.
    """
    attributeKey = describableAttrib(type=str, description="What is the name of the attribute in the profile?")
    attributeId = describableAttrib(type=str, description="What is the id for the attribute in the profile?")


@attrs(frozen=True)
class Profile(object):
    """
    A representation of an entity's profile with pointers to specific attributes.
    """
    tenantId = describableAttrib(type=str, description="Which tenant does this attribute belong in?")
    environmentId = describableAttrib(type=str, description="Which environment does this profile live in?")
    commitId = describableAttrib(type=str , description="Which commit is this linked based off of?")
    attributes = describableAttrib(type=List[ProfileAttributeMapping], default=Factory(list), description="Which attributes are currently associated with this profile?")
    # With Defaults
    createdAt = describableAttrib(type=str, factory=utc_timestamp, description="When was this profile created?")
    id = describableAttrib(type=str, factory=unique_id, description=ID_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    context = describableAttrib(type=str, default=CONTEXTS.PROFILE, description=CONTEXT_DESCRIPTION)

    @staticmethod
    def from_dict(d:dict) -> 'Profile':
        mapped_attributes = [] if not d.get("attributes") else d["attributes"]
        mapped_attributes = [
            ProfileAttributeMapping(**attribute) if not isinstance(attribute, ProfileAttributeMapping) else attribute
            for attribute in mapped_attributes
        ]
        return Profile(
            **merge_dicts(d, {
                "attributes": mapped_attributes
            })
        )


@attrs(frozen=True)
class ProfileSnapshot(Profile):
    """
    A representation of an entity's profile with attributes that are fully expanded.
    """

    # With Defaults
    attributes = describableAttrib(type=List[ProfileAttribute], factory=list, description="Which attributes exist in this snapshot?")
    context = describableAttrib(type=str, default=CONTEXTS.PROFILE_SNAPSHOT, description=CONTEXT_DESCRIPTION)

    @staticmethod
    def from_dict(d:dict) -> 'ProfileSnapshot':
        mapped_attributes = [] if not d.get("attributes") else d["attributes"]
        mapped_attributes = [
            load_profile_attribute_from_dict(attribute) if not isinstance(attribute, get_types_of_union(ProfileAttribute)) else attribute
            for attribute in mapped_attributes
        ]
        return ProfileSnapshot(
            **merge_dicts(d, {
                "attributes": mapped_attributes
            })
        )


@attrs(frozen=True)
class ProfileCommit(object):
    """
    A representation of the payload required to modify a entity's profile.
    """

    tenantId = describableAttrib(type=str, description="Which tenant does this attribute belong in?")
    environmentId = describableAttrib(type=str, description="Which environment does this profile live in?")
    profileId = describableAttrib(type=str, description="What profile is this commit on?")

    attributesModified = describableAttrib(type=Optional[List[ProfileAttributeMapping]], factory=list, description="Which attributes were modified in the commit?")
    attributesAdded = describableAttrib(type=Optional[List[ProfileAttributeMapping]], factory=list, description="Which attributes were added ?")
    attributesRemoved = describableAttrib(type=Optional[List[ProfileAttributeMapping]], factory=list, description="Which attributes were removed in the commit?")
    extends = describableAttrib(type=Optional[str], default=None, description="What is the id of the commit this commit extends?")

    createdAt = describableAttrib(type=str, factory=utc_timestamp, description="When was this profile commit created?")
    id = describableAttrib(type=str, factory=unique_id, description=ID_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    context = describableAttrib(type=str, default=CONTEXTS.PROFILE_COMMIT, description=CONTEXT_DESCRIPTION)



@attrs(frozen=True)
class ProfileSummary(object):
    """
    Summary of a profile ...
    TODO ... turn profile type into a list!
    """
    profileTypes = describableAttrib(type=str, description="What is the type of this profile?")
    profileId = describableAttrib(type=str, description="What is the id for this profile?")
    attributes = describableAttrib(type=str, description="How many attributes are currently in this profile?")

    # @classmethod
    # def from_profile_snapshot(cls, snapshot:ProfileSnapshot) -> 'ProfileSummary':
    #     return cls(
    #         profileType=snapshot
    #     )
    #
    # @classmethod
    # def from_profile(cls, profile: Profile):



@attrs(frozen=True)
class ProfileCommitSummary(object):
    """
    Summary of a commit ...
    """
    profileId = describableAttrib(type=str, description="What is the id of the profile this commit is relevant to?")
    commitId = describableAttrib(type=str, description="What is the id of the commit?")
    timestamp = describableAttrib(type=str, description="When was the commit created?")
    attributesAdded = describableAttrib(type=str, description="How many attributes were added by the commit?")
    attributesRemoved = describableAttrib(type=str, description="How many attributes were removed by the commit?")
    attributesModified = describableAttrib(type=str, description="How many attributes were modified by the commit?")

    @classmethod
    def from_profile_commit(cls, profileCommit:ProfileCommit) -> 'ProfileCommitSummary':
        return cls(
            profileId = profileCommit.profileId,
            commitId = profileCommit.id,
            timestamp = profileCommit.createdAt,
            attributesAdded = len(profileCommit.attributesAdded),
            attributesRemoved = len(profileCommit.attributesRemoved),
            attributesModified = len(profileCommit.attributesModified)
        )


@attrs(frozen=True)
class ProfileAttributeSummary(object):
    """
    Summary of an attribute ...
    """
    profileId = describableAttrib(type=str, description="What is the id of the profile this attribute is relevant to?")
    attributeId = describableAttrib(type=str, description="What is the id of this attribute?")
    timestamp = describableAttrib(type=str, description="What was this attribute created?")
    attributeKey = describableAttrib(type=str, description="What is the id of the attribute?")
    attributeType = describableAttrib(type=str, description="What type is this attribute?")
    attributeValueType = describableAttrib(type=str, description="What type is the value associated with this attribute?")

    @classmethod
    def from_profile_attribute(cls, profileAttr:ProfileAttribute) -> 'ProfileAttributeSummary':
        return cls(
            profileId = profileAttr.profileId,
            attributeId = profileAttr.id,
            timestamp = profileAttr.createdAt,
            attributeKey = profileAttr.attributeKey,
            attributeType = profileAttr.context,
            attributeValueType = profileAttr.attributeValue.context
        )
