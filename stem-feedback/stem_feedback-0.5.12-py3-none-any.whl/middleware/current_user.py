from threading import local

_user = local()


class CurrentUserMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _user.value = request.user
        return self.get_response(request)


def value():
    try:
        return _user.value
    except (Exception,):
        return None


def is_user_request():
    try:
        return _user.request_change
    except (Exception,):
        return False


def get_current_user():
    try:
        return _user.value.username
    except (Exception,):
        return ''
