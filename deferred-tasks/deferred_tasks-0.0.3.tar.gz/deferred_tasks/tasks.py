import logging
import requests
import json
from django.core.management import call_command
from django.conf import settings

logger = logging.getLogger(__name__)


class Proxy(object):
    def __init__(self, method):
        self._method = method

    def __call__(self, *args, **kwargs):
        self._method(*args, **kwargs)

    def delay(self, *args, **kwargs):
        command_args = [
            "{}.{}".format(self._method.__module__, self._method.__name__),
            "'{}'".format(json.dumps({"args": args, "kwargs": kwargs})),
        ]

        if getattr(settings, "DEFERRED_TASKS_ALWAYS_EAGER", False):
            call_command("deferred_task", *command_args)
            logger.debug("Running method synchronously %s", self._method.__name__)
        else:
            request_kwargs = {
                "url": "https://api.heroku.com/apps/{app_name}/dynos".format(
                    app_name=settings.HEROKU_APP_NAME
                ),
                "headers": {
                    "Accept": "application/vnd.heroku+json; version=3",
                    "Authorization": "Bearer {api_key}".format(
                        api_key=settings.HEROKU_API_KEY
                    ),
                },
                "json": {
                    "size": "hobby",
                    "time_to_live": 60 * 60 * 30,  # 30 minutes before cancelling
                    "type": "run",
                    "command": "./manage.py deferred_task {}".format(
                        " ".join(command_args)
                    ),
                },
            }
            if settings.DEBUG:
                logger.debug(
                    "Mock run method asynchronously %s %s",
                    self._method.__name__,
                    json.dumps(request_kwargs),
                )
            else:
                logger.debug("Running method asynchronously %s", self._method.__name__)
                response = requests.post(**request_kwargs)
                response.raise_for_status()


def shared_task(f):
    return Proxy(f)
