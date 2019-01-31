
import logging
import os
import six

from dli.client.exceptions import (
    CatalogueEntityNotFoundException,
    MissingMandatoryArgumentException,
)
from dli.siren import siren_to_entity, siren_to_dict
from dli.client.utils import ensure_count_is_valid

logger = logging.getLogger(__name__)


class DatasetFunctions(object):

    @property
    def __root(self):
        return self.ctx.memoized(
            self.get_root_siren().datasets_root,
            "datasets_root"
        )

    def get_s3_access_keys_for_dataset(self, *dataset_ids):
        """
        Retrieve S3 access keys for the specified account to access the
        specified dataset(s).

        :param list dataset_ids: One ore more dataset ids to get access to.
        :returns: A namedtuple containing the AWS keys and session token.
        :rtype: collections.namedtuple
        
        - **Sample**

        .. code-block:: python

                s3_access_keys = client.get_s3_access_keys_for_dataset(dataset_id1, dataset_id2)
                # print(s3_access_keys)
                # access_key(access_key_id='39D19A440AFE452B9', secret_access_key='F426A93CDECE45C9BFF8F4F19DA5CB81', session_token='C0CC405803F244CA99999')

        """
        if not dataset_ids:
            raise MissingMandatoryArgumentException('dataset_ids')

        # validate that all datasets exist
        for dataset_id in dataset_ids:
            self._get_dataset(dataset_id=dataset_id)

        payload = {"datasetIds": list(dataset_ids)}
        response = self.get_root_siren().request_access_keys(__json=payload)
        keys = siren_to_entity(response)
        return keys

    def get_dataset(self, id=None, name=None, package_id=None, package_name=None):
        """
        Retrieves a dataset.

        :param str id: The id of the dataset.
        :param str name: The name of the dataset.
        :param str package_id: The id of the package to which this dataset belongs. 
                            Either this or package name is required if dataset is being looked up by name.
        :param str package_name: The name of the package to which this dataset belongs.
                            Either this or package id is required if dataset is being looked up by name.

        :returns: The dataset.
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                # Look up by dataset id
                dataset = client.get_dataset('my_dataset_id')
                # or equivalent
                dataset = client.get_dataset(id='my_dataset_id')

                # Look up by dataset name 

                # If package id is known
                dataset = client.get_dataset(name='my_dataset', package_id='my_package_id')

                # if package name is known
                dataset = client.get_dataset(name='my_dataset', package_name='my_package')
        """

        if id is not None:
            return siren_to_entity(self._get_dataset(dataset_id=id))

        if name is not None:
            return siren_to_entity(self._get_dataset(name=name, package_id=package_id, package_name=package_name))

        raise ValueError("Either dataset id or name (along with package id or package name) must be specified to look up dataset")

    def _get_dataset(self, **kwargs):

        dataset = self.__root.get_dataset(**kwargs)

        if not dataset:
            raise CatalogueEntityNotFoundException('Dataset', params=kwargs)

        return dataset   

    def register_dataset(self, builder):
        """
        Submit a request to create a new dataset under a specified package in the Data Catalogue.

        :param dli.client.builders.DatasetBuilder builder: An instance of DatasetBuilder. This builder object sets sensible defaults and exposes
                                                           helper methods on how to configure its storage options.

        :returns: A newly created Dataset.
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                # Please refer to builder docs for examples on
                # how to creata an instance of DatasetBuilder.

                dataset = client.register_dataset(builder)
        """
        payload = builder.build()

        result = self.__root.create_dataset(__json=payload)
        return siren_to_entity(result)

    def edit_dataset(
        self,
        dataset_id,
        name=None,
        description=None,
        content_type=None,
        data_format=None,
        publishing_frequency=None,
        keywords=None,
        naming_convention=None,
        documentation=None,
        location_builder=None,
        taxonomy=None,
        load_type=None
    ):
        """
        Updates information on a dataset, returning the updated instance.
        Fields that are left as ``None`` will not be changed.

        :param str dataset_id: Id of the dataset being updated.
        :param str name: A descriptive name of a dataset. It should be unique within the package.
        :param str description: A short description of a package.
        :param str content_type: A way for the data steward to classify the type of data in the dataset (e.g. pricing).
        :param str data_format: The format of the data: csv, parquet, etc.
        :param str publishing_frequency: The internal on which data is published (e.g. daily, monthly, etc.).
        :param list[str] keywords: User-defined list of keywords that can be used to find this dataset through the search interface.
        :param str naming_convention: Key for how to read the dataset name.
        :param str documentation: Documentation about this dataset in markdown format.
        :param dli.client.builders.DatasetLocationBuilder location_builder: An instance of DatasetLocationBuilder. This builder object exposes
                                                                            helper methods to configure dataset storage options.
        :param list[str] taxonomy: A list of segments to be used for a taxonomy, the Data-<< Organization >>-<< topic >> prefix will be applied by the catalogue
                                   For a taxonomy of Data-IHS Markit-Financial Markets-Credit-CDS, you would provide `taxonomy=["Credit", "CDS"]`
        :param str loadType: Optional. Whether each datafile in this dataset should be considered as a full version of a dataset
                                or a delta or increment. Accepted types are `Full Load` and `Incremental Load`
        :returns: Updated Dataset.
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                # e.g. update dataset description
                updated_dataset = client.edit_dataset(
                    "my-dataset-id",
                    description="Updated my dataset description"
                )

                # update dataset location. Please note that this is only allowed if the dataset has no datafiles registered.
                builder = DatasetLocationBuilder().with_external_storage("external-storage-location")
                updated_dataset = client.edit_dataset(
                    "my-dataset-id",
                    location_builder=builder
                )

                # update dataset taxonomy
                updated_dataset = client.edit_dataset(
                    "my-dataset-id",
                    taxonomy=["Credit", "CDS"]
                )

        """
        if not dataset_id:
            raise MissingMandatoryArgumentException('dataset_id')

        dataset = self._get_dataset(dataset_id=dataset_id)

        fields = {
            "packageId": dataset.packageId,
            "name": name,
            "description": description,
            "keywords": keywords,
            "contentType": content_type,
            "location": dataset.location,
            "dataFormat": {"type": data_format} if data_format else None,
            "publishingFrequency": publishing_frequency,
            "namingConvention": naming_convention,
            "documentation": documentation,
            "taxonomy": taxonomy,
            "loadType": load_type
        }

        if location_builder:
            fields.update(location_builder.build())

        # clean up any unknown fields, and update the entity
        dataset_as_dict = siren_to_dict(dataset)
        for key in list(dataset_as_dict.keys()):
            if key not in fields:
                del dataset_as_dict[key]

        payload = {k: v for k, v in fields.items() if v is not None}
        dataset_as_dict.update(payload)

        # perform the update and return the resulting entity
        return siren_to_entity(dataset.edit_dataset(__json=dataset_as_dict))

    def delete_dataset(self, dataset_id):
        """
        Marks a particular dataset (and all its datafiles) as deleted.
        This dataset will no longer be accessible by consumers.

        :param str dataset_id: The id of the dataset to be deleted.

        :returns:

        - **Sample**

        .. code-block:: python

                client.delete_dataset(dataset_id)

        """
        if not dataset_id:
            raise MissingMandatoryArgumentException('dataset_id')

        dataset = self._get_dataset(dataset_id=dataset_id)

        dataset.delete_dataset()

    def get_datafiles(self, dataset_id, name_contains=None, as_of_date_start=None, as_of_date_end=None, count=100):
        """
        Returns a list of all datafiles registered under a dataset.

        :param str dataset_id: The id of the dataset.
        :param str name_contains: Optional. Look up only those datafiles for the dataset where name contains this string.
        :param str as_of_date_start: Optional. Datafiles having data_as_of date greater than or equal to this date. This must be specified in YYYY-MM-DD format.
        :param str as_of_date_end: Optional. Datafiles having data_as_of date less than or equal to this date. This must be specified in YYYY-MM-DD format.
        :param int count: Optional count of datafiles to be returned. Defaulted to 100.

        :returns: List of all datafiles registered under the dataset.
        :rtype: list[collections.namedtuple]

        - **Sample**

        .. code-block:: python

                datafiles = client.get_datafiles(
                    dataset_id,
                    name_contains='My Test Data',
                    as_of_date_start='2018-10-11',
                    as_of_date_end='2018-10-15',                    
                    count=10
                )
        """
        if not dataset_id:
            raise MissingMandatoryArgumentException('dataset_id')

        ensure_count_is_valid(count)

        params = {
            'name': name_contains,
            'as_of_date_start': as_of_date_start,
            'as_of_date_end': as_of_date_end,
            'page_size': count
        }

        query_params = {k: v for k, v in six.iteritems(params) if v is not None}

        dataset = self._get_dataset(dataset_id=dataset_id)
            
        datafiles = dataset.get_datafiles(**query_params).get_entities(rel="datafile")

        return [siren_to_entity(df) for df in datafiles]

    def _register_schema(self, dataset_id, payload):
        if not dataset_id:
            raise MissingMandatoryArgumentException('dataset_id')

        dataset = self._get_dataset(dataset_id=dataset_id)

        payload = {k: v for k, v in payload.items() if v is not None}
        return siren_to_entity(dataset.create_schema(__json=payload))

    def register_schema(
        self,
        dataset_id,
        version,
        valid_as_of,
        fields,
        type='StructType',
        partitions=None,
        description=None
    ):
        """
        Registers schema metadata for a dataset.

        :param str dataset_id: Mandatory. Id of the dataset for the schema.
        :param str version: Mandatory. A user assigned version name/number. It should be unique within the dataset.
        :param str valid_as_of: Mandatory. The date as of which the schema is active.
                               Expected format is YYYY-MM-DD, e.g. 2018-05-28
        :param list[dict] fields: Mandatory. Non empty list of `Field` as described below.
        :param str type: Type of the schema. Defaults to `StructType`.
        :param list[dict] partitions: Optional. Non empty list of `Partition` as described below.
        :param str description: Optional. Description for the schema.

        .. code-block:: python

                # Field: Spark compatible
                {
                    "name": "field_a", 			# name of the column.
                    "type": "String", 			# string representation of the type of the column (might be another StructType if it is a nested type).
                    "nullable": True,  			# defaulted to True - A boolean indicating whether the field is nullable or not.
                    "metadata": None			# optional dictionary with metadata for this column.
                }

                # Partition:
                {
                    "name": "key1",
                    "type": "String"
                }    

        :returns: The registered schema.
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                my_schema_fields = [
                            {
                                'name': 'field_1',
                                'type': 'String',
                                'nullable': False
                            },
                            {
                                'name': 'field_2',
                                'type': 'Double',
                                'nullable': False
                            },
                            {
                                'name': 'field_3',
                                'type': 'Int',
                                'nullable': True,
                                'metadata': {
                                    'some_key': 'some_value'
                                }
                            },
                        ]
                my_schema_partitions = [
                    {
                        'name': 'field_1',
                        'type': 'String'
                    }
                ]

                my_schema = client.register_schema(
                    "my-dataset-id",
                    version='1a',
                    valid_as_of='2018-10-31',
                    fields=my_schema_fields,
                    type='my-schema-type',
                    partitions=my_schema_partitions,
                    description="My schema description"
                )
        """

        payload = {
            'version': version,
            'validAsOf': valid_as_of,
            'type': type,
            'fields': fields,
            'partitions': partitions,
            'description': description,
        }

        return self._register_schema(dataset_id, payload)

    def register_spark_schema(
        self,
        dataset_id,
        version,
        valid_as_of,
        spark_schema_json,
        partitions=None,
        description=None
    ):
        """
        Registers dataframe schema for the datalake `dataset` for instances where data ingest pipelines make use of spark.

        :param str dataset_id: Mandatory. Id of the dataset for the schema.
        :param str version: Mandatory. A user assigned version name/number. It should be unique within the dataset.
        :param str valid_as_of: Mandatory. The date as of which the schema is active.
                               Expected format is YYYY-MM-DD, e.g. 2018-05-28
        :param dict spark_schema_json: Mandatory. Json schema for the spark dataframe.
        :param list[dict] partitions: Optional. Non empty list of `Partition` as described below.
        :param str description: Optional. Description for the schema.

        .. code-block:: python

                # Partition:
                {
                    "name": "key1",
                    "type": "String"
                }    

        :returns: The registered schema.
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                # my_spark_dataframe: some spark dataframe with data being published in the data lake

                my_spark_schema_json = my_spark_dataframe.schema.jsonValue()

                my_schema = client.register_spark_schema(
                    "my-dataset-id",
                    version='1a',
                    valid_as_of='2018-10-31',
                    spark_schema_json=my_spark_schema_json,
                    description="My schema description"
                )
        """

        payload = {
            'version': version,
            'validAsOf': valid_as_of,
            'partitions': partitions,
            'description': description,
        }
        payload.update(spark_schema_json)

        return self._register_schema(dataset_id, payload)

    def get_schema(self, dataset_id, version=None):
        """
        Looks up schema for a dataset by version. In case version is not specified this will fetch schema version having the latest valid_as_of date.
        Throws exception if no schema is registered for the dataset.

        :param str dataset_id: The id of the dataset under which the schema is registered.
        :param str version: Optional. The version of the schema.

        :returns: The schema.
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                # Fetch schema version '1a'
                schema = client.get_schema('my_dataset_id', version='1a')

                # Fetch the schema with the latest valid_as_of date
                latest_schema = client.get_schema('my_dataset_id')

        """

        if not dataset_id:
            raise MissingMandatoryArgumentException('dataset_id')

        dataset = self._get_dataset(dataset_id=dataset_id)

        schema_siren = dataset.get_schema(version=version) if version else dataset.get_schema()

        if schema_siren:
            return siren_to_entity(schema_siren)
        
        raise CatalogueEntityNotFoundException('Schema', {'dataset_id': dataset_id, 'version': version})

    def get_schemas(self, dataset_id, count=100):
        """
        Returns a list of all schemas registered under the dataset. The list is sorted by schema valid_as_of date in descending order.

        :param str dataset_id: The id of the dataset.
        :param int count: Optional count of schemas to be returned. Defaulted to 100.

        :returns: List of all schemas registered under the dataset sorted by valid_as_of date in descending order.
        :rtype: list[collections.namedtuple]

        - **Sample**

        .. code-block:: python

                my_schemas = client.get_schemas("my_dataset_id", count=10)
        """

        if not dataset_id:
            raise MissingMandatoryArgumentException('dataset_id')
        
        ensure_count_is_valid(count)

        dataset = self._get_dataset(dataset_id=dataset_id)

        schemas = dataset.get_schemas(page_size=count).get_entities(rel="schema")

        return [siren_to_entity(s) for s in schemas]

    def delete_schema(self, dataset_id, version):
        """
        Marks a schema version for a dataset as deleted. 

        :param str dataset_id: The id of the dataset under which the schema is registered.
        :param str version: The version of the schema.

        :returns:

        - **Sample**

        .. code-block:: python

                # Delete schema version '1a'
                client.delete_schema(dataset_id='my_dataset_id', version='1a')

        """

        if not dataset_id:
            raise MissingMandatoryArgumentException('dataset_id')
        if not version:
            raise MissingMandatoryArgumentException('version')

        dataset = self._get_dataset(dataset_id=dataset_id)

        schema = dataset.get_schema(version=version)

        if schema:
            return schema.delete_schema(dataset_id=dataset_id, version=version)
            
        raise CatalogueEntityNotFoundException('Schema', {'dataset_id': dataset_id, 'version': version})

    def edit_schema(
        self,
        dataset_id,
        version,
        new_version=None,
        valid_as_of=None,
        fields=None,
        type=None,
        partitions=None,
        description=None
    ):
        """
        Updates schema metadata for a dataset.
        If a field is passed as ``None`` then the field will not be updated.

        :param str dataset_id: Mandatory. Id of the dataset for the schema.
        :param str version: Mandatory. Version of the schema being updated.
        :param str new_version: New version if to be updated. This is a user assigned version name/number. It should be unique within the dataset.
        :param str valid_as_of: The date as of which the schema is active.
                               Expected format is YYYY-MM-DD, e.g. 2018-05-28
        :param list[dict] fields: If provided, a non empty list of `Field` as described below.
        :param str type: Type of the schema.
        :param list[dict] partitions: If provided, a non empty list of `Partition` as described below.
        :param str description: Description for the schema.

        .. code-block:: python

                # Field: Spark compatible
                {
                    "name": "field_a", 			# name of the column.
                    "type": "String", 			# string representation of the type of the column (might be another StructType if it is a nested type).
                    "nullable": True,  			# defaulted to True - A boolean indicating whether the field is nullable or not.
                    "metadata": None			# optional dictionary with metadata for this column.
                }

                # Partition:
                {
                    "name": "key1",
                    "type": "String"
                }    

        :returns: The updated schema.
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                # Updating description and valid_as_of date for my schema
                my_updated_schema = client.edit_schema(
                    "my-dataset-id",
                    '1a',
                    valid_as_of='2018-11-05',
                    description="My updated schema description"
                )
        """
        if not dataset_id:
            raise MissingMandatoryArgumentException('dataset_id')
        if not version:
            raise MissingMandatoryArgumentException('version')

        dataset = self._get_dataset(dataset_id=dataset_id)

        schema = dataset.get_schema(version=version)

        if schema:
            schema_as_dict = siren_to_dict(schema)
            payload = {
                'version': new_version,
                'validAsOf': valid_as_of,
                'type': type,
                'fields': fields,
                'partitions': partitions,
                'description': description,
            }

            for key in list(schema_as_dict.keys()):
                if key not in payload:
                    del schema_as_dict[key]

            schema_as_dict.update({k: v for k, v in payload.items() if v is not None})

            result = schema.edit_schema(__json=schema_as_dict)
            return siren_to_entity(result)

        raise CatalogueEntityNotFoundException('Schema', {'dataset_id': dataset_id, 'version': version})
