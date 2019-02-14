import uuid


class Query(object):

    def __init__(self, count, after_index=0, include_data=False,
            writer_ids=None, user_ids=None, record_ids=None, content_types=None,
            plain={}, include_all_writers=False):
        """
        Initialize the Query class.

        This object type is used to build a Query to run against the server.
        It is exposed through the e3db.Client.query method.

        Parameters
        ----------
        count : int
            How many records to include.

        after_index : int
            Where to start the query at. The server returns indicies which can
            be used to mark a query, so another query can be done, including the
            after_index to pick up where the other left off. Useful for batch
            and large jobs.
            Optional.

        include_data : bool
            Whether to include data, or just meta data when retrieving the
            E3DB records.
            Optional.

        writer_ids : list
            A list of writer_ids to use for filtering.
            Optional.

        user_ids : list
            A list of user_ids to use for filtering.
            Optional.

        record_ids : list
            A list of record_ids to lookup and use for filtering results.
            Optional.

        content_types : list
            A list of record types to use for filtering.
            Optional.

        plain : dict
            A JSON-style dictionary of a plaintext meta data query to use for
            filtering based on plaintext metadata of the Records.

        include_all_writers : bool
            Whether or not to include all writers, or just the writer_id of the
            client.

        Returns
        -------
        None
        """
        self.__count = int(count)
        self.__after_index = int(after_index)
        self.__include_data = bool(include_data)
        self.__writer_ids = [uuid.UUID(i) for i in writer_ids]
        self.__user_ids = [uuid.UUID(i) for i in user_ids]
        self.__record_ids = [uuid.UUID(i) for i in record_ids]
        self.__content_types = [str(i) for i in content_types]
        self.__plain = dict(plain) if plain is not None else None
        self.__include_all_writers = bool(include_all_writers)

    # count getters
    @property
    def count(self):
        """
        Get count of Query.

        Parameters
        ----------
        None

        Returns
        -------
        int
            Get count of records.
        """
        return self.__count

    # after_index getters
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
        return self.__after_index

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
        self.__after_index = int(value)

    # include_data getters
    @property
    def include_data(self):
        """
        Get included_data of Query.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            Whether data is included with the records.
        """
        return self.__include_data

    # writer_ids getters
    @property
    def writer_ids(self):
        """
        Get writer_ids of Query.

        Parameters
        ----------
        None

        Returns
        -------
        list <uuid.UUID>
            List of writer_ids.
        """
        return self.__writer_ids

    # user_ids getters
    @property
    def user_ids(self):
        """
        Get user_ids of Query.

        Parameters
        ----------
        None

        Returns
        -------
        list <uuid.UUID>
            List of user_ids.
        """
        return self.__user_ids

    # record_ids getters
    @property
    def record_ids(self):
        """
        Get record_ids of Query.

        Parameters
        ----------
        None

        Returns
        -------
        list <uuid.UUID>
            List of record_ids.
        """
        return self.__record_ids

    # content_types getters
    @property
    def content_types(self):
        """
        Get content_types of Query.

        Parameters
        ----------
        None

        Returns
        -------
        list <uuid.UUID>
            List of content_types.
        """
        return self.__content_types

    # plain getters
    @property
    def plain(self):
        """
        Get plaintext query.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            plaintext query
        """
        return self.__plain

    # include_all_writers getters
    @property
    def include_all_writers(self):
        """
        Get whether the query included all writers.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            include_all_writers
        """
        return self.__include_all_writers

    def to_json(self):
        """
        Serialize the configuration as JSON-style object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            JSON-style document containing the Query elements.
        """
        return {
            'count': int(self.__count),
            'after_index': int(self.__after_index),
            'include_data': bool(self.__include_data),
            'writer_ids': [str(i) for i in self.__writer_ids],
            'user_ids': [str(i) for i in self.__user_ids],
            'record_ids': [str(i) for i in self.__record_ids],
            'content_types': [str(i) for i in self.__content_types],
            'plain': self.__plain,
            'include_all_writers': bool(self.__include_all_writers)
        }
