import json
from importlib import import_module

from .exceptions import TaskNotFound
from .models import LoggedTask


def persist_task(
    task_id, queue, task_name, args, kwargs, stacktrace, status, rollbar_uuid
):
    return LoggedTask.objects.create(
        id=task_id,
        queue=queue,
        task_name=task_name,
        args=json.dumps(args),
        kwargs=json.dumps(kwargs),
        stacktrace=stacktrace,
        status=status,
        rollbar_occurrence=rollbar_uuid,
    )


def rerun_logged_task(logged_task):
    task_name = logged_task.task_name.split(".")[-1]
    module_path = logged_task.task_name.replace(".{}".format(task_name), "")

    module = import_module(module_path)
    task_func = getattr(module, task_name, None)

    if task_func is None:
        raise TaskNotFound()

    args = json.loads(logged_task.args)
    kwargs = json.loads(logged_task.kwargs)
    task_func.delay(*args, **kwargs)
    logged_task.delete()
