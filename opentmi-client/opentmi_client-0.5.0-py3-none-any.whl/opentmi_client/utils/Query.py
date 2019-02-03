"""
Query creator module
"""
import json


class Query(object):
    """
    Base Query class
    """
    def __init__(self):
        """
        Constructor for Query
        """
        self.__query = {}

    def set(self, key, value):
        """
        Set value to query
        :param key: string
        :param value:
        :return: Query
        """
        self.__query[key] = value
        return self

    def to_string(self):
        """
        convert query to string
        :return: query as a string
        """
        return json.dumps(self.__query)



class Request(object):
    """
    Request object to create mongoose-query related url parameters
    """
    def __init__(self, request_type):
        """
        Constructor for Request
        :param request_type: type
        """
        self.__request = {
            "t": request_type,
            "q": Query()}

    @property
    def query(self):
        """
        Getter for Query object
        :return: Query
        """
        return self.__request["q"]

    def _set(self, key, value):
        self.__request[key] = value

    def _has(self, key):
        return key in self.__request

    def _push(self, key, value):
        if not self._has(key):
            self._set("f", "")
        else:
            self.__request[key] += " "
        self.__request[key] += value

    def params(self):
        """
        Get params for Transport
        :return: dict
        """
        request = self.__request.copy()
        request["q"] = request["q"].to_string()
        return request


class Find(Request):
    """
    Find Request
    """
    def __init__(self):
        """
        Constructor for Find query
        """
        Request.__init__(self, "find")

    def limit(self, limit):
        """
        Limit results items
        :param limit:
        :return: Find
        """
        self._set("l", limit)
        return self

    def skip(self, skip):
        """
        Skip results
        :param skip:
        :return: Find
        """
        self._set("sk", skip)
        return self

    def select(self, field):
        """
        Select some fields to be fetched
        :param field:
        :return: Find
        """
        self._push("f", field)
        return self



class Distinct(Request):
    """
    Distinct kind of request
    """
    def __init__(self):
        """
        Constructor for Distinct
        """
        Request.__init__(self, "distinct")

    def select(self, field):
        """
        Select field to be distinct
        :param field:
        :return: Distinct
        """
        self._set("f", field)
        return self
