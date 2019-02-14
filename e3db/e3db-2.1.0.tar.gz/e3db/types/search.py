import time
from .search_range import Range
from .search_params import Params

class Search(object):
    def __init__(self, next_token=0, count=50, include_all_writers=False, include_data=False, match=None, exclude=None, range=None): 
        """
        Initialize the search v2 class.

        This object type is used to build a v2/search query to run against the server.
        It is exposed through the e3db.Client.search method.

        Parameters
        ----------
        next_token : int, optional
            Where to start the query at. E3DB will return an token which indicates
            where the  query left off. Another query can be executed including this next_token, and 
            it will pick off where the other left off (the default is 0, which starts from the beginning).

        count : int, optional
            How many records to include minimum of 1 and up to a maximum of 1000 (the default is 50).
            Based on the current version, the resulting query might return less than this count, even if
            there are more records available. The query will need to be re-run with the corresponding next_token.

        include_all_writers : bool, optional
            Whether or not to include all writers, or just the writer_id of the 
            (the default is False).

        include_data : bool, optional
            Whether to include data, or just meta data when retrieving the
            E3DB records (the default is False).

        match : [Params], optional
            A list of Search Param objects to Match when querying for Records
            (the default is None, which matches all records).

        exclude : [Params], optional
            A list of Search Param objects to Exclude when querying for Records
            (the default is None, which matches no records excluding nothing).

        range : Range, optional
            A Search Range object to filter results based on created or last_modified time
            (the default is None, which removes any time filter.).

        Returns
        -------
        Search
        """
        self.__next_token = int(next_token)
        self.__limit = int(count)
        self.__include_data = bool(include_data)
        self.__include_all_writers = bool(include_all_writers)
        self.__match = match if match else [] 
        self.__exclude = exclude if exclude else []
        self.__range = None
        
    @property
    def matches(self):
        """
        Get list of Params on which to match.
        
        Returns
        -------
        [Params]
            List of Match Parameters
        """
        return self.__match

    @matches.setter
    def matches(self, p):
        """
        Set list of Params on which to match. 
        Overrides current Match Params.

        Parameters
        ----------
        p: [Params]
            Parameters to search on

        Returns
        -------
        None
        """
        self.__match = p

    @property
    def excludes(self):
        """
        Get list of Params on which to exclude.
        
        Returns
        -------
        [Params]
            List of Exclude Parameters
        """
        return self.__exclude

    @excludes.setter
    def excludes(self, p):
        """
        Set list of Params on which to exclude. 
        Overrides current Match Params.

        Parameters
        ----------
        p: [Params]
            Parameters to search on

        Returns
        -------
        None
        """
        self.__exclude = p

    def append_match(self, p):
        """
        Add to list of Params on which to Match

        Parameters
        ----------
        p : Param
             Parameter to add to Match list

        Returns
        -------
        None
        """
        self.__match.append(p)

    def append_exclude(self, p):
        """
        Add to list of Params on which to Exclude

        Parameters
        ----------
        p : Param
             Parameter to add to Exclude list

        Returns
        -------
        None
        """
        self.__exclude.append(p)

    # count getters
    @property
    def count(self):
        """
        Get count of Search.

        Parameters
        ----------
        None

        Returns
        -------
        int
            Get count of records.
        """
        return self.__limit

    # next_token getters
    @property
    def next_token(self):
        """
        Get next_token of Search.

        Parameters
        ----------
        None

        Returns
        -------
        int
            Get next_token of the Search.
        """
        return self.__next_token

    @next_token.setter
    def next_token(self, value):
        """
        Set next_token of SearchResult.

        Parameters
        ----------
        value: int
            Set next_token from server result

        Returns
        -------
        None
        """
        self.__next_token = int(value)

    # include_data getters
    @property
    def include_data(self):
        """
        Get included_data of Search.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            Whether data is included with the records.
        """
        return self.__include_data


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
            JSON-style document containing the Search elements.
        """
        return {
            "limit": int(self.__limit),
            "next_token": int(self.__next_token),
            "include_all_writers": bool(self.__include_all_writers),
            "include_data": bool(self.__include_data),
            "match": [i.to_json() for i in self.__match],
            "exclude": [i.to_json() for i in self.__exclude],
            "range": self.__range.to_json() if self.__range is not None else {}
        }

    def match(self, condition="OR", strategy="EXACT", writers=[], records=[], users=[], record_types=[], keys=[], values=[], plain=None):
        """
        Public method to construct Query Params on which to Match(select) when searching for E3DB records.

        Appends to the List of Match Parameters in the Search Object.
        Independent Match Parameters are OR-ed together. 

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
        Search
            Returns reference to self, allows for chaining of match, exclude, range methods.
        """

        m = Params(condition=condition, strategy=strategy, writer_ids=writers, record_ids=records, user_ids=users, content_types=record_types, keys=keys, values=values, plain=plain)
        self.append_match(m)
        return self

    def exclude(self, condition="OR", strategy="EXACT", writers=[], records=[], users=[], record_types=[], keys=[], values=[], plain=None):
        """
        Public method to construct Query Params on which to Exclude(select) when searching for E3DB records.

        Appends to the List of Exclude Parameters in the Search Object.
        Independent Exclude Parameters are OR-ed together. 

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
        Search
            Returns reference to self, allows for chaining of match, exclude, range methods.
        """
        e = Params(condition=condition, strategy=strategy, writer_ids=writers, record_ids=records, user_ids=users, content_types=record_types, keys=keys, values=values, plain=plain)
        self.append_exclude(e)
        return self
    
    def range(self, key="CREATED", format="Unix", zone="UTC", zone_offset=None, start=None, end=None):
        """
        Public Method to filter search based on time the E3DB record was created or last modified.

        Parameters
        ----------
        key : str, optional
            "CREATED|MODIFIED" (the default is "CREATED")

        format : str, optional
            Currently is not a supported parameter (the default is "Unix")

        zone : str, optional
            Since python time objects are naive or zone-agnostic, this will attempt to append
            the proper timezone information to the time object for the query.
            Currently supported are:
                "PST":"-08:00", "MST":"-07:00", "CST":"-06:00", "EST":"-05:00", "UTC":"+00:00"
                (the default is "UTC" if the proper timezone cannot be found, which represents +00:00)

        zone_offset : str, optional
            If provided this offset will be used over zone.
            Accepts the format "[+|-]dd:dd"
            (the default is None(UTC), which will attempt to use zone if provided)
        
        start : time, optional
            Search only for records that come after this time 
            (the default is None, which leaves no lower bound on the query)
        
        end : time, optional
            Search only for records that come before this time 
            (the default is None, which leaves no upper bound on the query)
        
        Returns
        -------
        Search
            Returns reference to self, allows for chaining of match, exclude, range methods.
        """

        r = Range(key=key, format=format, zone=zone, start=start, end=end)
        self.__range = r
        return self
