import logging
from typing import Callable

from django.conf import settings

import celery


logger = logging.getLogger(__name__)


def create_task_class(variation: Callable[[str, bool], bool]) -> celery.Task:
    class KillSwitchTask(celery.Task):
        def killswitch_name(self):
            service = settings.RANCH["service"]
            return f"task-killswitch-{service}-{self.name}".replace(".", "-").replace(
                "_", "-"
            )

        def __call__(self, *args, **kwargs):
            if variation(self.killswitch_name(), False):
                from . import _collector

                logger.info(f"Skipping task {self.name} with killswitch feature flag")
                _collector.increment("killswitch_on", tags={"task": self.name})
                return

            super().__call__(*args, **kwargs)

    return KillSwitchTask
