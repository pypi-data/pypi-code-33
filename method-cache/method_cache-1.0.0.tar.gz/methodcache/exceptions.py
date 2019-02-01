

class GeneralMethodCacheException(Exception):
    """
        General MethodCache Exception
    """
    pass


class NoMethod(GeneralMethodCacheException):
    """
        Raised when Method not registered in Cache
    """

    pass


class TTLExpired(GeneralMethodCacheException):
    """
    Raised when TTL of an MethodObject are expired
    """
    pass