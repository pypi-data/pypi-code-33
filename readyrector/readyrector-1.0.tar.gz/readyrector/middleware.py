from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models.expressions import F
from django.db.models.query_utils import Q
from django.http.response import HttpResponseRedirect
from django.urls import Resolver404, resolve
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from . import models


class RedirectDatabaseMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        if response.status_code != 404:
            return response

        path = request.path_info.strip('/')
        redirect_obj = models.Redirect.objects.filter(
            Q(from_path=path) | Q(from_path=f'{path}/')
        ).first()

        if redirect_obj:
            redirect_obj.hits = F('hits') + 1
            redirect_obj.last_hit = timezone.now()
            redirect_obj.save(update_fields=('hits', 'last_hit'))
            return HttpResponseRedirect(redirect_obj.to_url)

        return response


class RedirectURLConfMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        if response.status_code != 404:
            return response

        path = request.path_info
        redirect_urls = getattr(settings, 'READYRECTOR_URLCONF', '')

        if not redirect_urls:
            raise ImproperlyConfigured(
                'Setting READYRECTOR_URLCONF is not set or empty.')

        try:
            resolved_url = resolve(path, redirect_urls)
            return resolved_url.func(
                request, *resolved_url.args, **resolved_url.kwargs)
        except Resolver404:
            if settings.APPEND_SLASH and not request.path.endswith('/'):
                try:
                    resolved_url = resolve(f'{path}/', redirect_urls)
                    return resolved_url.func(
                        request, *resolved_url.args, **resolved_url.kwargs)
                except Resolver404:
                    pass

        return response
