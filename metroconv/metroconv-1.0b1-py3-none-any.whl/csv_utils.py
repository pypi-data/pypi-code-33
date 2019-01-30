
import csv
import os


class CsvObject(object):

    _path = None
    _contents = None

    def __init__(self, path):
        self._path = path
        self.read_file()

    def __repr__(self):
        return '<CsvObject: {}>'.format(self._path)

    def read_file(self):
        with open(self._path) as infile:
            reader = csv.DictReader(infile)
            self._contents = []
            for line in reader:
                self._contents.append(line)

    @property
    def contents(self):
        return self._contents


def write_csv_file(path, iterable):
    with open(path, 'w') as outfile:
        writer = csv.writer(outfile)
        for item in iterable:
            writer.writerow(item)


def read_csv_file(path):
    return CsvObject(path=path)
