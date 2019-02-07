"""Handlers for enforcing opinionated config. Gross, but necessary."""
import copy
import logging

from django.conf import settings

from celery.signals import celeryd_init, setup_logging

from ..lib.error_handling import log_errors_and_send_to_rollbar


@celeryd_init.connect
@log_errors_and_send_to_rollbar
def enforce_app_config(sender, instance, conf, options, **kwargs):
    # acks_late is a global config setting *but* the setting is only used to determine
    # instance properties on the Tasks when they are instantiated. I couldn't find a
    # signal that'd let me alter config before the Tasks were instantiated, hence
    # the manual task modification below. We alter the config just to keep things
    # looking relatively consistent if someone comes spelunking in here later.
    conf.task_acks_late = True

    for task in instance.app.tasks.values():
        task.acks_late = True


@setup_logging.connect
@log_errors_and_send_to_rollbar
def setup_logging(loglevel, logfile, format, colorize, **kwargs):
    config = copy.copy(settings.LOGGING)
    config["disable_existing_loggers"] = False
    logging.config.dictConfig(config)
    logging.info("logging set up")
