class LinkedinCoreException(Exception):
    pass


class ManagerNotFound(LinkedinCoreException):
    pass


class UnknownError(LinkedinCoreException):
    pass


class ExecutorError(LinkedinCoreException):
    pass


class ManagerError(LinkedinCoreException):
    pass
