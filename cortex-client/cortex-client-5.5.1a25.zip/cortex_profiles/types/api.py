from attr import attrs

# from cortex_profiles.schemas.schemas import CONTEXTS
from cortex_profiles.types.utils import describableAttrib


@attrs(frozen=True)
class DeleteProfileResponse(object):
    """
    Profile Deletion Response ...
    # TODO ... add context to this???
    """
    snapshots_deleted = describableAttrib(type=int, default=0, description="How many snapshots were deleted for the profile?")
    commit_pointers_deleted = describableAttrib(type=int, default=0, description="How many commit pointers were deleted for the profile?")
    commits_deleted = describableAttrib(type=int, default=0, description="How many commits were deleted for the profile?")
    attributes_deleted = describableAttrib(type=int, default=0, description="How many attributes were deleted for the profile?")