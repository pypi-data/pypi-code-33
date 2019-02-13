from tagliatelle.ClientRequest import ClientRequest


class Client:
    """Main class of the high level tagging client built on top of Tagliatelle API"""

    def __init__(self, access_token, url_override):
        self.accessToken = access_token
        self.urlOverride = url_override

    def tag(self):
        return ClientRequest(self.accessToken, self.urlOverride)
