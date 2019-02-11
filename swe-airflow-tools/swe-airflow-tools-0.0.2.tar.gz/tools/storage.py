#! -*- coding: utf-8 -*-

import abc
import csv
import os

from collections import namedtuple


class IStorage(metaclass=abc.ABCMeta):

    #__slots__ = ['_storage_name', '_storage_reference', '_rows', '_fields_mapping', '_reader', '_model',  '_length']

    def __init__(self, storage_name, storage_reference=None, rows=None, fields_mapping=None, model=None):
        """

        """
        self._storage_name = storage_name
        self._storage_reference = storage_reference
        self._rows = rows
        self._fields_mapping = fields_mapping
        self._model = model

        self._reader = None
        self._length = 0

        if not self._fields_mapping and self._model:
            self._fields_mapping = self._model._fields

    @abc.abstractmethod
    def __iter__(self):
        """ Implements in child for determine what the iteration """
        raise NotImplemented()

    @abc.abstractmethod
    def write(self, rows=None, storage_reference=None, clear_rows=True):
        """
        Write the records/_rows for storage destination.

        :param records: records or _rows for storage
        :type records: string

        :return: string with reference for storage location
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def read(self):
        """
        Read the records/_rows for storage source.

        :param records: records or _rows for storage
        :type records: string

        :return: string with reference for storage location
        """
        raise NotImplementedError()

    def find(self, expression):
        """
        Find row in storage

        :param expression: lambda expression
        :return: row
        """
        raise NotImplementedError()

    def clear(self):
        """ Clear rows for release memory """
        self._rows = None

    @property
    def storage_name(self):
        return self._storage_name

    @property
    def storage_reference(self):
        return self._storage_reference

    @storage_reference.setter
    def storage_reference(self, value):
        self._storage_reference = value

    @property
    def fields_mapping(self):
        return self._fields_mapping

    @property
    def rows(self):
        return self._rows


class CSVStorage(IStorage):

    def __init__(self,
                 storage_name,
                 storage_reference=None,
                 rows=None,
                 fields_mapping=None,
                 model=None,
                 has_header=True,
                 delimiter=';',
                 quotechar='"',
                 quoting=csv.QUOTE_NONNUMERIC):
        """

        :param storage_name:
        :param storage_reference:
        :param rows:
        :param fields_mapping:
        :param model:
        :param has_header:
        :param args:
        :param kwargs:
        """

        super(CSVStorage, self).__init__(
            storage_name,
            storage_reference,
            rows=rows,
            fields_mapping=fields_mapping,
            model=model
        )

        self._has_header = has_header
        self._delimiter = delimiter
        self._quotechar = quotechar
        self._quoting = quoting

    def __iter__(self):
        """ Iter over rows in storage.

            If have self._rows, it's already loader in past. Use this for rapid iteration.
            Else load items on demand.
        """
        for row in self._rows or self.read():
            yield row

    def __len__(self):
        """ Read the data for length and counter """
        if self._length == 0:
            for row in self: continue
        return self._length

    def write(self, rows=None, storage_reference=None, clear_rows=True):
        if storage_reference:
            self._storage_reference = storage_reference
        if not self._storage_reference:
            raise Exception('Invalid storage reference!')
        if not os.path.isdir(os.path.dirname(self._storage_reference)):
            os.makedirs(os.path.dirname(self._storage_reference))
        _rows = rows or self._rows or []
        with open(self._storage_reference, 'w') as data:
            writer = csv.writer(
                data,
                delimiter=self._delimiter,
                quotechar=self._quotechar,
                quoting=self._quoting
            )
            if self._fields_mapping:
                writer.writerow(self._fields_mapping)
            writer.writerows([tuple(field for field in row) for row in _rows])
        if clear_rows:
            self.clear()

    def read(self):
        with open(self._storage_reference, 'r', newline='') as data:

            if self._has_header:
                header = data.readline()
            if self._fields_mapping:
                header = self._fields_mapping
            else:
                # TODO : View what csv.reader returns and create list of fake columns
                header = None

            if not self._model:
                self._model = namedtuple(
                    ''.join([name.capitalize() for name in self.storage_name.split('_')]),
                    header
                )

            reader = csv.reader(
                data,
                delimiter=self._delimiter,
                quotechar=self._quotechar,
                quoting=self._quoting
            )

            length = 0
            for row in map(self._model._parse, reader):
                if self._length == 0:
                    length += 1
                yield row

            self._length = length

    def find_all(self, expression):
        """
        Find all records according expression

        :param expression: filter expression
        :param type: lambda expression
        :return:
        """
        return list(filter(expression, self.rows))

    def find_one(self, expression):
        """
        Find one record according expression

        :param expression: filter expression
        :param type: lambda expression
        :return:
        """

        # TODO : Optime search performance
        # https://stackoverflow.com/questions/23116082/indexing-and-finding-values-in-list-of-namedtuples
        # https://stackoverflow.com/questions/20413080/check-if-namedtuple-with-value-x-exists-in-list
        try:
            return self.find_all(expression)[0]
        except IndexError:
            return []

    @property
    def rows(self):
        if not self._rows:
            self._rows = [row for row in self.read()]
        return self._rows

    def to_dict(self):
        return [dict(row._asdict()) for row in self.rows]