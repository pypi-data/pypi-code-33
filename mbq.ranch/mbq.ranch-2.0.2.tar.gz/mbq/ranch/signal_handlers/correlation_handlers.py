from django.conf import settings

from celery.signals import before_task_publish, task_prerun

from ..lib.error_handling import log_errors_and_send_to_rollbar


CORRELATION_SETTINGS = settings.RANCH.get("correlation", {})
CORRELATION_ID_GETTER = CORRELATION_SETTINGS.get("getter", lambda: None)
CORRELATION_ID_SETTER = CORRELATION_SETTINGS.get("setter", lambda value: None)


@before_task_publish.connect
@log_errors_and_send_to_rollbar
def add_correlation_id_to_headers(
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
    correlation_id = CORRELATION_ID_GETTER()
    if correlation_id:
        headers["__RANCH_CORRELATION_ID"] = correlation_id


@task_prerun.connect
@log_errors_and_send_to_rollbar
def set_correlation_id_from_headers(sender, task_id, task, **kwargs):
    correlation_id = getattr(task.request, "__RANCH_CORRELATION_ID", None)
    if correlation_id:
        CORRELATION_ID_SETTER(correlation_id)
