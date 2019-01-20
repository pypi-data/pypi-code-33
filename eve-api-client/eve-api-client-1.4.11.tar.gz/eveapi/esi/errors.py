class ESIErrorLimitReached(Exception):
    error = 'ESI error limit hit, please wait'

    def __init__(self, remaining_time):
        self.remaining_time = remaining_time


class ESIPermissionRevoked(Exception):
    error = 'Character refresh token was revoked'


class ESIPageCacheRefresh(Exception):
    error = "Current page expiration does not match the first page's expiration, retrying original request"
