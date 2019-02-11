
from django.conf import settings
from django.template.response import TemplateResponse
from django.urls import resolve


class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if settings.MAINTENANCE_MODE:
            if not request.user.is_superuser:
                if not resolve(request.path).app_name == 'admin':
                    return TemplateResponse(request, 'site/maintenance.html', {})
