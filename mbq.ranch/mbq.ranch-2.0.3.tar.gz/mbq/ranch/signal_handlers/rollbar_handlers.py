import rollbar
from celery.signals import task_rejected

from ..lib.error_handling import log_errors_and_send_to_rollbar


@task_rejected.connect
@log_errors_and_send_to_rollbar
def handle_task_rejected(**kw):
    rollbar.report_exc_info(extra_data=kw)
