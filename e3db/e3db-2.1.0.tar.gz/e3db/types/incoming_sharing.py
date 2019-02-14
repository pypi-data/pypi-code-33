import uuid


class IncomingSharingPolicy(object):
    """
    Class to create Incoming Sharing policy object.

    This class is a data holding class, similar to a C-style struct.
    """

    def __init__(self, json):
        """
        Initialize the Config class.

        Parameters
        ----------
        json : dict
            Dictionary including writer_id, writer_name, and record_type.

        Returns
        -------
        None
        """

        # Will throw exception if UUID is malformed
        self.__writer_id = uuid.UUID(json['writer_id'])
        self.__writer_name = str(json['writer_name'])
        self.__record_type = str(json['record_type'])

    # writer_id getters
    @property
    def writer_id(self):
        """
        Get writer_id

        Parameters
        ----------
        None

        Returns
        -------
        uuid.UUID
            writer_id
        """
        return self.__writer_id

    # writer_name getters
    @property
    def writer_name(self):
        """
        Get writer_name

        Parameters
        ----------
        None

        Returns
        -------
        str
            writer_name
        """
        return self.__writer_name

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
            'writer_id': str(self.__writer_id),
            'writer_name': str(self.__writer_name),
            'record_type': str(self.__record_type)
        }
