from typing import Optional, List

from attr import attrs, attrib, Factory
from cortex_profiles.types.profiles import ProfileAttributeMapping, ProfileCommit
from cortex_profiles.schemas.schemas import CONTEXTS, VERSION


@attrs(frozen=True, auto_attribs=True)
class LatestCommitPointer(object):
    id: str  # What is the id of this piece of data?
    commitId: str  # What commit does this pointer point to?
    profileId: str  # Who is this pointer for?
    environmentId: str  # What environment is this pointer in?
    tenantId: str  # What tenant is this pointer in?
    createdAt: str  # When was this pointer created?
    context: str = CONTEXTS.SESSION  # What is the type of the data being captured by this data type?
    version: str = VERSION  # What version of the data type is being adhered to?


@attrs(frozen=True, auto_attribs=True)
class RecursiveProfileCommit(object):
    id: str  # What is the id of this piece of data? aka commitId
    createdAt: str  # When was this snapshot created?
    tenantId: str  # Which tenant does this attribute belong in?
    environmentId: str  # Which environment does this profile live in?
    profileId: str  # What profile is this commit on?
    extends: Optional[str] = None  # What is the id of the commit this commit extends?
    recursive_commits = List[ProfileCommit]
    attributesModified: Optional[List[ProfileAttributeMapping]] = []  # Which attributes were modified in the commit?
    attributesAdded: Optional[List[ProfileAttributeMapping]] = []  # Which attributes were added ?
    attributesRemoved: Optional[List[ProfileAttributeMapping]] = []  # Which attributes were removed in the commit?
    version: str = VERSION  # What version of the system does this piece of data adhere to?
    context: str = CONTEXTS.PROFILE_COMMIT  # What is the type of the data being captured by this data type?


@attrs(frozen=True, auto_attribs=True)
class ProfileLock(object):
    lockerId: str # Who locked the profile?
    profileId: str # What profile is locked?
    locked: str # When was the profile locked?
    ttl: int # How many seconds will the lock last for before breaking?
    lockedUntil: str # Until when will this profile remain locked if not already unlocked?
    unlocked: Optional[str] # When was the profile unlocked?
    isLocked: bool # Is the profile still locked?