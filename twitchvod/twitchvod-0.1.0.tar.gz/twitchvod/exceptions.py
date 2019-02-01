"""twitchvod exceptions.py"""

# Base errors...
class HTTPError(Exception):
    """Base HTTP Error exception"""

    def __init__(self, *args, **kwargs):
        self.http_response = kwargs.pop("http_response", None)
        super(HTTPError, self).__init__(*args, **kwargs)


# 4xx errors...
class HTTPClientError(HTTPError):
    """Client HTTP Error"""


# 5xx errors...
class HTTPServerError(HTTPError):
    """Server HTTP Error"""


# everything else...
class HTTPGenericError(HTTPError):
    """Generic HTTP Error"""
