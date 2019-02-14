import json
import os


class Config:
    """
    Class to create E3DB configuration, or load from a file.

    The configuration containers client api keys, the encryption keys, and
    other configuration elements.
    """

    DEFAULT_API_URL = "https://api.e3db.com"

    def __init__(self, client_id, api_key_id, api_secret, public_key, private_key, client_email="", version="1", api_url=DEFAULT_API_URL):
        """
        Initialize the Config class.

        Parameters
        ----------
        client_id : str
            UUID of the client

        api_key_id : str
            Public api key obtained from the server

        api_secret : str
            Secret api key obtained from the server

        public_key : str
            Public key used for crypto operations. Base64URL encoded string of
            bytes.

        private_key : str
            Private key used for crypto operations. Base64URL encoded string of
            bytes.

        client_email : str
            Email of the client.
            Optional.

        version : str
            Version of the configuration file style. Defaults to 1.
            Optional.

        api_url : str
            Manually specified API url. Defaults to DEFAULT_API_URL.
            Optional.

        Returns
        -------
        None
        """

        self.version = version
        self.client_id = client_id
        self.api_key_id = api_key_id
        self.api_secret = api_secret
        self.client_email = client_email
        self.public_key = public_key
        self.private_key = private_key
        self.api_url = api_url

    def __call__(self):
        """
        Serialize the configuration when the Config object is called.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            JSON-style document container the configuration elements.
        """

        return {
            'version': self.version,
            'client_id': self.client_id,
            'api_key_id': self.api_key_id,
            'api_secret': self.api_secret,
            'client_email': self.client_email,
            'public_key': self.public_key,
            'private_key': self.private_key,
            'api_url': self.api_url,
        }

    @classmethod
    def __load_file(self, filename):
        """
        Private method to open a configuration file and return it as JSON.

        Parameters
        ----------
        filename : str
            Profile path to load. A full path, or relative path.

        Returns
        -------
        dict
            JSON of configuration file loaded.
        """

        try:
            with open(filename) as e3db_config:
                data = json.load(e3db_config)
            return data
        except ValueError as error:
            print("Loading E3DB json file failed. Perhaps the JSON is malformed?")
            print("Error: " + str(error))

    @classmethod
    def load(self, profile=''):
        """
        Public method to load a configuration file and return it as JSON.

        Parameters
        ----------
        profile : str
            Profile to load. Empty string loads ~/.tozny/e3db.json.
            profile='dev' would load ~/.tozny/dev/e3db.json

        Returns
        -------
        dict
            JSON of configuration file loaded.
        """
        # if profile is empty we read the default ~/.tozny/e3db.json file
        home = os.path.expanduser('~')
        return Config.__load_file(os.path.join(home, '.tozny', profile, 'e3db.json'))

    def write(self, profile=''):
        """
        Public method to write a configuration file.

        Parameters
        ----------
        profile : str
            Profile to write to. Empty string writes to ~/.tozny/e3db.json.
            profile='dev' would write ~/.tozny/dev/e3db.json

        Returns
        -------
        None
        """
        # if profile is empty we read the default ~/.tozny/e3db.json file
        home = os.path.expanduser('~')
        directory = os.path.join(home, '.tozny', profile)
        if not os.path.exists(directory):
            os.makedirs(directory)
        # Check if file already exists, if so, throw exception to prevent
        # overwriting of key material
        file_path = os.path.join(home, '.tozny', profile, 'e3db.json')
        if os.path.exists(file_path):
            raise IOError("File {0} already exists.".format(file_path))
        with open(file_path, 'w+') as f:
            config = {
                'version': str(self.version),
                'client_id': str(self.client_id),
                'api_key_id': str(self.api_key_id),
                'api_secret': str(self.api_secret),
                'client_email': str(self.client_email),
                'public_key': str(self.public_key),
                'private_key': str(self.private_key),
                'api_url': str(self.api_url),
            }
            f.write(json.dumps(config, indent=4, separators=(',', ': ')))
