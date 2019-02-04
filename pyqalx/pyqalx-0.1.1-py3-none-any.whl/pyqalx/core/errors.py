"""pyqalx.core.errors defines QalxError exception and a load of children.

If pyqalx is going raise an error you know about then use one of these or create a new one.

"""

class QalxError(Exception):
    """Base qalx error. Take responsibility!"""
    pass


class QalxAuthError(QalxError):
    """qalx did not find a way to authenticate or the authentication didn't work"""
    pass


class QalxNoGUIDError(QalxError):
    """A QalxEntity without a guid is like a dog without a bone."""
    pass


class QalxNoInfoError(QalxError):
    """A QalxEntity without info is like a dog without a bone."""
    pass


class QalxReturnedMultipleError(QalxError):
    """There should only be one thing. But qalx sent more than one."""
    pass


class QalxConfigProfileNotFound(QalxError):
    """The profile wasn't in the file or the file wasn't properly formed."""
    pass


class QalxConfigFileNotFound(QalxError):
    """There should be a file in the users `home` directory (either a .bots or .qalx)."""
    pass


class QalxQueueError(QalxError):
    """There wasn't the correct information to connect to the remote queue. """


class QalxBotInitialisationFailed(QalxError):
    """The bot initialisation function returned something falsey."""


class QalxEntityNotFound(QalxError):
    """We couldn't find the entity class you were looking for."""


class QalxMultipleEntityReturned(QalxError):
    """We found more than one entity, but you just wanted the one hey?"""


class QalxConfigError(QalxError):
    """Something about an attempted load of config didn't work"""


class QalxAPIResponseError(QalxError):
    """There was a problem with some kind of API request."""


class QalxEntityUnchanged(QalxError):
    """Saved something which hadn't actually been changed when we thought it had."""


class QalxNoQueueFoundByName(QalxError):
    """No qalx queue was found for the given name"""
