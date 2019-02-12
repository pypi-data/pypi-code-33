import logging
import signal

import django
from django.core.management.base import BaseCommand, CommandParser
from django.db import close_old_connections

import arrow
import rollbar
from mbq.pubsub import _collector as collector
from mbq.pubsub import models, utils
from mbq.pubsub.settings import project_settings


logger = logging.getLogger(__name__)


class SignalHandler:
    def __init__(self):
        self._interrupted = False

    def handle_signal(self, *args, **kwargs):
        self._interrupted = True

    def should_continue(self):
        return not self._interrupted


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signal_handler = SignalHandler()
        signal.signal(signal.SIGINT, self.signal_handler.handle_signal)
        signal.signal(signal.SIGTERM, self.signal_handler.handle_signal)
        signal.signal(signal.SIGQUIT, self.signal_handler.handle_signal)

    def add_arguments(self, parser):
        # django fixed a long-standing annoyance in 2.1 so we only
        # need this hack if we're using a version before that.
        # SubParser inspired by:
        # https://stackoverflow.com/a/37414551/305736
        add_parsers_kwargs = {}
        if django.VERSION < (2, 1):
            command = self

            class SubParser(CommandParser):
                def __init__(self, **kwargs):
                    return super().__init__(command, **kwargs)

            add_parsers_kwargs["parser_class"] = SubParser

        queue_choices = sorted(project_settings.QUEUES)

        subparsers = parser.add_subparsers(dest="command", **add_parsers_kwargs)
        # we should be able to pass this to .add_subparsers above but
        # that kwarg is broken in Python 3.6
        subparsers.required = True

        consume_parser = subparsers.add_parser("consume")
        consume_parser.add_argument("-q", "--queue", required=True, choices=queue_choices)

        replay_parser = subparsers.add_parser("replay")
        replay_parser.add_argument("-q", "--queue", required=True, choices=queue_choices)
        replay_parser.add_argument("num_messages", type=int)

    def handle(self, **options):
        getattr(self, f'handle_{options["command"]}')(**options)

    def handle_consume(self, queue=None, **options):
        try:
            consumer = project_settings.CONSUMER_CLASS(
                queue,
                project_settings.MESSAGE_HANDLERS,
                default_handler=project_settings.DEFAULT_HANDLER,
            )
            while self.signal_handler.should_continue():
                consumer.process_queue()
                if project_settings.USE_DATABASE:
                    if utils.is_db_ready():
                        consumer.process_dead_letter_queue()
                        self._send_dlq_metrics(queue)
                        self._delete_old_dlq_messages(queue)
                    else:
                        logger.info(
                            "Database is not ready. Skipping processing the DLQ and collecting metrics."
                        )

            # django only cleans up db connections when handling the "request_finished" signal
            # so we want to make sure it happens regularly here in the long-lived consumer
            close_old_connections()
        except Exception:
            logger.exception("Consume failed")
            rollbar.report_exc_info()

    def handle_replay(self, queue=None, num_messages=None, **options):
        consumer = project_settings.CONSUMER_CLASS(
            queue,
            project_settings.MESSAGE_HANDLERS,
            default_handler=project_settings.DEFAULT_HANDLER,
        )
        consumer.replay_dead_letter_queue(num_messages)

    def _send_dlq_metrics(self, queue):
        collector.gauge(
            "consumer.undeliverable_messages.total",
            models.UndeliverableMessage.objects.filter(queue=queue).count(),
            tags={"queue": queue},
        )

    @utils.debounce(minutes=15)
    def _delete_old_dlq_messages(self, queue):
        days_ago_30 = arrow.utcnow().shift(days=-30)
        models.UndeliverableMessage.objects.filter(
            queue=queue, created_at__lte=days_ago_30.datetime
        ).delete()
