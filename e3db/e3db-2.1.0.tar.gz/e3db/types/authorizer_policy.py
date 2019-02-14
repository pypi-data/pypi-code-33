import uuid


class AuthorizerPolicy(object):
    """
    Class to create Authorizer policy object.

    This class is a data holding class, similar to a C-style struct.
    """

    def __init__(self, json):
        """
        Initialize the Config class.

        Parameters
        ----------
        json : dict
            Dictionary including authorizer_id, authorizer_name, writer_id,
            user_id, record_type, and authorized_by

        Returns
        -------
        None
        """

        # Will throw exception if UUID is malformed
        self.__authorizer_id = uuid.UUID(json['authorizer_id'])
        self.__writer_id = uuid.UUID(json['writer_id'])
        self.__user_id = uuid.UUID(json['user_id'])
        self.__record_type = str(json['record_type'])
        self.__authorized_by = uuid.UUID(json['authorized_by'])

    # authorizer_id getters
    @property
    def authorizer_id(self):
        """
        Get authorizer_id

        Parameters
        ----------
        None

        Returns
        -------
        uuid.UUID
            authorizer_id
        """
        return self.__authorizer_id

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

    # user_id getters
    @property
    def user_id(self):
        """
        Get user_id

        Parameters
        ----------
        None

        Returns
        -------
        uuid.UUID
            user_id
        """
        return self.__user_id

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

    # authorized_by getters
    @property
    def authorized_by(self):
        """
        Get authorized_by

        Parameters
        ----------
        None

        Returns
        -------
        uuid.UUID
            authorized_by
        """
        return self.__authorized_by

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
            'authorizer_id': str(self.__authorizer_id),
            'authorizer_name': str(self.__authorizer_name),
            'writer_id': str(self.__writer_id),
            'user_id': str(self.__user_id),
            'record_type': str(self.__record_type),
            'authorized_by': str(self.__authorized_by)
        }
