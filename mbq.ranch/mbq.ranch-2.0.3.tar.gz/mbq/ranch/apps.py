from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from mbq import metrics


class RanchConfig(AppConfig):
    name = "mbq.ranch"
    verbose_name = "Ranch"

    def ready(self):
        env = settings.RANCH.get("env")
        service = settings.RANCH.get("service")

        if not all([env, service]):
            raise ImproperlyConfigured(
                "mbq.ranch must be configured with env and service parameters."
            )

        self.module._collector = metrics.Collector(
            namespace="mbq.ranch", tags={"env": env, "service": service}
        )

        from . import signal_handlers  # noqa
