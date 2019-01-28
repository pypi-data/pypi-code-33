
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

import json
from typing import List, Optional

import attr
import pandas as pd
from cortex_client.profilesclient import ProfilesClient
from cortex_profiles.notebook.utils import tab_with_content, to_output, InteractableJson, map_object
from cortex_profiles.types.profiles import ProfileCommitSummary, ProfileSummary, ProfileAttributeSummary

OrderedList = List


def df_from_list_of_attr_classes(l:List, attrClass:type) -> pd.DataFrame:
    return pd.DataFrame(list(map(attr.asdict, l)), columns=list(map(lambda a: a.name, attr.fields(attrClass))))


class ProfileVisualizationClient(ProfilesClient):
    """A client for the Cortex Profiles SDK Functionality."""

    def visualizeHistoryOfAttribute(self, profileId:str, attributeKey:str):
        return tab_with_content({
            commitId: to_output(self._render_json(
                map_object(self.describeAttributeByKey(profileId, attributeKey, commitId=commitId), attr.asdict, {})
            ))
            for commitId in reversed(self.visualizeCommits(profileId)[attr.fields(ProfileCommitSummary).commitId.name])
        })

    def visualizeHistoryOfAttributesInProfile(self, profileId:str):
        return tab_with_content({
            commitId: to_output(self.visualizeAttributes(profileId, commitId=commitId))
            for commitId in reversed(self.visualizeCommits(profileId)[attr.fields(ProfileCommitSummary).commitId.name])
        })

    def visualizeProfile(self, profileId:str, commitId:Optional[str]=None):
        profile = attr.asdict(self.describeProfile(profileId, commitId))
        return self._render_json(profile if profile is not None else {})

    def visualizeProfiles(self, query:Optional[dict]=None) -> pd.DataFrame:
        return df_from_list_of_attr_classes(
            self.listProfiles(query)
        ).sort_values(by=[attr.fields(ProfileSummary).profileId.name])

    def visualizeCommits(self, profileId:str) -> pd.DataFrame:
        """
        Get Commit History ...
        :param profileId:
        :return:
        """
        return df_from_list_of_attr_classes(
            self.listCommits(profileId), ProfileCommitSummary
        ).sort_values(by=attr.fields(ProfileCommitSummary).timestamp.name, ascending=False)

    def visualizeAttributes(self, profileId:str, commitId:Optional[str]=None) -> pd.DataFrame:
        """
        Get the profile as of a certain commit
            ... defaults to latest commit if no commitId is specified ...
        :param profileId:
        :param commitId:
        :return:
        """
        return df_from_list_of_attr_classes(
            self.listAttributes(profileId, commitId), ProfileAttributeSummary
        ).sort_values(by=[attr.fields(ProfileAttributeSummary).attributeKey.name])

    def _render_json(self, j:dict):
        return InteractableJson(json.loads(json.dumps(j)))
        # return pprint(utils.json_makeup(json.loads(json.dumps(j))))
