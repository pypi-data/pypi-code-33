import uuid
import os


def crypto_mode():
    if 'CRYPTO_SUITE' in os.environ and os.environ['CRYPTO_SUITE'] == 'NIST':
        return 'nist'

    return 'sodium'


class ClientInfo():

    def __init__(self, client_id, public_key, validated):
        """
        Initialize the ClientInfo class.

        If certain keys, such as record_id, created, last_modified, and version
        are not missing (such as when a record is created, but these variables
        have not been set by the server yet).

        Parameters
        ----------
        client_id : str
            UUID of the client

        public_key : dict
            Type of key, and Base64URL encoded string of bytes that is the
            client's public key.

        validated : bool
            Whether then client has been validated or not.

        Returns
        -------
        None
        """
        self.__client_id = uuid.UUID(client_id)
        self.__public_key = dict(public_key)
        self.__validated = bool(validated)

    # client_id getters
    @property
    def client_id(self):
        """
        Get client_id of Client.

        Parameters
        ----------
        None

        Returns
        -------
        uuid.UUID
            client_id of the Client
        """
        return self.__client_id

    # public_key getters
    @property
    def public_key(self):
        """
        Get public_key of Client.

        Parameters
        ----------
        None

        Returns
        -------
        str
            Base64 URL encoded public_key of the Client
        """
        if crypto_mode() == 'nist':
            return self.__public_key['p384']
        else:
            return self.__public_key['curve25519']

    # validated getters
    @property
    def validated(self):
        """
        Get validated status of Client.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            Boolean of validated status of Client.
        """
        return self.__validated

    def to_json(self):
        """
        Serialize the configuration as JSON-style object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            JSON-style document containing the ClientInfo elements.
        """

        return {
            'client_id': str(self.__client_id),
            'public_key': dict(self.__public_key),
            'validated': bool(self.__validated)
        }
