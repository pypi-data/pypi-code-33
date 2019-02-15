import threading
import time
from collections import Counter

from django.conf import settings

import arrow
from celery.signals import (
    after_task_publish,
    before_task_publish,
    celeryd_after_setup,
    heartbeat_sent,
    task_failure,
    task_postrun,
    task_prerun,
    task_retry,
    task_success,
    task_unknown,
)

from .. import _collector
from ..lib.error_handling import log_errors_and_send_to_rollbar
from ..models import LoggedTask
from ..stats.rabbitmq import send_rabbitmq_queue_stats


local = threading.local()

HEARTBEAT_METRICS_INTERVAL_SECONDS = 30
EXTRA_ERROR_QUEUE_TAGS_FN = settings.RANCH.get(
    "extra_error_queue_tags_fn", lambda task: []
)


@before_task_publish.connect
@log_errors_and_send_to_rollbar
def add_metadata_to_task_headers(
    sender,
    body,
    exchange,
    routing_key,
    headers,
    properties,
    declare,
    retry_policy,
    **kwargs
):
    queued_at = arrow.get(headers.get("eta")).timestamp
    headers["__RANCH_QUEUED_AT"] = queued_at


@after_task_publish.connect
@log_errors_and_send_to_rollbar
def send_metrics_on_publish(sender, headers, body, exchange, routing_key, **kwargs):
    _collector.increment(
        "task.publish", value=1, tags={"task": headers.get("task", "unknown")}
    )


@task_prerun.connect
@log_errors_and_send_to_rollbar
def store_metadata_before_task_runs(
    sender, task_id, task, args, kwargs, **extra_kwargs
):
    local.task_received_at = time.time()
    try:
        local.task_queue = task.request.delivery_info.get("routing_key")
    except Exception:
        local.task_queue = None

    queued_at = getattr(task.request, "__RANCH_QUEUED_AT", None)
    if queued_at:
        wait_time_ms = (time.time() - queued_at) * 1000
        _collector.timing(
            "task.wait_time",
            value=wait_time_ms,
            tags={"task": task.name, "queue": local.task_queue},
        )


@task_postrun.connect
@log_errors_and_send_to_rollbar
def send_metrics_after_task_runs(
    sender, task_id, task, args, kwargs, retval, state, **extra_kwargs
):
    execution_time_ms = (time.time() - local.task_received_at) * 1000
    _collector.timing(
        "task.execution_time",
        value=execution_time_ms,
        tags={"task": task.name, "state": state, "queue": local.task_queue},
    )


def _send_task_processed_metric(task_name, result):
    _collector.increment(
        "task.processed",
        value=1,
        tags={"task": task_name, "result": result, "queue": local.task_queue},
    )


@task_retry.connect
@log_errors_and_send_to_rollbar
def send_metrics_on_task_retry(sender, request, reason, einfo, **kwargs):
    _send_task_processed_metric(sender.name, "retry")


@task_success.connect
@log_errors_and_send_to_rollbar
def send_metrics_on_task_success(sender, result, *args, **kwargs):
    _send_task_processed_metric(sender.name, "success")


@task_failure.connect
@log_errors_and_send_to_rollbar
def send_metrics_on_task_failure(
    sender, task_id, exception, args, kwargs, traceback, einfo, **extra_kwargs
):
    _send_task_processed_metric(sender.name, "failure")


@task_unknown.connect
@log_errors_and_send_to_rollbar
def send_metrics_on_task_unknown(sender, name, id, message, exc, **kwargs):
    _collector.increment("task.unknown", value=1, tags={"task": name})


@celeryd_after_setup.connect
@log_errors_and_send_to_rollbar
def store_metadata_on_worker_start(sender, instance, conf, **kwargs):
    local.worker_instance = instance
    local.app_config = conf

    # worker_queues is a dict of queue name to Celery queue instance, for
    # all queues this worker is configured to process
    # Don't freak out about the variable named amqp, yes it is
    # called this even if you're using Redis. Celery is jank.
    local.worker_queues = instance.app.amqp.queues

    # broker_type is a string, "amqp" or "redis" (or others but these
    # are the ones we expect to use)
    local.broker_type = instance.app.broker_connection().transport_cls

    local.last_send_on_heartbeat = 0


def _send_queue_length_metrics():
    if local.broker_type == "amqp":
        send_rabbitmq_queue_stats(
            local.app_config["broker_url"], list(local.worker_queues.keys())
        )


def _error_queue_tags(task):
    tags = ["queue:{}".format(task.queue), "task:{}".format(task.task_name)]
    tags.extend(EXTRA_ERROR_QUEUE_TAGS_FN(task))
    return tuple(tags)


def _send_error_queue_metrics():
    tasks = LoggedTask.objects.all()
    counts = Counter(_error_queue_tags(task) for task in tasks)

    for tags, count in counts.items():
        _collector.gauge("queue.errors.length", value=count, tags=tags)


@heartbeat_sent.connect
@log_errors_and_send_to_rollbar
def send_queue_metrics_on_heartbeat(sender, **kwargs):
    if time.time() - HEARTBEAT_METRICS_INTERVAL_SECONDS < local.last_send_on_heartbeat:
        return

    _send_queue_length_metrics()
    _send_error_queue_metrics()

    local.last_send_on_heartbeat = time.time()
