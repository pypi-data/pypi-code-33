from tmg_etl_library.components.databases.database import Database
from tmg_etl_library.components.config import BQTableConfig

from google.api_core.exceptions import NotFound
from google.cloud.bigquery.table import TimePartitioning, TimePartitioningType
from google.cloud.bigquery.job import ExtractJobConfig, CopyJobConfig, QueryJobConfig, QueryJob
from google.cloud import bigquery
from google.cloud import storage

from jsonschema import validate, ValidationError

import re
import os
import datetime as dt
import time
import csv


class BQClient(Database):
    def __init__(self, log, project):
        super().__init__(log)
        self.client = bigquery.Client(project=project)

    def table_exists(self, table):
        """
        Checks to see if a big query table exists
        :param table: BQTable object to find in project
        :return: True/False
        """

        google_table_ref = self.get_table_ref(table)

        try:
            self.client.get_table(google_table_ref)
            return True
        except NotFound:
            return False

    def list_tables(self, project, dataset, table_regex=''):
        '''
        :param project: String Project
        :param dataset: String Dataset
        :param table_regex: Option Regex to Filter the Tables Returned
        :return: List of BQTable Objects
        '''

        google_bq_dataset = self._get_dataset(project, dataset)
        google_bq_table_items = self.client.list_tables(google_bq_dataset)

        table_names = [table.table_id for table in google_bq_table_items]

        if table_regex:
            table_names = [table_name for table_name in table_names if re.match(table_regex, table_name)]

        bqTables = [BQTable(project=project, dataset=dataset, name=table) for table in table_names]

        return bqTables

    def delete_tables(self, tables):
        """
        :param tables: BQTable or List of BQTables to Delete
        :return: Nothing
        """

        if isinstance(tables, BQTable):
            google_bq_table = self.get_table_ref(tables)
            self.logger.info('Deleting Table: %s' % str(tables))
            self.client.delete_table(google_bq_table)

        elif isinstance(tables, list):
            for table in tables:
                google_bq_table = self.get_table_ref(table)
                self.logger.info('Deleting Table: %s' % str(table))
                self.client.delete_table(google_bq_table)

        else:
            raise TypeError()

    def create_gbq_schema(self, BQTable_schema):
        """
        :param BQTable_schema:
        :return: [SchemaField]
        """
        return [bigquery.SchemaField(name=column['name'], field_type=column['type'], mode=column.get('mode', 'NULLABLE'))
                for column in BQTable_schema]

    def create_table(self, table, config=None):
        """
        Creates a new empty table in BQ.
        :param table: BQTable
        :param config: BQTableConfig
        :return: BQTable
        """

        if not config:
            config = BQTableConfig()

        if not table.schema:
            raise Exception('No schema is defined.')

        dataset = self._get_dataset(table.project, table.dataset, force_dataset_creation=config.force_dataset_creation)
        if not dataset:
            raise Exception('Dataset {0} not found'.format(table.dataset))

        table_ref = dataset.table(table.name)

        try:
            self.client.get_table(table_ref)
            self.logger.info('Table {0} already exists.'.format(table.name))
            return table
        except NotFound:
            if not config.force_table_creation:
                raise Exception('Table {0} does not exist and force_table_creation is not set to True.'.format(table.name))
            self.logger.info('Table {0} does not exists.'.format(table.name))

        self.logger.info('Creating table {0}'.format(table.name))
        schema = self.create_gbq_schema(table.schema)
        gbq_table = bigquery.Table(table_ref, schema=schema)

        if table.expiry:
            expiry_datetime = dt.datetime.now() + dt.timedelta(minutes=table.expiry)
            gbq_table.expires = expiry_datetime

        if table.partitioned_field:
            gbq_table.time_partitioning = TimePartitioning(type_=TimePartitioningType.DAY, field=table.partitioned_field)

        google_bq_table = self.client.create_table(gbq_table)
        self.logger.info('Table {0} is created.'.format(table.name))

        return BQTable.GBQ_to_BQTable(google_bq_table)

    def insert_csv(self, CSVFile, BQTable, config):
        """
        Inserts a file into the table passed to the function using the configs passed to the function.
        :param BQTable: Object which decribes a BQ table
        :param push_config: configurations of the job to insert a file into a table
        :param tmp_file: the file containing the data to be inserted
        :return:
        """

        table_exists = self.table_exists(BQTable)
        if config.create_disposition == 'CREATE_NEVER' and not table_exists:
            raise RuntimeError('Table does not exist and config set to not create table')

        elif config.create_disposition == 'CREATE_IF_NEEDED' and not table_exists:
            self.create_table(BQTable)

        google_bq_table = self.get_table_ref(BQTable)

        with open(CSVFile.full_path, 'rb') as csv_file_obj:
            job_config = bigquery.LoadJobConfig()

            job_config.field_delimiter = CSVFile.delimiter
            job_config.write_disposition = config.write_disposition
            job_config.allow_quoted_newlines = config.allow_quoted_newlines
            job_config.skip_leading_rows = config.skip_leading_rows if config.skip_leading_rows else 0
            job_config.max_bad_records = config.max_bad_records
            job_config.allow_jagged_rows = config.allow_jagged_rows
            job_config.quote_character = CSVFile.quote_char
            job_config.ignore_unknown_values = config.ignore_unknown_values
            job = self.client.load_table_from_file(
                csv_file_obj, google_bq_table, job_config=job_config)  # API request
            job.result()

    def query_to_file(self, query, CSVFile, config):
        job_config = QueryJobConfig()
        job_config.use_legacy_sql = config.use_legacy_sql
        self.logger.info('Running Query')
        query_df = self.client.query(query, job_config=job_config).to_dataframe()
        self.logger.info('Pushing Query results to CSV at location: %s' % CSVFile.full_path)

        if hasattr(CSVFile, 'quotechar'):
            query_df.to_csv(CSVFile.full_path, index=False, sep=CSVFile.delimiter,
                        quotechar=CSVFile.quotechar,
                        header=config.print_header)
        else:
            query_df.to_csv(CSVFile.full_path, index=False, sep=CSVFile.delimiter, header=config.print_header)

    def run_query(self, query=None, query_file_name=None, destination=None, write_disposition=None, use_legacy_sql=False, async_query=False, query_params={}):
        """
        :param query: String Query to be Performed
        :param destination: BQTable, where the results of the query should be written to
        :param write_disposition: If the table exists, WRITE_TRUNCATE or WRITE_APPEND, Default: WRITE_EMPTY
        :param use_legacy_sql: Defaults to False - uses Standard SQL
        :return:
        """
        if not (query or query_file_name):
            raise Exception("query or query_file_name should be provided.")

        if query_file_name:
            with open(query_file_name, mode="r") as query_file:
                query = query_file.read()

        query = query.format(**query_params)

        job_config = bigquery.QueryJobConfig()
        job_config.use_legacy_sql = use_legacy_sql

        if destination:
            self.logger.info('Query Destination: %s' % str(destination))
            job_config.time_partitioning = TimePartitioning(type_=TimePartitioningType.DAY, field=destination.partitioned_field)
            google_bq_table = self.get_table_ref(destination)
            job_config.destination = google_bq_table

        if write_disposition:
            job_config.write_disposition = write_disposition

        self.logger.info('Running Query')
        query_job = self.client.query(query, job_config=job_config)  # API request - starts the query asynchronously

        if async_query:
            return query_job

        while True:
            query_job.reload()  # Refreshes the state via a GET request.
            if query_job.state == 'DONE':
                if query_job.error_result:
                    raise RuntimeError(query_job.errors)
                break
            time.sleep(1)

        iterator = query_job.result()

        return iterator

    def wait_for_queries(self, query_jobs):
        """
        :param QueryJobs: List of QueryJob type
        :return:
        """
        if not isinstance(query_jobs, list):
            raise TypeError('queries must be of type list')
        else:
            for query_job in query_jobs:
                if not isinstance(query_job, QueryJob):
                    raise TypeError('Values in list must be of type QueryJob')

        for query_job in query_jobs:
            while True:
                query_job.reload()  # Refreshes the state via a GET request.
                if query_job.state == 'DONE':
                    if query_job.error_result:
                        raise RuntimeError(query_job.errors)
                    self.logger.info('Query Job with id "%s" has completed' % query_job.job_id)
                    break
                time.sleep(1)

        return True

    def get_table_ref(self, table):
        """
        Retrieves table reference
        :param table: BQTable object
        :return:
        """

        dataset = self._get_dataset(table.project, table.dataset)
        if not dataset:
            return None
        return dataset.table(table_id=table.name)

    def _get_dataset(self, project, dataset_id, location='EU', force_dataset_creation=False):
        """
        Create or get the dataset in GC
        :param project: project name
        :param dataset_name: dataset name
        :param location: dataset location name: EU or US
        :param force_dataset_creation: If True creates a dataset if doesn't exists
        :return: dataset
        """

        dataset_ref = bigquery.DatasetReference(dataset_id=dataset_id, project=project)
        try:
            dataset = self.client.get_dataset(dataset_ref=dataset_ref)
            self.logger.info('Dataset {0} is reached.'.format(dataset_id))
            return dataset
        except NotFound:
            if force_dataset_creation:
                dataset = bigquery.Dataset(dataset_ref=dataset_ref)
                dataset.location = location
                self.client.create_dataset(dataset)
                self.logger.info('Dataset {0} is created.'.format(dataset_id))
                return dataset
            else:
                return None

    def update_schema(self, table):
        '''
        :param table: BQTable object
        '''

        self.logger.info('Updating Schema for Table %s' % str(table))
        google_bq_current_table_ref = self.get_table_ref(table)
        google_bq_current_table = self.client.get_table(google_bq_current_table_ref)
        current_field_names = [field.name for field in google_bq_current_table.schema]

        new_schema_field_names = [field['name'] for field in table.schema]
        columns_removed = [field_name for field_name in current_field_names if field_name not in new_schema_field_names]

        if columns_removed:
            raise Exception('New Schema does not have columns which exist in current table - Please Include')

        updated_schema = [bigquery.SchemaField(name=column['name'], field_type=column['type'], mode=column.get('mode', 'NULLABLE'))
                          for column in table.schema]

        google_bq_current_table.schema = updated_schema

        self.client.update_table(google_bq_current_table, ['schema'])

    def copy_tables(self, source=None, target=None, config=None, copy_list=[]):
        """
        :param source: BQTable
        :param target: BQTable
        :param copy_list: List of Dictionaries of [{"source": BQTable, "target": BQTable"}, ...]
        :return:
        """
        if not copy_list:
            copy_list.append({'source': source, 'target': target})

        copy_job_config = CopyJobConfig()
        if config:
            copy_job_config.write_disposition = config.write_disposition

        for copy in copy_list:
            target_BQTable = copy['target']
            if target_BQTable.expiry or target_BQTable.partitioned_field:
                self.create_table(copy['target'], config)
            self.logger.info('Copying table %s to %s' % (str(copy['source']), str(copy['target'])))
            google_bq_table_source = self.get_table_ref(copy['source'])
            google_bq_table_target = self.get_table_ref(copy['target'])
            self.client.copy_table(google_bq_table_source, google_bq_table_target, job_config=copy_job_config)


    def merge_csv_files(self, input_file_names, output_file_name, files_have_headers=False):
        #TODO: Potentially move to file object instead
        """
        Merge multiple csv files into single CSV file.

        :param input_file_names: list of csv files
        :param output_file_name: output file
        :return:
        """

        self.logger.info('Merging CSVs on local to file %s' % output_file_name)
        with open(output_file_name, 'wt') as outfile:
            # writing the first csv file
            with open(input_file_names[0], 'rt', encoding="ISO-8859-1") as infile_obj:
                infile = infile_obj.read()
                for line in infile:
                    outfile.write(line)

            # writing other csv files
            for input_file_name in input_file_names[1:]:
                with open(input_file_name, 'rt', encoding="ISO-8859-1") as infile:
                    if files_have_headers:
                        next(infile)  # skip the header
                    for line in infile:
                        outfile.write(line)

        outfile.close()


    def export_table_to_storage(self, BQTable, CSVFile, extract_config=None):
        """
        Exporting the BQ table into the Google Storage, if the table is large, it will exported into multiple files.

        :param project: Project
        :param dataset_id: Dataset name
        :param table_id:  table name
        :param bucket_name: Bucket name
        :param filename: destination file name in the bucket
        """

        job_config = ExtractJobConfig()
        job_config.print_header = extract_config.print_header
        job_config.field_delimiter = CSVFile.delimiter

        destination_uri = 'gs://{}/{}'.format(extract_config.gs_bucket, extract_config.gs_filename)
        table_ref = self.get_table_ref(BQTable)

        self.logger.info('exporting {project}:{dataset}.{table} to {destination}'.format(
            project=BQTable.project,
            dataset=BQTable.dataset,
            table=BQTable.name,
            destination=destination_uri
        ))

        extract_job = self.client.extract_table(
            source=table_ref,
            destination_uris=[destination_uri],
            job_config=job_config
        )
        # API request
        extract_job.result()

    def get_file_names_from_storage_with_pattern(self, project, bucket_name, pattern, prefix=None):
        #TODO: Potentially move to storage object, replace parameters with Storage object
        """
        Get a list of files from google storage matching pattern.

        :param project: google cloud project
        :param bucket_name: bucket name
        :param pattern: the regex pattern of the filename to search in the storage.
        :param prefix: the prefix of the file names (optional)
        :return: list of file names.
        """

        #TODO: Cleanup
        if prefix:
            prefix = prefix[:-1] if prefix[-1] == '*' else prefix

        client = storage.Client(project=project)
        bucket = client.get_bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)
        re_pattern = re.compile(pattern)
        file_names = list(filter(lambda blob: re_pattern.match(blob.name), blobs))
        return file_names

    def download_from_storage(self, project, bucket_name, src_filename, dest_filename=None, dest_folder=None):
        #TODO: Potentially move to storage object
        """
        Download a file from google bucket

        :param project: google cloud project
        :param bucket_name: bucket name
        :param src_filename: name of the source file in google cloud storage
        :param dest_filename: destination dest_filename (optional)
        :param dest_folder: destination folder (optional)
        :return: True if no exception occurs otherwise False
        """
        dest_filename = dest_filename if dest_filename else os.path.basename(src_filename)

        if dest_folder:
            dest_filename = "{0}/{1}".format(
                dest_folder,
                os.path.basename(dest_filename)
            )

        client = storage.Client(project=project)
        bucket = client.get_bucket(bucket_name)

        blob = bucket.blob(src_filename)

        self.logger.info("Downloading {src_filename} from bucket gs://{bucket}".format(
            src_filename=os.path.basename(src_filename),
            bucket=bucket_name,
        ))

        try:
            blob.download_to_filename(dest_filename)
            return dest_filename
        except NotFound:
            self.logger.info('File: %s not found', src_filename)
            return False

    def delete_from_storage(self, project, bucket_name, filename):
        #TODO: potentially move to storage object
        """
        Delete a file from storage

        :param project: Project name
        :param bucket_name: Bucket name
        :param src_filename: file in the bucket
        :return:
        """

        client = storage.Client(project=project)
        bucket = client.get_bucket(bucket_name)

        blob = bucket.blob(filename.name)

        blob.delete(client)

        self.logger.info("Deleting {filename} from bucket gs://{bucket}".format(
            filename=filename,
            bucket=bucket_name,
        ))

    def full_table_to_file(self, BQTable, CSVFile, config):

        # export table into the multiple files in the storage
        # if the size of the table is big, it will be exported into multiple files

        if not config.gs_bucket:
            config.gs_bucket = '{project}-tmp-files'.format(project=BQTable.project)
        if not config.gs_filename:
            config.gs_filename = '{table}_*'.format(table=BQTable.name)

        self.export_table_to_storage(
            BQTable=BQTable,
            CSVFile=CSVFile,
            extract_config=config
        )

        # find the files in storage
        table_files = self.get_file_names_from_storage_with_pattern(
            project=BQTable.project,
            bucket_name=config.gs_bucket,
            pattern='',
            prefix=config.gs_filename
        )

        # download files from storage
        downloaded_files = []
        for table_file in table_files:
            downloaded_file = self.download_from_storage(
                project=BQTable.project,
                bucket_name=config.gs_bucket,
                src_filename=table_file.name,
                dest_filename=os.path.basename(table_file.name),
                dest_folder=CSVFile.path
            )
            downloaded_files.append(downloaded_file)

        if not config.storage_retention:
            # delete files from storage
            for table_file in table_files:
                self.delete_from_storage(
                    project=BQTable.project,
                    bucket_name=config.gs_bucket,
                    filename=table_file
                )

        # concatenate the files into single csv file.
        self.merge_csv_files(
            downloaded_files,
            CSVFile.full_path,
            files_have_headers=config.print_header
        )


class BQTable:
    def __init__(self, project, dataset, name):
        """
        Class that contains all the information needed to represent a BQ table

        :param project: BQ project name
        :param dataset: BQ dataset name
        :param name: BQ table name
        :param schema: BQ schema (Dictionary)
        """
        self.project = project
        self.dataset = dataset
        self.name = name
        self._schema = None
        self._expiry = None
        self._partitioned_field = None

    def __repr__(self):
        return '%s.%s.%s' % (self.project, self.dataset, self.name)

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, value):
        valid_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "mode": {"type": "string"},
                    "type": {"type": "string"}
                },
                'required': ["name", "type"],
                "additionalProperties": False,
                'max_items': 3
            }
        }

        try:
            validate(value, valid_schema)
            self._schema = value
        except ValidationError as e:
            raise('Schema given is not in the correct format. Please check documentation.')

    @property
    def expiry(self):
        return self._expiry

    @expiry.setter
    def expiry(self, value):
        """
        :param value: Time in Minutes for when the table should expire (delete itself)
        :return: Nothing
        """
        if not isinstance(value, int):
            raise TypeError('expiry must be an Integer')

        self._expiry = value

    @property
    def partitioned_field(self):
        return self._partitioned_field

    @partitioned_field.setter
    def partitioned_field(self, value):
        """
        :param value: Field (String) to set as the field to partition the table on
        :return: Nothing
        """
        if not isinstance(value, str):
            raise TypeError('Partitioned Field must be a String')

        self._partitioned_field = value


    @classmethod
    def GBQ_to_BQTable(cls, google_bq_table):
        return cls(project=google_bq_table.project,
                   dataset=google_bq_table.dataset_id,
                   name=google_bq_table.table_id)


class BQTableConfig:
    #TODO: move to config classes
    '''
    Could split these configs into the Table and Job configs
    expiry and partition field added to the Table, they are parameters of the table
    and the force creations could go into the jobs
    That would help with the current issue of passing this config alongside the job
    '''
    def __init__(self):
        self.force_table_creation = True
        self.force_dataset_creation = True
        self.dataset_location = 'EU'

    @property
    def force_table_creation(self):
        return self._force_table_creation

    @force_table_creation.setter
    def force_table_creation(self, value):
        if not isinstance(value, bool):
            raise TypeError('force_table_creation must be set to a Boolean Value')
        self._force_table_creation = value

    @property
    def force_dataset_creation(self):
        return self._force_dataset_creation

    @force_dataset_creation.setter
    def force_dataset_creation(self, value):
        if not isinstance(value, bool):
            raise TypeError('force_dataset_creation must be set to a Boolean Value')
        self._force_dataset_creation = value