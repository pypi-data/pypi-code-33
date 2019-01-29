from functools import wraps

from django.http import HttpResponse, HttpResponseBadRequest


def ajax_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.is_ajax():
            return func(request, *args, **kwargs)
        return HttpResponseBadRequest()

    return wrapper


def login_required_ajax(the_func):
    def _decorated(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponse('You are not logged in or your session has expired! Please log in again!', status=401)
        return the_func(request, *args, **kwargs)
    return _decorated
