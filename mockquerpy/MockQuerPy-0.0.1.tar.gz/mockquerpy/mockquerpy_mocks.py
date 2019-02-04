#!/usr/bin/env python

# Std lib
from collections import Iterator

# Bigquery return object
from google.cloud.bigquery.table import Row

# Amedia libs
#from lib.gcloud.amediaquery import CONF_TABLE_ATTRIBUTES


class MockRowIterator(Iterator):
    def __init__(self, data):
        self.data = data
        self.dataGen = self.RowIterator()

    def RowIterator(self):
        yield from self.data

    @property
    def total_rows(self):
        return len(self.data)

    def __next__(self):
        return next(self.dataGen)


class MockJob():
    mockdata = (None, )

    def __init__(self, q):
        # print('TEST:BQ:MOCK: MockJob initialized with mockdata:\n\t', end='')
        # print(self.mockdata)
        self.query = q

    def result(self):
        return MockRowIterator(self.mockdata)


class MockJobConfig():
    def __init__(self):
        self.destination = None
        # print('TEST:BQ:MOCK: Inited MockJobConfig')


class MockDataset():
    # The gcloud libs actually get a dataset through a DatasetReference
    # We're omitting this here due keeping the test libs simple
    def __init__(self, dataset_id):
        self.data = {'dataset_id': dataset_id,
                     'table_id': None}

    def dataset(self, dataset_id):
        self.data['dataset_id'] = dataset_id
        return self

    def table(self, table_id):
        self.data['table_id'] = table_id
        return self

    def __str__(self):
        return "{cls} object, dataset_id: {dataset_id}, table_id: {table_id}".\
                format(cls=self.__class__, **self.data)


class _MockBigQuery():
    """Mocking object for google bigquery.  Pass it into AmediaQuery
    to override so that we may run unittests.

    Example usage
    ------------

    aq = AmediaQuery(BigQuery=MockQuery)
    ...

    The following code will just run against the mock object interface
    """

    def __init__(self):
        self.dataset = lambda d: MockDataset(d)
        # print("TEST:BQ:MOCK: MockQuery initialized")

    def query(self, query: str, **kw):
        """Mock function for querying bigquery, spawns a mockjob

        Parameters
        ---------
        query: str: the query, string to run

        Returns
        -------
        MockJob instance

        """
        return MockJob(query)

    def delete_table(self, table_ref: MockDataset):
        """Mockfunction which deletes a dataset

        Parameters
        ----------
        table_ref: MockDataset : reference to dataset we wish to remove

        Returns
        -------
        None

        """
        pass

    def dataset(dataset):
        return MockDataset

    def get_table(table_ref):
        pass

    @staticmethod
    def QueryJobConfig():
        return MockJobConfig()

    @classmethod
    def Client(cls, **kw):
        return cls()


def _set_test_data(data):
    MockJob.mockdata = data
