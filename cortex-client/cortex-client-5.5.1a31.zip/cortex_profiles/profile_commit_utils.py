from typing import Optional, List
from typing import Tuple

import attr
import pydash
from cortex_profiles import queries, utils
from cortex_profiles.types.attributes import ProfileAttribute
from cortex_profiles.types.general import OrderedList
from cortex_profiles.types.profiles import Profile, ProfileCommit, ProfileAttributeMapping


def extend_commit_with_attributes(commit:ProfileCommit, attributes_added:List[ProfileAttributeMapping],
                                  attributes_modified:List[ProfileAttributeMapping], attributes_removed:List[ProfileAttributeMapping]) -> ProfileCommit:
    return utils.modify_attr_class(
        commit,
        dict(
            id=utils.unique_id(),
            createdAt=utils.utc_timestamp(),
            extends=commit.id,
            attributesAdded=attributes_added,
            attributesModified=attributes_modified,
            attributesRemoved=attributes_removed
        )
    )


def apply_commit_to_profile(commit:ProfileCommit, profile:Profile) -> Profile:
    """
    Applied a SINGLE commit to a profile.
    :param commit:
    :param profile:
    :return:
    """
    new_profile_dict = attr.asdict(profile)

    attributes_removed = list(map(attr.asdict, commit.attributesRemoved))
    attributes_modified = list(map(attr.asdict, commit.attributesModified))
    attributes_added = list(map(attr.asdict, commit.attributesAdded))

    # helpers.print_json_with_header("Attrs before everything: ", new_profile_dict["attributes"])

    # Remove attributes from profile
    attributeKeys_to_remove_from_profile = [attribute["attributeKey"] for attribute in attributes_removed]
    new_profile_dict["attributes"] = [attribute for attribute in new_profile_dict["attributes"] if attribute not in attributeKeys_to_remove_from_profile]

    # helpers.print_json_with_header("Attrs after removed: ", new_profile_dict["attributes"])

    # Modify attributes in profile
    attribute_modification_map = {attribute["attributeKey"]: attribute for attribute in attributes_modified}
    new_profile_dict["attributes"] = [
        attribute_modification_map.get(attribute["attributeKey"], attribute)
        for attribute in new_profile_dict["attributes"]
        if attribute["attributeKey"] not in attributeKeys_to_remove_from_profile
    ]

    # helpers.print_json_with_header("Attrs after modification: ", new_profile_dict["attributes"])

    # Add attributes to profile
    new_profile_dict["attributes"] = new_profile_dict["attributes"] + attributes_added

    # helpers.print_json_with_header("Attrs after added: ", new_profile_dict["attributes"])

    # Return attributes to ProfileAttributeMappings
        # new_profile_dict["attributes"] = [ProfileAttributeMapping(**d) for d in new_profile_dict["attributes"]]
        # from dict below replaces the line above ...
    return Profile.from_dict(new_profile_dict)



def apply_commits_onto_profile(commits:Optional[OrderedList[ProfileCommit]], profile:Profile) -> Profile:
    """
    Applies a LIST OF COMMITS to a profile.
    :param commits:
    :param profile:
    :return:
    """
    if not commits:
        return profile
    head, tail = commits[0], commits[1:]
    return apply_commits_onto_profile(tail, apply_commit_to_profile(head, profile))



def determine_attribute_modification_deltas_relevant_to_profile(attributes:List[ProfileAttribute], profile: Profile) -> Tuple[List[ProfileAttributeMapping], List[ProfileAttributeMapping], List[ProfileAttributeMapping]]:
    """
    Figure out if the attribute is new ... already exists ... is a modification ...

    :param attribute:
    :param profile:
    :return:
    """
    # helpers.print_attr_class_with_header("profile", profile)
    profile_attribute_key_id_mappings = {attribute.attributeKey: attribute.attributeId for attribute in profile.attributes}
    attributes_added  = [
        ProfileAttributeMapping(attributeKey=attribute.attributeKey, attributeId=attribute.id)
        for attribute in attributes
        if attribute.attributeKey not in profile_attribute_key_id_mappings
    ]
    # helpers.print_attr_class_with_header("attributes_added", attributes_added)
    attributes_modified = [
        ProfileAttributeMapping(attributeKey=attribute.attributeKey, attributeId=attribute.id)
        for attribute in attributes
        if attribute.attributeKey in profile_attribute_key_id_mappings and profile_attribute_key_id_mappings[attribute.attributeKey] != attribute.id
    ]
    # helpers.print_attr_class_with_header("attributes_modified", attributes_modified)
    attributes_removed = []
    # helpers.print_attr_class_with_header("attributes_removed", attributes_removed)
    return attributes_added, attributes_modified, attributes_removed



# ========================================================================================================================


def apply_commit_to_attributes(attributes: List[ProfileAttributeMapping], commit: ProfileCommit) -> List[ProfileAttributeMapping]:
    """
    This takes a commit and a current list of attributes and transforms the current attributes based off of the commit ...
    :param attributes:
    :param commit:
    :return:
    """
    # Remove attributes ...
    profile_paths_to_remove = pydash.map_(commit.attributesRemoved, "profilePath")
    print("Profile Paths to Ignore {}".format(profile_paths_to_remove))
    attributes = filter(
        lambda x: x["profilePath"] not in profile_paths_to_remove ,
        attributes
    )

    # Modify Attributes
    # Make a map of all the attributes to be modified ...
    modificationMap = pydash.collections.key_by(commit.attributesModified, "profilePath")
    print("Profile Paths to Modify {}".format(modificationMap))
    attributes = [modificationMap.get(attributeMapping["profilePath"], attributeMapping["attributeId"]) for attributeMapping in attributes]

    # Add Attributes ...
    attributes = attributes + commit.attributesAdded

    return attributes


def profile_commit_chain_from_recursive_commit(recursive_commit_query_result:dict) -> OrderedList[ProfileCommit]:
    """
    Turns a recursive commit into an ordered list of commits
    :param recursive_commit_query_result:
    :return:
    """
    ordered_commits_from_newest_to_oldest = []
    ordered_commits_from_newest_to_oldest.append(
        queries.extract_profile_commit_from_mongo_payload(recursive_commit_query_result)
    )
    ordered_commits_from_newest_to_oldest.extend(
        list(map(
            queries.extract_profile_commit_from_mongo_payload,
            recursive_commit_query_result.get("recursive_commits", [])
        ))
    )
    return ordered_commits_from_newest_to_oldest
