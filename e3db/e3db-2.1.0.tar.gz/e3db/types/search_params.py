import uuid

class Params(object):
    def __init__(self, condition="OR", strategy="EXACT", keys=None, values=None, writer_ids=None, user_ids=None, record_ids=None, content_types=None, plain={}):
        """
        Initialize the Search Params class.

        This object type is used to build the params for searching with E3DB.

        Parameters
        ----------
        condition : str, optional
            "OR|AND" (the default is "OR")
            Provided parameters are either OR-ed or AND-ed together based on the condition provided.

        strategy : str, optional
            "EXACT|FUZZY|WILDCARD|REGEXP" (the default is "EXACT")
            Determines the strategy when matching the parameters provided.

        writer : list, optional
            List of writer ids to filter on (the default is [], which matches all)

        record : list, optional
            List of reader ids to filter on (the default is [], which matches all)

        user : list, optional
            List of user ids to filter on (the default is [], which matches all)

        record_type : list, optional
            List of record_types to filter on (the default is [], which matches all)

        keys : list, optional
            List of keys to filter on (the default is [], which matches all)

        values : list, optional
            List of values to filter on (the default is [], which matches all)

        plain : dict, optional
            Plaintext meta data to match against record plaintext meta data fields.
        
        Returns
        -------
        Params
        """
        self.__condition = condition
        self.__strategy = strategy
        self.__writer_ids = [i if isinstance(i, uuid.UUID) else uuid.UUID(i) for i in writer_ids]
        self.__user_ids = [i if isinstance(i, uuid.UUID) else uuid.UUID(i) for i in user_ids]
        self.__record_ids = [i if isinstance(i, uuid.UUID) else uuid.UUID(i) for i in record_ids]
        self.__content_types = [str(i) for i in content_types]
        self.__plain = dict(plain) if plain is not None else None
        self.__values = [str(i) for i in values]
        self.__keys = [str(i) for i in keys]

    @property
    def condition(self):
        """
        Get condition of Search Params
        
        Returns
        -------
        str
            "OR|AND"
        """
        return self.__condition

    @condition.setter
    def condition(self, s):
        """
        Set condition of Search Params

        Parameters
        ----------
        s : str
            "OR|AND"

        Returns
        -------
        None
        """
        self.__condition = s

    @property
    def strategy(self):
        """
        Get strategy of Search Params
        
        Returns
        -------
        str
            "EXACT|FUZZY|WILDCARD|REGEXP" 
        """
        return self.__strategy

    @strategy.setter
    def strategy(self, s):
        """
        Set strategy of Search Params

        Parameters
        ----------
        s : str
            "EXACT|FUZZY|WILDCARD|REGEXP" 

        Returns
        -------
        None
        """
        self.__strategy = s

    @property
    def users(self):
        """
        Get user_ids of Search Params
        
        Returns
        -------
        list
            list of user_ids in this Param object
        """
        return self.__user_ids

    @users.setter
    def users(self, ids):
        """
        Set user_ids of Search Params

        Parameters
        ----------
        ids : list
            list of user_ids to set in this Search Param

        Returns
        -------
        None
        """
        self.__user_ids = ids

    @property
    def writers(self):
        """
        Get writer_ids of Search Params
        
        Returns
        -------
        list
            list of writer_ids in this Param object
        """
        return self.__writer_ids

    @writers.setter
    def writers(self, ids):
        """
        Set writer_ids of Search Params

        Parameters
        ----------
        ids : list
            list of writer_ids to set in this Search Param

        Returns
        -------
        None
        """
        self.__writer_ids = ids

    @property
    def records(self):
        """
        Get record_ids of Search Params
        
        Returns
        -------
        list
            list of record_ids in this Param object
        """
        return self.__record_ids

    @records.setter
    def records(self, ids):
        """
        Set record_ids of Search Params

        Parameters
        ----------
        ids : list
            list of record_ids to set in this Search Param

        Returns
        -------
        None
        """
        self.__record_ids = ids

    @property
    def keys(self):
        """
        Get keys of Search Params
        
        Returns
        -------
        list
            list of keys in this Param object
        """
        return self.__keys

    @keys.setter
    def keys(self, s):
        """
        Set keys of Search Params

        Parameters
        ----------
        s : list
            list of keys to set in this Search Param

        Returns
        -------
        None
        """
        self.__keys = s

    @property
    def values(self):
        """
        Get values of Search Params
        
        Returns
        -------
        list
            list of values in this Param object
        """
        return self.__values

    @values.setter
    def values(self, s):
        """
        Set values of Search Params

        Parameters
        ----------
        s : list
            list of values to set in this Search Param

        Returns
        -------
        None
        """
        self.__values = s

    @property
    def plain(self):
        """
        Get plain of Search Params
        
        Returns
        -------
        dict
            dict of plain meta tags in this Param object
        """
        return self.__plain

    @plain.setter
    def plain(self, d):
        """
        Set plain of Search Params

        Parameters
        ----------
        d: dict
            dict of plain meta tags in this Param object

        Returns
        -------
        None
        """
        self.__plain = d

    def to_json(self):
        """
        Serialize the configuration as JSON-style object.
        
        Returns
        -------
        dict
            JSON-style document containing the Param elements.
        """
        return {
            "condition": self.__condition,
            "strategy": self.__strategy,
            "terms": {
                "writer_ids": [str(i) for i in self.__writer_ids],
                "user_ids": [str(i) for i in self.__user_ids],
                "record_ids": [str(i) for i in self.__record_ids],
                "content_types": [str(i) for i in self.__content_types],
                "keys": [str(i) for i in self.__keys],
                "values": [str(i) for i in self.__values],
                "tags": self.__plain
            }
        }