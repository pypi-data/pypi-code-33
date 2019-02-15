import traceback as traceback_stdlib

import rollbar
from celery.signals import task_failure, task_unknown

from ..constants import TaskStatus
from ..controllers import persist_task
from ..lib.error_handling import log_errors_and_send_to_rollbar


@task_failure.connect
@log_errors_and_send_to_rollbar
def handle_task_failure(
    sender, task_id, exception, args, kwargs, traceback, einfo, **extra_kwargs
):
    rollbar_uuid = rollbar.report_exc_info(extra_data=extra_kwargs)
    try:
        persist_task(
            task_id,
            sender.request.delivery_info.get("routing_key"),
            sender.name,
            args,
            kwargs,
            traceback_stdlib.format_exc(),
            TaskStatus.FAILURE,
            rollbar_uuid,
        )
    except Exception:
        # If anything goes wrong persisting the task to the DB,
        # we put it back in the Celery queue so that it is not
        # permanently lost. If that also fails, we should be
        # saved by acks_late=True since the original job
        # can only be acknowledged if we can still talk to Rabbit.
        sender.retry(countdown=60)


@task_unknown.connect
@log_errors_and_send_to_rollbar
def handle_task_unknown(sender, name, id, message, exc, **kwargs):
    rollbar_uuid = rollbar.report_exc_info(extra_data=kwargs)
    try:
        queue = message.delivery_info.get("routing_key", "unknown")
    except Exception:
        queue = "unknown"

    persist_task(
        id,
        queue,
        name,
        message.payload[0],
        message.payload[1],
        traceback_stdlib.format_exc(),
        TaskStatus.UNKNOWN,
        rollbar_uuid,
    )
