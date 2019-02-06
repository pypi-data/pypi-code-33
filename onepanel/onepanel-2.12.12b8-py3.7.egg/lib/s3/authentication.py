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
        self.count = 0

    def loads_credentials(self):
        return True

    def credentials(self):
        response = self.conn.get(self.endpoint)

        if response.status_code != 200:
            raise ValueError(response.status_code)

        data = response.json()

        aws_access_key_id = 'ASIAYMWGQPXDZCQWIZIZ'#data['AccessKeyID']
        aws_secret_access_key = 'RcLYP05yRrL7ZoyMpXhsGPmVV4Zhh7h7YcC+y72X' #data['SecretAccessKey']
        aws_session_token = 'FQoGZXIvYXdzEJf//////////wEaDG9heNWFzemci8EYPSKcA/ump3cIQk/HN+kxC1Ob0QXLu/ou8QDqomLwsQJOLx0skRlveg7dsiz1Qh5KUu9XDUXn7IueICF9+Mv5qMDegK7M6u8pIzlB/txEiuNxKPRRZDHMDjgyysmnwOzr+I4r6Ib5YSVNSV4v4epgzrZtUzgbfohfa6JZwTn8j9emlR7SiaDG5j0Iz36HlE6yQByjrKc2U4pKk6ve1UkP0LWR2uHzDUMlok+Krqfe3otLViPAO1xWINJG8bMFqZBOm34ixKce6JeKQqf4b1qUmJQ0hxB61+tpLeBfIuGC2kqAfCnyPlQBMFDq+EJJmyS/GPk1PsAFpWLJ+R0bL6FWi1Fc7bM5h+wYqV/mLKaSQVPL7B4U77YSvK7lln+jMHqQGjtGH19CwIOhyeDMrceR56fOwnNrMDsDbeV2CwlJJT649M3QMDjEdf41B1UO3BkZgcSXYCDn8WoZJliG8iEfNB1MxwII2Edr/5pBumTvgZ/zhl6mS7hwVkoqthbnQWyFKMruUvyoSEoPW9HX2tX5fM0hom4J9iY4QdIoshTNtaoo2cjd4gU=' #data['SessionToken']

        if self.count > 0:
            aws_access_key_id = data['AccessKeyID']
            aws_secret_access_key = data['SecretAccessKey']
            aws_session_token = data['SessionToken']

        self.count += 1

        return Credentials(aws_access_key_id, aws_secret_access_key, aws_session_token)
