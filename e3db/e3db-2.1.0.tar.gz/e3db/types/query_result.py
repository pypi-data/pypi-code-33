from .query import Query
from .record import Record


class QueryResult(object):

    def __init__(self, query, records):
        """
        Initialize the QueryResult class.

        This object type is used as a storage for the results of an E3DB query.
        The main purpose is to allow iteration over a list of returned records
        that are the result of a Query operation.

        Parameters
        ----------
        query : e3db.Query
            Query object stored for later operations, such as looking up the
            after index returned from the server during query execution.

        records : list<e3db.Record>
            A list of records to store for later iteration and operations.

        Returns
        -------
        None
        """

        if query and (not isinstance(query, Query)):
            raise TypeError("Query object is not e3db.Query type. Given type: {0}".format(type(query)))
        else:
            self.__query = query

        # Check that all records in this list are of type e3db.Record
        if records and (not all(isinstance(x, Record) for x in records)):
            raise TypeError("Records should be a list of e3db.Record types. Given type: {0}".format(type(records)))
        else:
            self.__records = records

    # after_index getters and setters
    @property
    def after_index(self):
        """
        Get after_index of Query.

        Parameters
        ----------
        None

        Returns
        -------
        int
            Get after_index of the Query.
        """
        return self.__query.after_index

    @after_index.setter
    def after_index(self, value):
        """
        Set after_index of QueryResult

        Parameters
        ----------
        value: int
            Set after_index from server result

        Returns
        -------
        None
        """
        self.__query.after_index = int(value)

    def __iter__(self):
        """
        Iterate over record objects.

        Parameters
        ----------
        None

        Returns
        -------
        iter
            Iterator over record objects returned from the Query.
        """

        return iter(self.__records)

    def __len__(self):
        """
        Get amount of records returned from the Query.

        Parameters
        ----------
        None

        Returns
        -------
        int
            Amount of records returned from the Query.
        """

        return len(self.__records)
