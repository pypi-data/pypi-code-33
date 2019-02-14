import uuid
import os


def crypto_mode():
    if 'CRYPTO_SUITE' in os.environ and os.environ['CRYPTO_SUITE'] == 'NIST':
        return 'nist'

    return 'sodium'


class ClientDetails():

    def __init__(self, json):
        """
        Initialize the ClientDetails class.

        Parameters
        ----------
        json : dict
            Configuration including keys for client_id, api_key_id, api_secret,
            public_key, and name.

        Returns
        -------
        None
        """

        self.__client_id = uuid.UUID(json['client_id'])
        self.__api_key_id = str(json['api_key_id'])
        self.__api_secret = str(json['api_secret'])
        self.__public_key = dict(json['public_key'])
        self.__name = str(json['name'])

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
            client_id
        """
        return self.__client_id

    # api_key_id getters
    @property
    def api_key_id(self):
        """
        Get api_key_id of Client.

        Parameters
        ----------
        None

        Returns
        -------
        str
            api_key_id
        """
        return self.__api_key_id

    # api_secret getters
    @property
    def api_secret(self):
        """
        Get api_secret of Client.

        Parameters
        ----------
        None

        Returns
        -------
        str
            api_secret
        """
        return self.__api_secret

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
            Base64 URLencoded public_key of Client.
        """
        if crypto_mode() == 'nist':
            return self.__public_key['p384']
        else:
            return self.__public_key['curve25519']

    # name getters and setters
    @property
    def name(self):
        """
        Get name of Client.

        Parameters
        ----------
        None

        Returns
        -------
        str
            Name of Client.
        """
        return self.__name

    def to_json(self):
        """
        Serialize the configuration as JSON-style object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            JSON-style document containing the ClientDetails elements.
        """
        return {
            'client_id': str(self.__client_id),
            'api_key_id': str(self.__api_key_id),
            'api_secret': str(self.__api_secret),
            'public_key': dict(self.__public_key),
            'name': str(self.__name)
        }

    def get_api_credentials(self):
        """
        Public method to retrieve the api credentials of the client.

        Parameters
        ----------
        None

        Returns
        -------
        tuple
            (api_key_id, api_secret) api credentials as strings
        """

        return (self.__api_key_id, self.__api_secret)

    def get_client_id(self):
        """
        Public method to retrieve the client_id of the client.

        Parameters
        ----------
        None

        Returns
        -------
        str
            client_id (UUID)
        """
        return str(self.__client_id)

    def get_public_key(self):
        """
        Public method to retrieve the public key of the client.

        Parameters
        ----------
        None

        Returns
        -------
        str
            client_id (UUID)
        """
        if crypto_mode() == 'nist':
            return self.__public_key['p384']
        else:
            return self.__public_key['curve25519']

    def get_name(self):
        """
        Public method to retrieve the name of the client.

        Parameters
        ----------
        None

        Returns
        -------
        str
            client name
        """
        return self.__name
