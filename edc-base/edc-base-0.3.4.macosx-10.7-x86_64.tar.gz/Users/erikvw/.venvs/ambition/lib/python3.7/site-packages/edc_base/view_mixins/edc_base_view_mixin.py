from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import messages
from django.views.generic.base import ContextMixin
from django_revision.views import RevisionMixin
from django.contrib.auth.mixins import LoginRequiredMixin


class EdcBaseViewMixin(LoginRequiredMixin, RevisionMixin, ContextMixin):
    """Mixes in common template variables for the footer, etc.
    """

    def get_context_data(self, **kwargs):
        super().get_context_data(**kwargs)
        app_config = django_apps.get_app_config("edc_base")
        edc_device_app_config = django_apps.get_app_config("edc_device")
        context = super().get_context_data(**kwargs)
        try:
            live_system = settings.LIVE_SYSTEM
        except AttributeError:
            live_system = None
        try:
            sentry_dsn = settings.SENTRY_DSN
        except AttributeError:
            sentry_dsn = None
        context.update(
            {
                "copyright": app_config.copyright,
                "device_id": edc_device_app_config.device_id,
                "device_role": edc_device_app_config.device_role,
                "disclaimer": app_config.disclaimer,
                "institution": app_config.institution,
                "license": app_config.license,
                "project_name": app_config.project_name,
                "project_repo": app_config.project_repo,
                "live_system": live_system,
                "sentry_dsn": sentry_dsn,
            }
        )
        if settings.DEBUG:
            messages.add_message(
                self.request,
                messages.ERROR,
                (
                    "This EDC is running in DEBUG-mode. Use for testing only. "
                    "Do not use this system for production data collection!"
                ),
            )
        elif not settings.DEBUG and not live_system:
            messages.add_message(
                self.request,
                messages.WARNING,
                (
                    "This EDC is for testing only. "
                    "Do not use this system for production data collection!"
                ),
            )
        try:
            if settings.WARNING_MESSAGE:
                messages.add_message(
                    self.request,
                    messages.WARNING,
                    settings.WARNING_MESSAGE,
                    extra_tags="warning",
                )
        except AttributeError:
            pass
        return context
