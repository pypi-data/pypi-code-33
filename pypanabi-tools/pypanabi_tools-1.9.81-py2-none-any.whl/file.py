#!/usr/bin/env python

import os
import json
from csv import reader
import gzip
import logging
import fileinput
import configparser
from pandas import DataFrame
from StringIO import StringIO
from fastparquet import write
from pandas.io.json import json_normalize


class ConfigFile(object):
    def __init__(self):
        """
        Constructor
        """
        self._logger = logging.getLogger(__name__)
        self._config_parser = configparser.ConfigParser()
        self._sections = None

    def load(self, file_path, with_sections=True):
        """
        Load Configuration file
        :param file_path: Path to config file [String]
        :param with_sections: Indicates if the file to load contains sections [Boolean]
        :return: None
        """
        try:
            if with_sections:
                self._config_parser.read(file_path)
            else:
                with open(file_path) as stream:
                    stream = StringIO("[root]\n" + stream.read())
                    self._config_parser.readfp(stream)
            self._sections = self._config_parser.sections()
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def sections(self):
        """
        Get all sections found in the file
        :return: Sections [List<String>]
        """
        return self._sections

    def get(self, section, attribute=None):
        """
        Get an specific section
        :param section: Section name [String]
        :param attribute: Attribute name or pattern[String]
        :return: Value or set of values [Dictionary]
        """
        try:
            items = dict()
            if section in self.sections():
                for attr, value in self._config_parser.items(section):
                    if attribute:
                        if attribute in attr:
                            items[attr] = value
                    else:
                        items[attr] = value

            return items
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def remove(self, section):
        """
        Remove section from file
        :param section: Section name [String]
        :return: None
        """
        try:
            if self.sections():
                if section in self.sections():
                    self._config_parser.remove_section(section)
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def add(self, section):
        """
        Add section to file
        :param section: Section name [String]
        :return: None
        """
        try:
            self._config_parser.add_section(section)
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def set(self, section, param, value):
        """
        Set tuples param=value in a section given
        :param section: Section name [String]
        :param param: Parameter name [String]
        :param value: Value [String]
        :return: None
        """
        try:
            self._config_parser.set(section, param, value)
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def write_config(self, file_path, mode='wb'):
        """
        Write configuration to file
        :param file_path: Path to config file [String]
        :param mode: read/write mode. Default: wb
        :return: None
        """
        try:
            with open(file_path, mode) as f:
                self._config_parser.write(f, space_around_delimiters=False)
        except Exception as ex:
            self._logger.error(repr(ex))
            raise


class CSVFile(object):
    def __init__(self, file_path, delimiter=','):
        """
        Constructor
        :param file_path: Path to json file [String]
        """
        self._logger = logging.getLogger(__name__)
        self._file_path = file_path
        self._file_path_compressed = None
        self._delimiter = delimiter
        self._dir_path = os.path.dirname(self._file_path)
        self._filename = os.path.basename(self._file_path)
        self._data = []

    def load(self):
        """
        Load CSV from file
        :return: None
        """
        try:
            self._data = list()
            with open(self._file_path, 'r') as csvfile:
                spamreader = reader(csvfile, delimiter=self._delimiter)
                for line in spamreader:
                    self._data.append(line)
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def read(self):
        """
        Read file and load in memory line by line
        :return: Iterator line by line
        """
        try:
            with open(self._file_path, 'r') as csvfile:
                spamreader = reader(csvfile, delimiter=self._delimiter)
                for line in spamreader:
                    yield line
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def data(self):
        """
        Get data loaded
        :return: List with data loaded [List<String>]
        """
        return self._data

    def count(self):
        """
        Count of records loaded from CSV file
        :return: Number of records [Long]
        """
        return len(self._data)

    def compress(self, destination=None):
        """
        Compress CSV file
        :param destination: Destination file path. Default: same name with suffix '.gz' [String]
        :return: Full path of new file created [String]
        """
        try:
            if not destination:
                destination = self._file_path + '.gz'

            with gzip.open(destination, 'wb') as gzipfile:
                for line in self.read():
                    gzipfile.write(self._delimiter.join(line) + '\n')
            self._file_path_compressed = destination

            return self._file_path_compressed
        except Exception as ex:
            self._logger.error(repr(ex))
            raise


class JSONFile(object):
    def __init__(self, file_path, json_lines=False):
        """
        Constructor
        :param file_path: Path to json file [String]
        :param json_lines: Flag to indicate if the file contains multiples jsons, separated by \n
        """
        self._logger = logging.getLogger(__name__)
        self._json_lines = json_lines
        self._file_path = file_path
        self._file_path_compressed = None
        self._dir_path = os.path.dirname(self._file_path)
        self._filename = os.path.basename(self._file_path)
        self._data = []

    def _set_file_path(self, file_path):
        self._file_path = file_path
        self._dir_path = os.path.dirname(self._file_path)
        self._filename = os.path.basename(self._file_path)

    def load(self):
        """
        Load JSON from file
        :return: None
        """
        try:
            with open(self._file_path, 'r') as f:
                if self._json_lines:
                    for line in f:
                        self._data.append(json.loads(line))
                else:
                    try:
                        self._data = json.load(f)
                    except Exception as ex:
                        for line in f:
                            self._data.append(json.loads(line))
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def read(self):
        """
        Read file and load in memory line by line
        :return: Iterator line by line
        """
        try:
            with open(self._file_path, 'r') as f:
                for line in f:
                    yield line
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def data(self):
        """
        Get data loaded
        :return: Dictionary with data loaded [Dictionary]
        """
        return self._data

    def count(self):
        """
        Count of records loaded from JSON file
        :return: Number of records [Long]
        """
        return len(self._data)

    def get(self, keypath):
        """
        Get property of data loaded
        :param keypath: key path to value. Keys of the path separated by '/' [String]
        :return: Value searched or None if key path is not found in the structure
        """
        keys = keypath.split('/')
        data = self._data
        try:
            for key in keys:
                data = data[key]
        except Exception as _:
            data = None
            pass
        return data

    def get_file_path(self):
        """
        Get file path
        :return: File path [String]
        """
        return self._file_path

    def to_lines(self):
        """
        Convert file from json list to json file
        :return: None
        """
        try:
            if not self._json_lines:
                f = fileinput.input(self._file_path, inplace=1)
                for line in f:
                    line = line.replace('[', '')
                    line = line.replace(']', '')
                    line = line.replace('},{', '}\n{')
                    line = line.replace('}, {', '}\n{')
                    line = line.replace('} ,{', '}\n{')
                    line = line.replace('} , {', '}\n{')
                    print line,
                f.close()
                self._json_lines = True
                self.load()
            else:
                raise Exception('File already has json lines format')
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def normalize(self):
        """
        Normalize file (flatten file)
        :return: None
        """
        try:
            # Normalize data
            if not self._data:
                raise Exception('File not loaded')
            data_normalized = json_normalize(self._data)

            # Dataframe
            df = DataFrame(data_normalized)
            # df.columns = df.columns.str.strip().str.lower().str.replace('$', '')
            self._data = df.to_dict(orient='records')
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def to_parquet(self, file_path=None, schema='hive', partition_on=list(), row_group_offsets=100000):
        """
        Save data to parquet
        :param file_path: Path to save the parquet file [String]
        :param schema: hive or simple [String]
        :param partition_on: List of columns to partition the data [List<String>]
        :param row_group_offsets: Number of rows to split the data in multiples files [Long]
        :return: File path [String]
        """
        try:
            if not file_path:
                file_path = self._file_path.replace('.json', '.parquet')
            print(file_path)
            write(file_path,
                  data=DataFrame(self._data),
                  partition_on=partition_on,
                  compression='GZIP',
                  row_group_offsets=row_group_offsets,
                  file_scheme=schema)
            return file_path
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def save(self, file_path=None):
        """
        Save file to disk
        :param file_path: Path to save the file. Default behavior overwrite original file [String]
        :return: File path [String]
        """
        try:
            if not file_path:
                file_path = self._file_path

            self._set_file_path(self._file_path)

            with open(file_path, 'w') as outfile:
                json.dump(self._data, outfile)
            return file_path
        except Exception as ex:
            self._logger.error(repr(ex))
            raise

    def compress(self, destination=None):
        """
        Compress JSON file
        :param destination: Destination file path. Default: same name with suffix '.gz' [String]
        :return: Full path of new file created [String]
        """
        try:
            if not destination:
                destination = self._file_path + '.gz'

            with gzip.open(destination, 'wb') as gzipfile:
                for line in self.read():
                    gzipfile.write(line)
            self._file_path_compressed = destination

            return self._file_path_compressed
        except Exception as ex:
            self._logger.error(repr(ex))
            raise
