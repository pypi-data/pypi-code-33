
"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import base64
from typing import List, Optional, Tuple, Callable, Any

import attr
import pydash
import pymongo
from cortex_client.authenticationclient import AuthenticationClient
from cortex_client.client import _Client
from cortex_client.secretsclient import SecretsClient
from cortex_profiles import utils, queries, profile_commit_utils
from cortex_profiles.profile_commit_utils import apply_commits_onto_profile, profile_commit_chain_from_recursive_commit
from cortex_profiles.profile_commit_utils import determine_attribute_modification_deltas_relevant_to_profile
from cortex_profiles.schemas import schemas
from cortex_profiles.schemas.schemas import UNIVERSAL_ATTRIBUTES
from cortex_profiles.types.attributes import ProfileAttribute
from cortex_profiles.types.attributes import load_profile_attribute_from_dict
from cortex_profiles.types.general import AggregateQuery, OrderedList
from cortex_profiles.types.internal import LatestCommitPointer
from cortex_profiles.types.profiles import ProfileCommit, Profile, ProfileSnapshot, ProfileSummary
from cortex_profiles.utils import group_objects_by


class InternalProfilesClient(_Client):
    """A client for the Cortex Profiles SDK Functionality."""

    def __init__(self, url:str, version:str, token:str, environmentId:str="cortex/default", mongodb_factory:Optional[Callable[[], Any]]=None):
        self.token = token
        self.authclient = AuthenticationClient(url, "2", token)
        self.secretsclient = SecretsClient(url, "2", token)
        self.tenantId = self.authclient.fetch_current_user_details()["tenant"]
        self.environmentId = environmentId

        # databases here ...
        secret = self.secretsclient.get_secret(base64.b64decode(b'ZnBp').decode("utf-8"))
        if not secret:
            raise Exception("Failed to get secret.")

        self.mongodb = mongodb_factory() if mongodb_factory else pymongo.MongoClient(secret["mongo_uri"])["cortex-graph"]

        self.latest_commit_pointers_collection = self.mongodb["commit-pointers"]
        self.commits_collection = self.mongodb["commits"]
        self.snapshots_collection = self.mongodb["snapshots"]
        self.attributes_collection = self.mongodb["attributes"]

    def index_databases(self):
        from pymongo import IndexModel, ASCENDING, DESCENDING

        index_id = IndexModel([("id", ASCENDING), ("createdAt", DESCENDING)], name="id_with_time")
        index_profile = IndexModel([("profileId", ASCENDING)], name="profileId_asc")
        index_environ = IndexModel([("environmentId", ASCENDING)], name="environment_parition")
        index_tenant = IndexModel([("tenantId", ASCENDING)], name="tenant_partition")

        self.latest_commit_pointers_collection.create_indexes([index_id, index_profile, index_environ, index_tenant])
        self.snapshots_collection.create_indexes([index_id, index_profile, index_environ, index_tenant])
        self.attributes_collection.create_indexes([index_id, index_profile, index_environ, index_tenant])

        index_attr_key = IndexModel([("attributeKey", ASCENDING)], name="attrkey_asc")
        self.commits_collection.create_indexes([index_id, index_profile, index_environ, index_tenant, index_attr_key])

    def flush_databases(self):
        self.latest_commit_pointers_collection.drop()
        self.commits_collection.drop()
        self.snapshots_collection.drop()
        self.attributes_collection.drop()
        # self.profiles_collection.drop()
        # self.locks_collection.drop()

    def flush_collection(self, collection):
        return collection.delete_many(self.append_secure_variables_to_query({}))

    def flush_profiles(self):
        self.flush_collection(self.latest_commit_pointers_collection)
        self.flush_collection(self.commits_collection)
        self.flush_collection(self.snapshots_collection)
        self.flush_collection(self.attributes_collection)
        # self.flush_collection(self.profiles_collection)
        # self.flush_collection(self.locks_collection)

    @utils.timeit
    def append_attributes_to_profile(self, attributes: List[ProfileAttribute], profileId: str) -> Tuple[
        Profile, ProfileCommit]:
        """
        This overrides attributes on a profile ...
        i.e one counter will override the other ..
        """
        # when an attribute is saved ... save it with the commit that it was created in?
        #     when a new commit happens,
        #         update all the attributes associated with the old commit to be associated with the new commit ...
        #     Get all of the attributes if specified ... else ... get the list specified ...

        # Get latest Commit ... or Create a new one if it doesnt exist ...
        default_commit = self.default_commit_for_user(profileId)
        # helpers.print_json_with_header("Default Commit: ", helpers.attr.asdict(default_commit))

        latest_commit = self.find_latest_commit_for_profile_or_create(profileId, default_commit)
        # helpers.print_json_with_header("Latest Commit: ", helpers.attr.asdict(latest_commit))

        # Get Profile from latest commit
        latest_profile = self.get_profile_based_off_commitId(latest_commit.id)
        # helpers.print_json_with_header("Latest Profile: ", helpers.attr.asdict(latest_profile))

        # Create New Commit Based of Latest Commit ...
        # Figure out which attributes are new ... modified ... removed ...
        attributes_added, attributes_modified, attributes_removed = determine_attribute_modification_deltas_relevant_to_profile(
            attributes, latest_profile)
        # helpers.print_attr_class_with_header("attributes_added: ", attributes_added)
        # helpers.print_attr_class_with_header("attributes_modified: ", attributes_modified)
        # helpers.print_attr_class_with_header("attributes_removed: ", attributes_removed)

        # Derive new commit from latest commit + attribute modifications
        new_commit = profile_commit_utils.extend_commit_with_attributes(latest_commit, attributes_added,
                                                                        attributes_modified, attributes_removed)
        # helpers.print_attr_class_with_header("new_commit: ", new_commit)

        # Save newest commit
        saved_commit = self.save_profile_commit(new_commit)
        # helpers.print_attr_class_with_header("saved_commit: ", saved_commit)

        # Save the new attributes ... & save the new modified attributes & update old modified attributes to deactivate ...
        saved_attributes = self.save_attributes(attributes, latest_commit, new_commit)
        # helpers.pprint_with_header("saved_attributes: ", saved_attributes)

        # Update the pointer to the latest commit ... from the old commit to the new one ..
        latest_commit_pointer = self.update_latest_commit_pointer(latest_commit, new_commit)
        # helpers.print_attr_class_with_header("latest_commit_pointer: ", latest_commit_pointer)

        # Rebuild the latest profile from the latest commits ...
        latest_profile = self.get_latest_profile(profileId)
        # helpers.print_attr_class_with_header("latest_profile: ", latest_profile)

        # Expand the profile and save it as a snapshot to be queried ...
        expanded_profile = self.expand_profile(latest_profile)
        expanded_profile = self.replace_latest_snapshot_for_profile(expanded_profile)
        # helpers.print_attr_class_with_header("expanded_profile: ", expanded_profile)

        return latest_profile, saved_commit

    def get_profile(self, profileId:str, commitId:Optional[str]=None) -> Optional[Profile]:
        return (
            self.get_latest_profile(profileId)
           if not commitId else self.get_profile_based_off_commitId(commitId)
        )

    def get_commit_history_for_profile(self, profileId:str) -> OrderedList[ProfileCommit]:
        return list(map(
            lambda x: ProfileCommit(**x),
            self.commits_collection.find(
                self.append_secure_variables_to_query({"profileId": profileId}),
                {"_id": 0}
            ).sort([("createdAt", -1)])
        ))

    def get_commit_by_id(self, commitId:str) -> Optional[ProfileCommit]:
        commit = utils.drop_from_dict(self.commits_collection.find_one(
            self.append_secure_variables_to_query({"id": commitId})
        ), ["_id"])
        return ProfileCommit(**commit) if commit else None

    def get_attribute_by_id(self, attributeId:str) -> dict:
        commit = utils.drop_from_dict(self.attributes_collection.find_one(
            self.append_secure_variables_to_query({"id": attributeId})
        ), ["_id"])
        return commit if commit else {}

    def get_attribute_by_key(self, profileId:str, attributekey:str, commitId:str) -> dict:
        commit = utils.drop_from_dict(self.attributes_collection.find_one(
            self.append_secure_variables_to_query({
                "profileId": profileId,
                "attributeKey": attributekey,
                "commits": commitId
            })
        ), ["_id"])
        return commit if commit else {}

    def get_latest_attributes_for_profile(self, profileId: str, attributesKeys: List[str]) -> List[ProfileAttribute]:
        # snapshot = find_latest_snapshot_for_profile(profileId, cortex)
        # attributes = snapshot.attributes if snapshot else []
        # Todo ... inefficient ... we get the whole profile ... them manually filter what we dont want ...
        # Can we get only what we want?
        # At the same time ... we only want to query amoungst the latest attributes ... (should we get latest commitid first?)
        # return attributes if not attributesKeys else list(filter(
        #     lambda attr: attr.attributeKey in attributesKeys,
        #     attributes
        # ))
        return self.find_latest_attributes_for_profile(profileId, attributesKeys)

    def get_latest_profile_commit(self, profileId:str) -> Optional[ProfileCommit]:
        """
        Getting the latest commit is like getting any other commit ...
        Where as searching ... is done on the most up to date attributes ...

        :param profileId:
        :return:
        """
        # TODO Add branches ...
        latest_commit = utils.drop_from_dict(
                self.latest_commit_pointers_collection.find_one(
                    self.append_secure_variables_to_query({
                        "profileId": profileId
                    })
                    # Dont need to sort because only 1 pointer should exist per profile
                ),
                ["_id"]
            )

        latest_commit_pointer = LatestCommitPointer(**latest_commit) if latest_commit else None
        if not latest_commit_pointer:
            return None
        return self.get_commit_by_id(latest_commit_pointer.commitId)


    def get_latest_profile(self, profileId:str) -> Optional[Profile]:
        """
        Gets the latest profile for the specified profile id.
        :param profileId:
        :return:
        """
        commit = self.get_latest_profile_commit(profileId)
        # helpers.print_attr_class_with_header("Latest profile commit: ", commit)
        if not commit:
            return None
        return self.get_profile_based_off_commitId(commit.id)


    def get_profile_based_off_commitId(self, commitId:str) -> Profile:
        """
        Builds the latest profile starting at the specified commit, recursively.
        :param commitId:
        :return:
        """
        commits = self.find_commits_recursively_starting_from(commitId)
        # Build profile from recursive commits ...
        return self.build_profile_from_commits(commits, commitId)

    def expand_profile(self, profile:Profile) -> Optional[ProfileSnapshot]:
        if profile is not None:
            return ProfileSnapshot(**utils.merge_dicts(
                attr.asdict(profile),
                {
                    "attributes": self.get_attributes_associated_with_profile(profile),
                    "context": attr.fields(ProfileSnapshot).context.default
                }
            ))
        else:
            return None

    def sort_counter_based_attributes(self, attributeKey:str, pick:int=5, ascending=True) -> List[dict]:
        return list(map(
            lambda x: utils.drop_from_dict(x, ["_id"]),
            self.attributes_collection.find(
                self.append_secure_variables_to_query({
                    "onLatestProfile": True,
                    "attributeKey": attributeKey,
                })
            ).sort([("attributeValue.value", -1 if not ascending else 1)]).limit(pick)
        ))


    def build_profile_from_commits(self, commits:OrderedList[ProfileCommit], commitId:str) -> Optional[Profile]:
        if not commits:
            return None
        # helpers.print_attr_class_with_header("Applying commits", commits)
        return apply_commits_onto_profile(
            commits,
            self.default_profile_for_user(commits[0].profileId, commitId)
        )

    def dervive_latest_commit_pointer_from_commit(self, commit:ProfileCommit) -> LatestCommitPointer:
        return LatestCommitPointer(
            id=utils.unique_id(),
            commitId=commit.id,
            profileId=commit.profileId,
            environmentId=self.environmentId,
            tenantId=self.tenantId,
            createdAt=utils.utc_timestamp()
        )

    def default_profile_for_user(self, profileId: str, commitId:str) -> Profile:
        return Profile(
            id=profileId,
            commitId=commitId,
            createdAt=utils.utc_timestamp(),
            tenantId=self.tenantId,
            environmentId=self.environmentId
        )

    def default_commit_for_user(self, profileId: str) -> ProfileCommit:
        return ProfileCommit(
            id=utils.unique_id(),
            createdAt=utils.utc_timestamp(),
            profileId=profileId,
            tenantId=self.tenantId,
            environmentId=self.environmentId
        )

    def find_profiles(self, query: dict) -> List[ProfileSnapshot]:
        # Limit Scope of Query ...
        restricted_query = queries.append_leaf_queries_with(
            query,
            self.append_secure_variables_to_query({})
       )
        # helpers.print_json_with_header("Query to run", restricted_query)
        # Find snapshots ...
        return list(map(
            lambda x: ProfileSnapshot.from_dict(utils.drop_from_dict(x, ["_id"])),
            self.snapshots_collection.find(
                restricted_query
            )
        ))

    def query_latest_attributes(self, query: dict, query_options: dict) -> object:
        return self.attributes_collection.find(
            queries.append_leaf_queries_with(query, self.append_secure_variables_to_query({})),
            **query_options
        )

    def find_latest_attributes_for_profile(self, profileId: str, attributeKeys: Optional[str]) -> List[ProfileAttribute]:
        query = self.append_secure_variables_to_query({
            "onLatestProfile": True,
            "profileId": profileId
        })
        if attributeKeys:
            query["attributeKey"] = {
                "$in": attributeKeys
            }
        return list(map(
            lambda x: load_profile_attribute_from_dict(utils.drop_from_dict(x, ["_id"])),
            self.attributes_collection.find(query)
        ))

    def find_latest_commit_for_profile_or_create(self, profileId:str, default_commit:ProfileCommit) -> ProfileCommit :
        """
        Finds the latest commit on a specific profile id ... or creates a default one if no commit is found for the profile id ...
        :param profileId:
        :param default_commit:
        :param cortex:
        :return:
        """

        # First ... find the latest pointer or create it ...
        pointer = LatestCommitPointer(
            **utils.drop_from_dict(
                queries.find_or_create_atomically(
                    self.latest_commit_pointers_collection,
                    self.append_secure_variables_to_query({
                        "profileId": profileId
                    }),
                    attr.asdict(self.dervive_latest_commit_pointer_from_commit(default_commit)),
                    {
                        "sort": [('createdAt', pymongo.DESCENDING)],
                        "upsert": True,
                        "return_document": pymongo.ReturnDocument.AFTER
                    }
                ),
                ["_id"]
            )
        )

        commit = queries.find_or_create_atomically(
            self.commits_collection,
            self.append_secure_variables_to_query({
                "id": pointer.commitId,
                "profileId": pointer.profileId
            }),
            attr.asdict(default_commit),
            {
                "sort": [('createdAt', pymongo.DESCENDING)],
                "upsert": True,
                "return_document": pymongo.ReturnDocument.AFTER
            }
        )
        return ProfileCommit(**utils.drop_from_dict(commit, ["_id"]))

    def save_profile_commit(self, commit: ProfileCommit) -> ProfileCommit:
        safe_commit = utils.modify_attr_class(commit, self.append_secure_variables_to_query({}))
        saved_commit = self.commits_collection.find_one_and_replace(
            {"id": safe_commit.id},
            attr.asdict(safe_commit),
            **{
                "upsert": True,
                "return_document": pymongo.ReturnDocument.AFTER
            }
        )
        return ProfileCommit(**utils.drop_from_dict(saved_commit, ["_id"]))

    def find_commits_recursively_starting_from(self, commitId:str) -> List[ProfileCommit]:
        query_results = list(self.commits_collection.aggregate(self.build_query_commits_recursively(commitId)))
        recursive_commit  = utils.drop_from_dict(query_results[0], ["_id"]) if query_results else []
        # helpers.print_json_with_header("Recursive commit starting at {}".format(commitId), recursive_commit)
        # Derive a list of all the commits in cronological order ...
        return profile_commit_chain_from_recursive_commit(recursive_commit)

    def build_query_commits_recursively(self, commitId:str) -> AggregateQuery:
        return [
            {
                "$match": self.append_secure_variables_to_query({
                  "id": commitId,
                })
            },
            # Find all of the commits that this commit is chained to ...
            {
                "$graphLookup" : {
                    "from": self.commits_collection.name,
                    "startWith": '$extends',
                    "connectFromField": 'extends',
                    "connectToField": 'id',
                    "as": 'recursive_commits',
                    "restrictSearchWithMatch": self.append_secure_variables_to_query({})
                }
            }
        ]

    def replace_latest_snapshot_for_profile(self, snapshot:ProfileSnapshot) -> ProfileSnapshot:
        return utils.drop_from_dict(
            self.snapshots_collection.find_one_and_replace(
                self.append_secure_variables_to_query({
                    "id": snapshot.id
                }),
                attr.asdict(snapshot),
                **{
                    "upsert": True,
                    "return_document": pymongo.ReturnDocument.AFTER
                }
            ), ["_id"]
        )

    def get_attributes_associated_with_profile(self, profile: Profile) -> List[ProfileAttribute]:
        data_for_raw_attributes = list(self.attributes_collection.find(
            self.append_secure_variables_to_query({
                "id": {"$in": [attribute.attributeId for attribute in profile.attributes]}
            })
        ))
        # print(data_for_raw_attributes) -> These are fine, theyre all Nones ...
        attributes = list(map(
            lambda x: load_profile_attribute_from_dict(utils.drop_from_dict(x, ["_id"])),
            data_for_raw_attributes
        ))
        # print(attributes)
        return attributes

    def update_latest_commit_pointer(self, fromCommit:ProfileCommit, toCommit:ProfileCommit) -> LatestCommitPointer:
        pointer = self.dervive_latest_commit_pointer_from_commit(toCommit)
        saved_pointer = self.latest_commit_pointers_collection.find_one_and_replace(
            self.append_secure_variables_to_query({
                "commitId": fromCommit.id,
                "profileId": fromCommit.profileId
            }),
            attr.asdict(pointer),
            **{
                "upsert": True,
                "return_document": pymongo.ReturnDocument.AFTER
            }
        )
        return utils.drop_from_dict(saved_pointer, ["_id"])

    def save_attributes(self, attributes: List[ProfileAttribute], oldCommit: ProfileCommit, newCommit: ProfileCommit) -> object:
        """
        Save new attributes ...
        Replace Modified attributes ...
        """
        operations = (
                queries.derive_operations_to_carry_over_uneffected_attributes_from_old_commit_to_new_commit(oldCommit, newCommit) +
                queries.derive_operations_to_save_new_attributes_and_associate_them_with_latest_commit(attributes, newCommit) +
                queries.derive_operations_to_save_modified_attributes_and_associate_them_with_latest_commit(attributes, newCommit) +
                queries.derive_operations_to_unmark_changed_attributes_as_latest(oldCommit, newCommit)
        )
        return utils.drop_from_dict(self.attributes_collection.bulk_write(operations).bulk_api_result, ["_id"])

    def counts_of_latest_attributes_per_profile(self, query:Optional[dict]=None) -> List[dict]:
        query = utils.merge_dicts({} if not query else query, {"onLatestProfile": True})
        return list(map(
            lambda x: utils.merge_dicts(x["_id"], {"totalCountOfLatestAttributes": x["count"]}),
            self.attributes_collection.aggregate(
                [
                    {
                        "$match": self.append_secure_variables_to_query(query)
                    },
                    {
                        "$group": {
                            "_id": {"profileId": "$profileId", "profileType": "$profileType"},
                            "count": {
                                "$sum": 1
                            }
                        }
                    }
                ]
            )
        ))

    # def list_profiles(self, query:Optional[dict]=None) -> List[ProfileSummary]:
    #     """
    #     This doesnt do too well if we decommission attributes ...
    #     :param query:
    #     :return:
    #     """
    #     return list(map(
    #         lambda x: ProfileSummary(**(x["_id"])),
    #         self.attributes_collection.aggregate(
    #             [
    #                 {
    #                     "$match": self.append_secure_variables_to_query({} if not query else query)
    #                 },
    #                 {
    #                     "$group": {
    #                         "_id": {"profileId": "$profileId", "profileType": "$profileType"},
    #                     }
    #                 }
    #             ]
    #         )
    #     ))


    def list_profiles(self, profileType:Optional[str]=None) -> List[ProfileSummary]:
        """
        This doesnt do too well if we decommission attributes ...
        :param query:
        :return:
        """
        profileAttrFields = attr.fields(ProfileAttribute)

        initial_query = {} if profileType is None else {
            profileAttrFields.attributeValue.name: {"elemMatch": profileType}}
        initial_query[profileAttrFields.attributeKey.name] = UNIVERSAL_ATTRIBUTES.TYPES


        type_attributes = list(self.attributes_collection.find(
            self.append_secure_variables_to_query(initial_query)
        ))
        types_for_profiles = {
            k: v[0] for k, v in group_objects_by(type_attributes, lambda x: x["profileId"]).items()
        }

        if profileType is None:
            # Return all profiles ... whether they have a type or not ...
            profiles = self.snapshots_collection.find(self.append_secure_variables_to_query({}))
        else:
            # Return only profiles of that types ...
            profiles = self.snapshots_collection.find(self.append_secure_variables_to_query({
                profileAttrFields.profileId.name: {"$in": list(types_for_profiles.keys())}
            }
            ))

        # TODO .. append typeless profiles ...
        return list(map(
            lambda profileSnapshot: ProfileSummary(
                profileTypes=types_for_profiles.get(profileSnapshot["id"], {}).get("attributeValue", {"value":[]})["value"],
                profileId=profileSnapshot["id"],
                attributes=len(profileSnapshot["attributes"])
        ),
            profiles
        ))


    def find_attributes(self, attributeIds: List[str]) -> List[ProfileAttribute]:
        return list(map(
            lambda x: ProfileAttribute(**utils.drop_from_dict(x, ["_id"])),
            self.attributes_collection.find(
                self.append_secure_variables_to_query({
                    "id": {"$in": attributeIds}
                })
            )
        ))

    def find_latest_snapshot_for_profile(self, profileId: str) -> ProfileSnapshot:
        query = self.append_secure_variables_to_query({"id": profileId})
        # helpers.print_json_with_header("Query to run ... ", query)
        snapshot = pydash.rename(utils.drop_from_dict(self.snapshots_collection.find_one(query), ["_id"]), {"id": "profileId"})
        return ProfileSnapshot.from_dict(snapshot) if snapshot else None

    def append_secure_variables_to_query(self, query:dict) -> dict:
        return utils.merge_dicts(query, {
            "environmentId": self.environmentId,
            "tenantId": self.tenantId,
        })