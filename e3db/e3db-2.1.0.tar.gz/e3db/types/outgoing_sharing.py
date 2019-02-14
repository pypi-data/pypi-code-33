import uuid


class OutgoingSharingPolicy():

    def __init__(self, json):
        """
        Initialize the OutgoingSharingPolicy class.

        Parameters
        ----------
        json : dict
            Dictionary including reader_id, reader_name, and record_type.

        Returns
        -------
        None
        """
        self.__reader_id = uuid.UUID(json['reader_id'])
        self.__reader_name = str(json['reader_name'])
        self.__record_type = str(json['record_type'])

    # reader_id getters
    @property
    def reader_id(self):
        """
        Get reader_id

        Parameters
        ----------
        None

        Returns
        -------
        uuid.UUID
            reader_id
        """
        return self.__reader_id

    # reader_name getters
    @property
    def reader_name(self):
        """
        Get reader_name

        Parameters
        ----------
        None

        Returns
        -------
        str
            reader_name
        """
        return self.__reader_name

    # record_type getters
    @property
    def record_type(self):
        """
        Get record_type

        Parameters
        ----------
        None

        Returns
        -------
        str
            record_type
        """
        return self.__record_type

    def to_json(self):
        """
        Serialize the configuration as JSON-style object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            JSON-style document containing the Policy elements.
        """

        return {
            'reader_id': str(self.__reader_id),
            'reader_name': str(self.__reader_name),
            'record_type': str(self.__record_type)
        }
