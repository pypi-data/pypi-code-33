
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

from typing import List, Optional, Tuple

import pandas as pd

from cortex_client.client import _Client
from cortex_profiles.internalprofilesclient import InternalProfilesClient
from cortex_profiles.types.api import DeleteProfileResponse
from cortex_profiles.types.profiles import ProfileCommit, Profile, ProfileAttribute, ProfileCommitSummary, \
    ProfileSummary, ProfileSnapshot, ProfileAttributeSummary
from cortex_profiles.types.schema import ProfileSchema, ProfileSchemaSummary


OrderedList = List
NoneType = type(None)


class ProfilesClient(_Client):
    """A client for the Cortex Profiles SDK Functionality."""

    def __init__(self, url:str, version:str, token:str, environmentId:str="cortex/default", internal_profiles_client:InternalProfilesClient=None):
        self.token = token
        self._internal_profiles_client = internal_profiles_client if internal_profiles_client is not None else InternalProfilesClient(url, version, token, environmentId)
        self.environmentId = environmentId
        self.tenantId = self._internal_profiles_client.tenantId

    def listCommits(self, profileId:str) -> List[ProfileCommitSummary]:
        """
        Get Commit History ...
        :param profileId:
        :return:
        """
        return [
            ProfileCommitSummary.from_profile_commit(commit)
            for commit in self._internal_profiles_client.get_commit_history_for_profile(profileId)
        ]

    def listAttributes(self, profileId:str, commitId:Optional[str]=None) -> Optional[List[ProfileAttributeSummary]]:
        """
        Get the profile as of a certain commit
            ... defaults to latest commit if no commitId is specified ...
        :param profileId:
        :param commitId:
        :return:
        """
        profile = self.describeProfile(profileId, commitId)
        attributes = profile.attributes if profile is not None else []
        return list(map(ProfileAttributeSummary.from_profile_attribute, attributes))

    def listProfiles(self, query:Optional[dict]={}) -> List[ProfileSummary]:
        return self._internal_profiles_client.list_profiles(query)

    def listSchemas(self) -> List[ProfileSchemaSummary]:
        return [
            ProfileSchemaSummary.from_profile_schema(x)
            for x in self._internal_profiles_client.list_schemas()
        ]

    def describeSchema(self, schemaId:str) -> ProfileSchema:
        return self._internal_profiles_client.get_schema(schemaId)

    def pushSchema(self, schema:ProfileSchema) -> ProfileSchema:
        return self._internal_profiles_client.upsert_profile_schema(schema)

    def describeProfile(self, profileId:str, commitId:Optional[str]=None) -> Optional[ProfileSnapshot]:
        """
        Get the profile as of a certain commit
            ... defaults to latest commit if no commitId is specified ...
        :param profileId:
        :param commitId:
        :return:
        """
        return self._internal_profiles_client.expand_profile(
            self._internal_profiles_client.get_profile(profileId, commitId)
        )

    def describeCommit(self, commitId:str):
        """
        Describe a specific commit ...
        :param commitId:
        :return:
        """
        return self._internal_profiles_client.get_commit_by_id(commitId)


    def describeAttributeById(self, attributeId:str) -> Optional[ProfileAttribute]:
        """
        Describe a specific attribute in the profile ...
        Either attributeId or attributeKey must be provided ... attributeId takes precedence over attributeKey ...
        If attribute key is provided ... the
        :param attributeId:
        :return:
        """
        return self._internal_profiles_client.get_attribute_by_id(attributeId)


    def describeAttributeByKey(self, profileId:str, attributeKey:str, commitId:Optional[str]=None) -> Optional[ProfileAttribute]:
        """
        Describe a specific attribute in the profile ...
        Either attributeId or attributeKey must be provided ... attributeId takes precedence over attributeKey ...
        If attribute key is provided ... the
        :param profileId:
        :param attributeKey:
        :param commitId:
        :return:
        """
        commit = (
            self._internal_profiles_client.get_latest_profile_commit(profileId)
            if commitId is None else self._internal_profiles_client.get_commit_by_id(commitId)
        )
        if not commit:
            return None
        return self._internal_profiles_client.get_attribute_by_key(profileId, attributeKey, commit.id)

    def deleteProfile(self, profileId:str) -> DeleteProfileResponse:
        deletion_response = self._internal_profiles_client.delete_profile(profileId)
        assert self.describeProfile(profileId) == None
        return deletion_response

    def pushAttributes(self, profileId:str, attributes:List[ProfileAttribute]) -> Tuple[str, Tuple[Profile, ProfileCommit]]:
        """
        Pushes attributes to the latest profile for the specified profileId
        :param profileId:
        :param attributes:
        :return:
        """
        return self._internal_profiles_client.append_attributes_to_profile(attributes, profileId)

    def findBottomProfilesForAttributeWithCounterValue(self, attributeKey: str, n=5):
        return pd.DataFrame([
            {
                "profileId": attribute["profileId"],
                "attributeKey": attribute["attributeKey"],
                "attributeValue": attribute["attributeValue"]["value"]
            }
            for attribute in self._internal_profiles_client.sort_counter_based_attributes(attributeKey, pick=n, ascending=True)
        ], columns=["profileId", "attributeKey", "attributeValue"])

    def findTopProfilesForAttributeWithCounterValue(self, attributeKey:str, n=5):
        return pd.DataFrame([
            {
                "profileId": attribute["profileId"],
                "attributeKey": attribute["attributeKey"],
                "attributeValue": attribute["attributeValue"]["value"]
            }
            for attribute in
            self._internal_profiles_client.sort_counter_based_attributes(attributeKey, pick=n, ascending=False)
        ], columns=["profileId", "attributeKey", "attributeValue"])

    def countsOfLatestAttributesPerProfile(self, query:Optional[dict]=None) -> pd.DataFrame:
        return pd.DataFrame(
            self._internal_profiles_client.counts_of_latest_attributes_per_profile(query),
            columns=["profileId", "profileType", "totalCountOfLatestAttributes"]
        )

    # TODO Link the commit history
    # Todo .. pull changes on profile as of latest commit ...
    #     Net attributes added ... download them and append them to the profile ..

    # def findProfilesWithAllAttributes(self, attributeKeys:List[str]):
    #     """
    #     Returns a list of profiles that have all of the attributes specified in their latest version.
    #     :param attributeKeys:
    #     :return:
    #     """
    #     pass
    #
    # def findProfilesWithSomeAttributes(self, attributeKeys:List[str]):
    #     """
    #     Returns a list of profiles that have all of the attributes specified in their latest version.
    #     :param attributeKeys:
    #     :return:
    #     """
    #     pass

    # def findProfilesWithAttributeQuery(self):


    # def findsCommitsBetweenDates

    # Todo link to find attributes ...
    # Todo ... link to ... find_latest_snapshot_for_profile
    # TODO - link to find query commits  in internal ......
    # TODO .. link to interla find profiles ...

    # def list_available_attributes_for_latest_profile(self, profileId: str) -> List[ProfileAttributeMapping]:
    #     # snapshot = find_latest_snapshot_for_profile(profileId, cortex)
    #     # if not snapshot:
    #     #     return []
    #     # return list(map(
    #     #     lambda attr: ProfileAttributeMapping(attributeKey=attr.attributeKey, attributeId=attr.id),
    #     #     snapshot.attributes
    #     # ))
    #     return [
    #         ProfileAttributeMapping(attributeKey=attribute.attributeKey, attributeId=attribute.id)
    #         for attribute in self._internal_profiles_client.find_latest_attributes_for_profile(profileId, [])
    #     ]

    # When we get history of a profile ...
    #   ... we get the latest commit for that profile and find all of the commits it was recursively involved in
    #   ... and get the commit id and time of each !
    # We can even turn this into a dataframe!


    # def merge_attributes_with_profile():
    #     """
    #     This attempts to merge two sets of profiles
    #     i.e ... two counters will get merged ...
    #     counters get merged ...
    #     latest is chosen for declared attributes ...
    #     :return:
    #     """
    #     pass


    # def net_attributes_from_commit_chain(commitChain: ProfileCommitChain) -> List[ProfileAttributeMapping]:
    #     """
    #     What are the net profile attributes after applying all of the changes
    #     in the commit chain?
    #     """
    #     snapshot = commitChain.snapshot
    #     # Start with attribute from profile snapshots ...
    #     attributes = snapshot.attributes
    #
    #     # Apply all of the additional commits on top of the snapshot ...
    #     attributes = flatmap(commitChain.additionalCommits, attributes, apply_commit_to_attributes)
    #     # Apply the latest commit
    #     attributes = apply_commit_to_attributes(attributes, )


    # def get_current_profile_attributes_for_user(profileId):
    #     pass
