# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.


class CloudVolumesError(Exception):
    pass


class ConnectionError(CloudVolumesError):
    pass


class AuthenticationError(CloudVolumesError):
    pass


class RateLimitingError(CloudVolumesError):
    pass


class APIError(CloudVolumesError):
    pass


class InternalError(APIError):
    pass
