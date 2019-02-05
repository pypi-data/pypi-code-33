class Credentials:
    def __init__(self, access_key_id, secret_access_key, session_token):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.session_token = session_token


class Provider:
    def __init__(self):
        # Do nothing
        pass

    def loads_credentials(self):
        """Returns true if the provider needs to load the credentials
           and provides them. E.g. if you need to make a network request
           for them. Returns false if you want to use the default logic
           to check for credentials via AWS config files, etc."""

        return False

    def credentials(self):
        return None


class APIProvider(Provider):
    def __init__(self, conn, endpoint):
        Provider.__init__(self)
        self.conn = conn
        self.endpoint = endpoint

    def loads_credentials(self):
        return True

    def credentials(self):
        response = self.conn.get(self.endpoint)

        if response.status_code != 200:
            raise ValueError(response.status_code)

        data = response.json()

        aws_access_key_id = data['AccessKeyID']
        aws_secret_access_key = data['SecretAccessKey']
        aws_session_token = data['SessionToken']

        return Credentials(aws_access_key_id, aws_secret_access_key, aws_session_token)
