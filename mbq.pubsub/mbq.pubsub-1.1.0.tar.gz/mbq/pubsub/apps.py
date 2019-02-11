from django.apps import AppConfig

from mbq import metrics
from mbq.pubsub.settings import project_settings


class PubSubConfig(AppConfig):
    name = "mbq.pubsub"
    verbose_name = "PubSub"

    def ready(self):
        self.module._collector = metrics.Collector(
            namespace="mbq.pubsub",
            tags={"env": project_settings.ENV.long_name, "service": project_settings.SERVICE},
        )
