import copy
from .meta import Meta


class Record():

    def __init__(self, meta=None, data=None):
        """
        Initialize the Record class.

        Parameters
        ----------
        meta : e3db.Meta
            Meta data object to include with the record.
            Required.

        data : dict
            JSON key-value store of data to be encrypted.

        Returns
        -------
        None
        """

        # Check that meta being passed in is of e3db.Meta type.
        if meta and (not isinstance(meta, Meta)):
            raise TypeError("Meta object is not e3db.Meta type. Given type: {0}".format(type(meta)))
        else:
            self.__meta = meta

        # Check that data passed in is a dictionary
        if data and (not isinstance(data, dict)):
            raise TypeError("Data object is not dict. Given type: {0}".format(type(data)))

        # make copy of the data so we dont modify the original object passed in
        self.__data = copy.deepcopy(data)

    def to_json(self):
        """
        Serialize the configuration as JSON-style object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            JSON-style document containing the Record elements.
        """

        return {
            'meta': self.__meta.to_json(),
            'data': self.__data
        }

    # meta getters and setters
    @property
    def meta(self):
        """
        Get meta

        Parameters
        ----------
        None

        Returns
        -------
        e3db.Meta
            meta
        """
        return self.__meta

    @meta.setter
    def meta(self, value):
        """
        Set reader_name

        Parameters
        ----------
        value : e3db.Meta
            Meta from the Record.

        Returns
        -------
        None
        """
        self.__meta = value

    # data getters and setters
    @property
    def data(self):
        """
        Get data

        Parameters
        ----------
        None

        Returns
        -------
        dict
            data from record
        """
        return self.__data

    @data.setter
    def data(self, value):
        """
        Set data

        Parameters
        ----------
        value : dict
            data of the Record

        Returns
        -------
        None
        """
        self.__data = value

    def get_meta(self):
        """
        Get Meta object from the Record.

        Parameters
        ----------
        None

        Returns
        -------
        e3db.Meta
            Meta from the Record.
        """

        return self.__meta

    def get_data(self):
        """
        Get data dict from the Record.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            JSON-style key-value pairs of the plaintext data
        """

        return self.__data

    def update_meta(self, meta):
        """
        Update Meta object of the Record.

        Parameters
        ----------
        meta : e3db.Meta
            Meta from the Record.

        Returns
        -------
        None
        """

        self.__meta = meta

    def update(self, meta, data):
        """
        Update entire Record object.

        Replaces current meta and data with passed in data.

        Parameters
        ----------
        meta : e3db.Meta
            Meta from the Record.

        data : dict
            JSON-style key-value pairs of the plaintext data

        Returns
        -------
        None
        """

        self.__meta = meta
        self.__data = data
