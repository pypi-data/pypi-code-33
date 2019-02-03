"""
OpenTMI Data base class
"""

from json import dumps
from pydash import get, set_, unset, map_values_deep
from opentmi_client.utils import remove_empty_from_dict


class BaseApi(object):
    """
    Base class for Data record
    """
    def __init__(self):
        """
        Constructor for BaseApi
        """
        self._data = {}

    @property
    def _id(self):
        """
        Getter for document id
        :return: document _id
        """
        return self.get('_id')

    @_id.setter
    def _id(self, value):
        """
        document id setter
        :param value: _id
        :return: _id
        """
        return self.set('_id', value)

    @property
    def is_empty(self):
        """
        :return: True data is empty
        """
        return len(self._data.keys()) == 0

    def set_data(self, data):
        """
        Set whole data dictionary
        :param data: Dictionary
        :return: None
        """
        self._data = data

    @property
    def data(self):
        """
        Get plain Dictionary object which are suitable for OpenTMI backend
        :return: Dictionary containsi whole data
        """
        data = map_values_deep(self._data, lambda x: x.data if isinstance(x, BaseApi) else x)
        return remove_empty_from_dict(data)

    @data.setter
    def data(self, values):
        """
        Set plain dictionary object which are suitable for OpenTMI backend
        :param values:
        :return:
        """
        data = remove_empty_from_dict(values)

        def has_attribute(ref, key):
            """
            Validates that attribute key has in ref
            :param ref: Object
            :param key: String
            :return: None
            :raise KeyError: if does not exists
            """
            if not hasattr(ref, key):
                raise KeyError("Key '{}' does not exists".format(key))

        def fnc(value, path):
            """
            mapper function
            :param value: Value to be set
            :param path: array of nested path
            :return:
            """
            ref = self
            for key in path[0:-1]:
                has_attribute(ref, key)
                ref = getattr(ref, key)
            key = path[-1]
            has_attribute(ref, key)
            setattr(ref, key, value)
        map_values_deep(data, fnc)

    def get(self, key, default=None):
        """
        Get value based on key
        :param key: String
        :param default: Default value if not found
        :return: Value for key. Some keys presents another BaseApi object
        """
        return get(self._data, key, default)

    def set(self, key, value):
        """
        Set value for key
        :param key: String
        :param value: new value for key
        :return: value
        """
        set_(self._data, key, value)
        return value

    def unset(self, key):
        """
        Remove key from object
        :param key: String
        :return: self
        """
        unset(self._data, key)
        return self

    def __str__(self):
        """
        Returns stringified json object
        :return: String
        """
        return dumps(self.data, indent=2, default=lambda o: o.data)
