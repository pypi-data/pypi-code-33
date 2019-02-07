from django.http.response import HttpResponseRedirect
from django.conf import settings

from tradenity import Configuration
from tradenity.exceptions import SessionExpiredException


def reset_session():
    Configuration.AUTH_TOKEN_HOLDER.reset()
    return HttpResponseRedirect("/")


class SessionExpiryHandlerMiddleware(object):

    def process_exception(self, request, exception):
        if isinstance(exception, SessionExpiredException):
            if hasattr(settings, 'on_session_expiry') and callable(settings.on_session_expiry):
                return settings.on_session_expiry()
            else:
                return reset_session()
