from functools import wraps

from tornado.web import HTTPError


def authenticated(method):
    """
    Decorate methods with this to require that the user be logged in.
    If user is not logged in, HTTP 401 is sent
    :param method: method to decorate
    :return: wrapper
    """

    @wraps(method)
    def wrapper(inst, *args, **kwargs):
        if not inst.current_user:
            raise HTTPError(401, 'Authentication failed')
        return method(inst, *args, **kwargs)

    return wrapper
