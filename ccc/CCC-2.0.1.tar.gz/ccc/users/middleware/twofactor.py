# -*- coding: utf-8 -*-
import pendulum
from django.conf import settings
from django.http.response import HttpResponsePermanentRedirect
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


class TimezoneMiddleware(MiddlewareMixin):

    def process_request(self, request):
        tzname = request.session.get('django_timezone')
        if tzname:
            timezone.activate(pendulum.timezone(tzname))
        else:
            timezone.deactivate()


class TwoFactortMiddleware(MiddlewareMixin):
    """
    Middleware for two factor authentication
    """

    def process_request(self, request):
        """
        Redirect to OTP verification if user is logged in but not verified with
        OTP for current session.
        """
        is_otp_verified = str(request.COOKIES.get('opt_verified', ''))
        if is_otp_verified == "true":
            return None
        exclude_url = settings.OTP_EXCLUDE_URLS
        if settings.TEST_ENV or request.path in exclude_url or\
                str(request.path).startswith('/ccclocked'):
            return None
        elif not request.user.is_anonymous:
            return HttpResponsePermanentRedirect(settings.OTP_VERIFY_URL)
