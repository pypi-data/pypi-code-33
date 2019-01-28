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

from cortex_client import DatasetsClient, CatalogClient, ActionClient, ConnectionClient
from .connection_builder import ConnectionBuilder
from .dataset_builder import DatasetBuilder, LocalDatasetBuilder
from .skill_builder import SkillBuilder
from .action_builder import ActionBuilder
from .schema_builder import SchemaBuilder
from cortex.pipeline import Pipeline


class BuilderFactory:
    """
    Builds component builders.
    """
    def __init__(self, client):
        self.client = client

    def dataset(self, name: str, camel_version='1.0.0') -> DatasetBuilder:
        """
        Creates a DatasetBuilder with the given name.

        :Example:

        >>> builder = cortex.builder()
        >>> train_df = pd.read_csv(' <path to data as csv file>')
        >>> train_ds = builder.dataset(' <data set name> ').from_df(train_df).build()

        :param name: name of the dataset builder
        """
        ds_client = DatasetsClient(self.client._url, 3, self.client._token.token)
        return DatasetBuilder(name, ds_client, camel_version)

    def connection(self, name: str, camel_version='1.0.0') -> ConnectionBuilder:
        connection_client = ConnectionClient(self.client._url, 2, self.client._token.token)
        return ConnectionBuilder(name, connection_client, camel_version)

    def skill(self, name: str, camel_version='1.0.0') -> SkillBuilder:
        """
        Creates a SkillBuilder with the given name.

        :param name: name of the skill builer
        """
        catalog_client = CatalogClient(self.client._url, 3, self.client._token.token)
        return SkillBuilder(name, catalog_client, camel_version)

    def action(self, name: str, camel_version='1.0.0'):
        """
        Creates an ActionBuilder with the given name.

        :param name: name of the action builer
        """
        action_client = ActionClient(self.client._url, 3, self.client._token.token)
        return ActionBuilder(name, action_client, camel_version)

    def schema(self, name: str, camel_version='1.0.0'):
        """
        Creates a SchemaBuilder with the given name.

        :param name: name of the schema builer
        """
        catalog_client = CatalogClient(self.client._url, 3, self.client._token.token)
        return SchemaBuilder(name, catalog_client, camel_version)

    def pipeline(self, name: str):
        """
        Creates a pipeline with the given name.

        :param name: name of the pipeline
        """
        return Pipeline(name)


class LocalBuilderFactory:
    """
    Builds local component builders.
    """
    def dataset(self, name: str, camel_version='1.0.0') -> DatasetBuilder:
        """
        Creates a LocalDatasetBuilder with the given name.

        :Example:

        >>> builder = cortex.builder()
        >>> train_df = pd.read_csv(' <path to data as csv file>')
        >>> train_ds = builder.dataset(' <data set name> ')\
                .from_df(train_df).build()

        :param name: name of the local dataset builder
        """
        return LocalDatasetBuilder(name, camel_version)

    def pipeline(self, name: str):
        """
        Creates a local pipeline with the given name.

        :param name: name of the local dataset builder pipeline
        """
        return Pipeline(name)
