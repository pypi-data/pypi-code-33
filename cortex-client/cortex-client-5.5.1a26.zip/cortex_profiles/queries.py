import copy
from typing import List
import attr
import pymongo
from cortex_profiles import utils
from cortex_profiles.types.attributes import ProfileAttribute
from cortex_profiles.types.general import FindQuery
from cortex_profiles.types.profiles import ProfileCommit, ProfileAttributeMapping
from pymongo import ReplaceOne, UpdateMany

FIND_OR_CREATE_ARGS = {
    "upsert" : True,
    "return_document" : pymongo.ReturnDocument.AFTER
}


def find_latest_snapshot_for_profile_or_create(snapshots_collection, profileId, default_profile):
    snapshot = find_or_create_atomically(
        snapshots_collection,
        {"profileId": profileId},
        default_profile,
        {
            "sort": [('createdAt', pymongo.DESCENDING)],
            "upsert": True,
            "return_document": pymongo.ReturnDocument.AFTER
        }
    )
    del snapshot["_id"]
    return snapshot



def find_or_create_atomically(mongo_collection, to_be_found,
                               to_be_created_if_not_found,
                               additional_args=FIND_OR_CREATE_ARGS):
    return mongo_collection.find_one_and_update(
       to_be_found,
       {"$setOnInsert": to_be_created_if_not_found},
       **additional_args
   )


def append_leaf_queries_with(query:object, leaf_appender:dict) -> dict:
    # Recursively add tenantId and envrionmentId constraints to the query ... to support $ands and $ors ...
    if isinstance(query, dict) and (("$and" in query) or ("$or" in query)):
        return {
            k:  append_leaf_queries_with(v, leaf_appender)
            for k, v in query.items()
        }
    elif isinstance(query, dict):
        return utils.merge_dicts(query, leaf_appender)
    elif isinstance(query, list):
        return list(map(
            lambda x: append_leaf_queries_with(x, leaf_appender),
            query
        ))
    else:
        return query


def derive_operations_to_unmark_changed_attributes_as_latest(oldCommit: ProfileCommit, newCommit: ProfileCommit) -> list:
    """
    Operation to mark all modified attributes from the old commit as not the latest ...
    :param oldCommit:
    :param newCommit:
    :return:
    """
    return [
        UpdateMany(
            query_to_find_attributes_associated_with_commit_by_key(
                oldCommit, [attribute.attributeKey for attribute in newCommit.attributesModified]
            ),
            {"$set": {"onLatestProfile": False}}
        )
    ]


def derive_operations_to_save_modified_attributes_and_associate_them_with_latest_commit(attributes: List[ProfileAttribute], newCommit: ProfileCommit):
    # For attributes we are modifying ...
    #   .. we need to clone them (first, find them by the attribute key associated with the old commit)
    #       -- no we dont! we dont need the old chain of commits for modified attributes ... the new attribute is not applicable in any of them!
    #   .. we do however need to mark any of the attributes that were modified that they are no longer latest!
    attributes_map = {attribute.id: attribute for attribute in attributes}
    new_modified_attrs = [
        utils.modify_attr_class(
            attributes_map[attribute.attributeId],  # Get the new attribute that we are modifying ..
            {
                "onLatestProfile": True,
                "commits": [newCommit.id],
                "tenantId": newCommit.tenantId,
                "environmentId": newCommit.environmentId
            }
        )
        for attribute in newCommit.attributesModified
    ]

    # Operations to insert all the newly modified values ...
    return [
        ReplaceOne(
            {"id": new_mod_attr.id},
            attr.asdict(new_mod_attr),
            upsert=True
        )
        for new_mod_attr in new_modified_attrs
    ]


def derive_operations_to_carry_over_uneffected_attributes_from_old_commit_to_new_commit(oldCommit: ProfileCommit, newCommit: ProfileCommit):
    # For all attributes in a profile that were not added or modified in the profile
    #   ... i.e all attributes associated with old commit that were not added, removed, or modified ...
    #   ... we need to associate them with the new commit ...
    return [
        # Update Untouched Attributes to be linked to the latest profile ...
        UpdateMany(
            query_to_find_stale_attributes_from_old_commit_that_need_to_bo_associated_with_new_commit(oldCommit, newCommit),
            {
                "$push": {"commits": newCommit.id},
                "$set": {"onLatestProfile": True}
            }
        )
    ]


def derive_operations_to_save_new_attributes_and_associate_them_with_latest_commit(
        attributes: List[ProfileAttribute], newCommit: ProfileCommit) -> list:
    # For attribute we are adding ... we only need to associate them with the new commit ...
    attributes_map = {attribute.id: attribute for attribute in attributes}
    return [
        ReplaceOne(
            {"attributeId": attribute.attributeId},
            attr.asdict(
                utils.modify_attr_class(
                    attributes_map[attribute.attributeId],
                    {
                        "onLatestProfile": True,
                        "commits": [newCommit.id],
                        "tenantId": newCommit.tenantId,
                        "environmentId": newCommit.environmentId
                    }
                )
            ),
            upsert=True
        )
        for attribute in newCommit.attributesAdded
    ]


def query_to_find_stale_attributes_from_old_commit_that_need_to_bo_associated_with_new_commit(oldCommit:ProfileCommit, newCommit: ProfileCommit) -> FindQuery:
    """
    New attribute are not stale attributes ...
    Removed attributes are not stale attributes ...
    Modified attributes are not stale attributes ...

    :param oldCommit:
    :param newCommit:
    :return:
    """
    # Attribute that are going to be added as latest anyways ... thus they dont need to be carried over ...
    added_attribute_ids = [attribute.attributeId for attribute in (newCommit.attributesAdded + newCommit.attributesModified)]
    # Attributes that are being removed ... thus they dont need to be carried over ...
    modified_or_removed_attribute_keys = [attribute.attributeKey for attribute in (newCommit.attributesRemoved + newCommit.attributesModified)]
    return {
        "$and": [
            # Associated with old commit ...
            {
                "commits": oldCommit.id
            },
            # Attribute is not already associated with new commit
            {
                "commits": {
                    "$not": {
                        "$elemMatch": {
                            "$eq": newCommit.id
                        }
                    }
                }
            },
            # IDs are not part of the new attributes that will be added with old commit ...
            # Todo ... make sure that new and modified attributes dont already exist with the same id ...
            {
                "id": {
                    "$nin": added_attribute_ids
                }
            },
            # Attributes that are not being modified or removed ...
            {
                "attributeKey": {
                    "$nin": modified_or_removed_attribute_keys
                }
            }
        ]
    }


def query_to_find_attributes_associated_with_commit_by_key(commit:ProfileCommit, attributeKeys:List[str]) -> List[ProfileAttribute]:
    return {
        "commits": commit.id,
        "attributeKey": {"$in": attributeKeys}
    }


def extract_profile_commit_from_mongo_payload(query_result: dict) -> ProfileCommit:
    updated_query_result = copy.deepcopy(query_result)
    updated_query_result["attributesModified"] = list(map(
        lambda x: ProfileAttributeMapping(**x), updated_query_result.get("attributesModified", [])
    ))
    updated_query_result["attributesAdded"] = list(map(
        lambda x: ProfileAttributeMapping(**x), updated_query_result.get("attributesAdded", [])
    ))
    updated_query_result["attributesRemoved"] = list(map(
        lambda x: ProfileAttributeMapping(**x), updated_query_result.get("attributesRemoved", [])
    ))
    return ProfileCommit(**{
        f: updated_query_result.get(f) for f in utils.field_names_of_attr_class(ProfileCommit)
    })
