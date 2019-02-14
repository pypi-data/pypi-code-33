
class Range():
    def __init__(self, key="CREATED", format="Unix", zone="UTC", zone_offset=None, start=None, end=None):
        """
        Initialize the Range class for use in Search. This class can be manually created if needed, but 
        the Search.range() method handles the Search workflow.

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
        
        end : time, optional
            Search only for records that come before this time 
            (the default is None, which leaves no upper bound on the query)
        
        after : time, optional
            Search only for record that come after this time 
            (the default is None, which leaves no lower bound on the query)
        
        Returns
        ----------
        None
        """
        self.__key = key
        self.__format = format
        self.__zone = zone
        self.__start = start 
        self.__end = end
        self.zone_dict = {
            "PST":"-08:00",
            "MST":"-07:00",
            "CST":"-06:00",
            "EST":"-05:00",
            "UTC":"+00:00"
        } 
        if zone_offset is not None:
            self.__zone_offset = zone_offset
        else:
            self.__zone_offset = self.zone_dict.get(zone, "+00:00")
    
    @property
    def end(self):
        """
        Get the end time with time zone information appended as a string

        Returns
        -------
        str
            end time properly formatted to send to E3DB.
        """
        return self.__end.isoformat("T") + self.__zone_offset
    
    @end.setter
    def end(self, t):
        """
        Set the end time of Search Range

        Parameters
        ----------
        t : datetime
            upper time bound for Search Range

        Returns
        -------
        None
        """
        self.__end = t

    @property
    def start(self):
        """
        Get the start time with time zone information appended as a string

        Returns
        -------
        str
            start time properly formatted to send to E3DB.
        """
        return self.__start.isoformat("T") + self.__zone_offset

    @start.setter
    def start(self, t):
        """
        Set the start time of Search Range

        Parameters
        ----------
        t : datetime
            lower time bound for Search Range

        Returns
        -------
        None
        """
        self.__after = t

    @property
    def zone(self):
        """
        Get zone of Search Range
        
        Returns
        -------
        str
            zone value
        """
        return self.__zone

    @zone.setter
    def zone(self, z):
        """
        Set zone for Search Range. Will default to "UTC" if proper timezone cannot be found, 
        and will override the value set in zone_offset.

        Parameters
        ----------
        z : str
            Proper zone parameter:
            "PST":"-08:00", "MST":"-07:00", "CST":"-06:00", "EST":"-05:00", "UTC":"+00:00"

        Returns
        -------
        None
        """
        self.zone = z
        self.__zone_offset = self.zone_dict.get(z, "+00:00")

    @property
    def zone_offset(self):
        """
        Get zone_offset of Search Range
        
        Returns
        -------
        str
            zone_offset value
        """
        return self.__zone_offset

    @zone_offset.setter
    def zone_offset(self, z):
        """
        Set zone_offset for Search Range

        Parameters
        ----------
        z : str
            Proper zone_offset parameter:
            Accepts the format "[+|-]dd:dd"

        Returns
        -------
        None
        """
        self.zone_offset = z
    
    @property
    def key(self):
        """
        Get Key for Search Range
        
        Returns
        -------
        str
            "CREATED|MODIFIED"
        """
        return self.__key

    @key.setter
    def key(self, k):
        """
        Set Key for Search Range

        Parameters
        ----------
        k : str
            Valid keys: "CREATED|MODIFIED"

        Returns
        -------
        None
        """
        self.__key = k

    def to_json(self):
        """
        Serialize the configuration as JSON-style object.
        
        Returns
        -------
        dict
            JSON-style document containing the Range elements.
        """
        return {
            "range_key": str(self.__key),
            "before": self.end,
            "after": self.start,
        }
