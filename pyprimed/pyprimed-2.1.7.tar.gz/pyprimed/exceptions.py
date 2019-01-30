# -*- coding: utf-8 -*-


class ConnectionFailedError(Exception):
    pass


class MethodNotAllowedExpection(Exception):
    pass


class RemoteMethodNotAllowedExpection(Exception):
    pass


class UnknownRemoteExpection(Exception):
    pass


class AuthenticationError(Exception):
    pass


class AuthorizationError(Exception):
    pass


class ResourceNotExistsError(Exception):
    pass


class ServerError(Exception):
    pass
