#!/usr/bin/env python

"""
Read files.
"""

import os
import numpy as np

__author__ = "Tobias Rawald"
__copyright__ = "Copyright 2015, 2018 The PyRQA project"
__credits__ = ["Tobias Rawald",
               "Mike Sips"]
__license__ = "Apache-2.0"
__maintainer__ = "Tobias Rawald"
__email__ = "pyrqa@gmx.net"
__status__ = "Development"


class FileReader(object):
    """
    File reader.
    """

    @staticmethod
    def file_as_float_array(file_path,
                            delimiter=',',
                            column=0,
                            offset=0):
        """
        Return file data as float array.

        :param file_path: Path to input file.
        :param delimiter: Column delimiter.
        :param column: Column to be extracted.
        :param offset: Number of leading input file lines that shall be ignored.
        :return: Series of float values.
        """

        with open(file_path, 'r') as input_file:
            lines = input_file.readlines()

            if offset < len(lines):
                lines = lines[offset:]

            line_count = 0
            result = []

            for line in lines:
                splitted_line = line.strip().split(delimiter)

                if len(splitted_line) > column:
                    result.append(np.float32(splitted_line[column]))
                else:
                    line_count += 1
                    out_str = "No element of index %d in line '%s'." % (column, line)
                    print(out_str)

            if line_count:
                out_str = "%d lines could not be processed." % line_count
                print(out_str)

            return np.array(result)

    @staticmethod
    def file_as_string(dir_path,
                       file_name):
        """
        Return file data as string.

        :param dir_path: Path to directory.
        :param file_name: Name of input file.
        :return: File data.
        """

        with open(os.path.join(dir_path, file_name)) as input_file:
            return input_file.read()
