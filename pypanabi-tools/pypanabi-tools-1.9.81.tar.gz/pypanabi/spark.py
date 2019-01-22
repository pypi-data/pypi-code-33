#!/usr/bin/env python

import os
import logging
from pyspark.sql import *
from pyspark.sql.functions import *
from .aws import S3


class Spark(object):
    def __init__(self,
                 spark_url='local',
                 appName='PanameraApp',
                 cassandra_host='cassandra',
                 cassandra_port='9042',
                 path=None,
                 is_remote=False,
                 bucket=None,
                 profile=None):
        """
        Constructor
        :param spark_url: sets the Spark master URL to connect to, such as 'local' to run locally, or 'spark://master:7077' to run on a Spark standalone cluster
        :param appName = spark application name
        :param cassandra_host = cassandra host [String]
        :param cassandra_port = cassandra port [String]
        :param path: absolute local path of the file or S3 prefix of the file [String]
        :param is_remote: indicates if the path informed is local or remote (s3 file) [Boolean]
        :param bucket: bucket name [String]
        :param profile: S3 profile [String]
        """
        self._logger = logging.getLogger(__name__)
        self._spark_url = spark_url
        self._appName = appName
        self._dataframe = None
        self._original_dataframe = None
        self._tmp_dir = '/tmp'
        self._tmp_file = None
        self._bucket = None
        self._session = None
        self._file_path = path
        self._file_type = None
        self._file_name = None
        self._file_format = None
        self._full_file_path = None
        try:
            if path:
                self._file_name = '.'.join((self._file_path.split(os.sep)[-1]).split('.')[:-1])
                self._file_format = path.split('.')[-1].lower()
                if is_remote:
                    self._logger.debug('File provided is stored in S3 -> Filename: {}'.format(self._file_name))
                    self._file_source = 's3'
                    self._bucket = bucket

                    if not bucket:
                        raise Exception('S3 bucket must be informed for remote files')

                    if not profile:
                        profile = 'reservoir'

                    # S3 Client
                    self._s3_client = S3(bucket=bucket, profile=profile)
                    self._logger.debug('Created S3 client -> Bucket: {}, Profile: {}'.format(bucket, profile))

                    if not self._s3_client.exists(self._file_path):
                        raise Exception('File {} does not exist in S3 bucket {}'.format(self._file_path, self._bucket))

                    # Cleaning temporal file if exists
                    tmp_file = os.path.join(self._tmp_dir, self._file_name + '.' + self._file_format)
                    if os.path.exists(tmp_file):
                        os.remove(tmp_file)

                else:
                    self._logger.debug('File provided is stored in local file system -> Filename: {}'.format(self._file_name))
                    self._file_source = 'file'
                    self._bucket = ''

                self._full_file_path = self._file_source + '://' + os.path.join(self._bucket, self._file_path)

                # Spark session
                self._session = SparkSession.builder \
                                            .config("spark.cassandra.connection.host", cassandra_host) \
                                            .config("spark.cassandra.connection.port", cassandra_port) \
                                            .master(self._spark_url) \
                                            .appName(self._appName) \
                                            .enableHiveSupport() \
                                            .getOrCreate()
                self._logger.debug('Spark session created -> AppName: {}, SparkUrl: {}'.format(self._appName, self._spark_url))

        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def set_file(self, path, is_remote=False, bucket=None, profile=None):
        """
        Set file path (remote or local file)
        :param path: absolute local path of the file or S3 prefix of the file [String]
        :param is_remote: indicates if the path informed is local or remote (s3 file) [Boolean]
        :param bucket: bucket name [String]
        :param profile: S3 profile [String]
        :return: None
        """
        try:
            self._file_path = path
            self._file_name = '.'.join((self._file_path.split(os.sep)[-1]).split('.')[:-1])
            self._file_format = path.split('.')[-1].lower()
            if is_remote:
                self._logger.debug('File provided is stored in S3 -> Filename: {}'.format(self._file_name))
                self._file_source = 's3'
                self._bucket = bucket

                if not bucket:
                    raise Exception('S3 bucket must be informed for remote files')

                if not profile:
                    profile = 'reservoir'

                # S3 Client
                self._s3_client = S3(bucket=bucket, profile=profile)

                if not self._s3_client.exists(self._file_path):
                    raise Exception('File {} does not exist in S3 bucket {}'.format(self._file_path, self._bucket))

                # Cleaning temporal file if exists
                tmp_file = os.path.join(self._tmp_dir, self._file_name + '.' + self._file_format)
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
            else:
                self._logger.debug('File provided is stored in local file system -> Filename: {}'.format(self._file_name))
                self._file_source = 'file'
                self._bucket = ''

            self._full_file_path = self._file_source + '://' + os.path.join(self._bucket, self._file_path)

            # Spark session
            if not self._session:
                self._session = SparkSession.builder \
                    .master(self._spark_url) \
                    .appName(self._appName) \
                    .enableHiveSupport() \
                    .getOrCreate()
            self._logger.debug('Spark session created -> AppName: {}, SparkUrl: {}'.format(self._appName, self._spark_url))
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def read(self):
        """
        Read file local or remote
        :return: dataframe with data loaded from file [Dataframe]
        """
        try:
            if not self._full_file_path:
                raise Exception('No file informed. Use set_file method for this purpose and run it again')

            if self._file_source == 's3':
                local_path = self._s3_client.download(prefix=self._file_path, local_path=self._tmp_dir)[0]
                self._tmp_file = os.path.join(self._tmp_dir, self._file_name + '.' + self._file_format)
            else:
                local_path = self._full_file_path

            # Reading file
            self._dataframe = self._session.read.load(local_path, format=self._file_format)
            self._original_dataframe = self._dataframe

            return self._dataframe
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def get_dataframe(self):
        """
        Get dataframe
        :return: data [Dataframe]
        """
        return self._dataframe

    def get_original_dataframe(self):
        """
        Get original dataframe
        :return: data [Dataframe]
        """
        return self._original_dataframe

    def get_columns(self):
        """
        Get dataframe columns
        :return: list with all columns [List]
        """
        if self._dataframe:
            return self._dataframe.columns

    def remove(self, columns):
        """
        Remove columns from dataframe
        :param columns: list of columns [List<String>]
        :return: None
        """
        try:
            for col in columns:
                self._dataframe = self._dataframe.drop(col)

            return self._dataframe
        except Exception as ex:
            self._logger.warning(repr(ex))
            raise

    def rename(self, columns):
        """
        Rename columns
        :param columns: dictionary with old name as key and new name as value [Dictionary]
        :return: None
        """
        try:
            for k, v in columns.items():
                self._dataframe = self._dataframe.withColumnRenamed(k, v)

            return self._dataframe
        except Exception as ex:
            self._logger.warning(repr(ex))
            raise

    # TODO: add implementation of 'sum' aggregation
    def sum(self, sum_column, aggregation_column_name='total'):
        """
        Aggregate current dataframe
        :param sum_column: in case that the operation be 'sum', this represents the column to be summarized [String]
        :param aggregation_column_name: new name for the column result of the aggregation [String]
        :return: data aggregated [Dataframe]
        """
        try:
            columns = [x for x in self.get_columns() if x != sum_column]
            #self._dataframe = self._dataframe.groupBy(columns).sum(sum_column).withColumnRenamed('sum({})'.format(sum_column), aggregation_column_name)
            return self._dataframe
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def count(self, aggregation_column_name='count'):
        """
        Aggregate current dataframe
        :param aggregation_column_name: new name for the column result of the aggregation [String]
        :return: data aggregated [Dataframe]
        """
        try:
            self._dataframe = self._dataframe.groupBy(self.get_columns()).count().withColumnRenamed('count', aggregation_column_name)
            return self._dataframe
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def concatenate(self, columns, concatenation_column_name='concat', remove_concatenated_columns=False):
        """
        Concatenate columns
        :param columns: list of columns [List<String>]
        :param concatenation_column_name: Name of the new column [String]
        :param remove_concatenated_columns: flag indicating if the columns concatenated must be removed or not [Boolean]
        :return: new set of data with the new column added [Dataframe]
        """
        try:
            self._dataframe = self._dataframe.withColumn(concatenation_column_name, concat(*columns))
            if remove_concatenated_columns:
                self._dataframe = self.remove(columns)

            return self._dataframe
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def order(self, columns):
        """
        Define specific order for the columns
        :param columns: list of columns in the desired order [List<String>]
        :return: date with columns in the desired order [Dataframe]
        """
        try:
            self._dataframe = self._dataframe.select(columns)
            return self._dataframe
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def add(self, column_name, value):
        """
        Add a new column to the dataframe with harcoded value
        :param column_name: column name [String]
        :param value: value [String]
        :return:
        """
        try:
            self._dataframe = self._dataframe.withColumn(column_name, lit(str(value)))
            return self._dataframe
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def filter(self, filters):
        """
        Filter dataframe
        :param filters: list of dictionaries with column, value and operator (dictionary keys: column, value, operator. [List<Dictionary>]
        :return:
        """
        try:
            for filter in filters:
                condition = "{column} {operator} '{value}'".format(**filter)
                self._dataframe = self._dataframe.filter("{}".format(condition))

            return self._dataframe
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def get_partition_value(self, partition):
        """
        Get value for an specified partition
        :param partition: partition name [String]
        :return: value for partition or None if partition does not exist
        """
        value = None
        if self._file_path:
            for pair in (x for x in self._file_path.split(os.sep) if '=' in x):
                val = pair.split('=')
                if val[0] == partition:
                    value = val[1]
                    break
        return value

    def reset(self):
        """
        Reset dataframe to the original
        :return: original dataframe [Dataframe]
        """
        self._dataframe = self._original_dataframe
        return self._dataframe

    def get_temporal_file(self):
        """
        Get full local path where temporal file is stored
        :return:
        """
        return self._tmp_file

    def save_to_cassandra(self, keyspace, table, mode='overwrite', dataframe=None):
        """
        Save dataframe to Cassandra
        :param host: hostname of cassandra [String]
        :param keyspace: keyspace name [String]
        :param table: table name in Cassandra [String]
        :param mode: writing mode append, overwrite, ignore, error [String]
        :param dataframe: dataframe which contains data to be sent to Cassandra [Dataframe]
        :return: None
        """
        try:
            if not dataframe:
                dataframe = self._dataframe

            if dataframe:
                dataframe.write \
                         .format("org.apache.spark.sql.cassandra") \
                         .mode(mode) \
                         .options(keyspace=keyspace, table=table) \
                         .save()
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def __repr__(self):
        return str({'AppName': self._appName, 'MasterURL': self._spark_url, 'File Path': self._full_file_path})
