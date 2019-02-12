import functools
import time

from django.db import connections
from django.db.migrations.executor import MigrationExecutor

from .settings import project_settings


_DB_READY = {}


def construct_full_queue_name(queue_name):
    return f"mbq-{project_settings.SERVICE}-{queue_name}-{project_settings.ENV.short_name}"


def debounce(seconds=None, minutes=None, hours=None):
    def wrapper(func):
        func.seconds_between_runs = 0
        func.last_run = time.time()

        if seconds:
            func.seconds_between_runs += seconds
        if minutes:
            func.seconds_between_runs += minutes * 60
        if hours:
            func.seconds_between_runs += hours * 60 * 60

        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            if func.last_run + func.seconds_between_runs < time.time():
                func(*args, **kwargs)
                func.last_run = time.time()

        return wrapped_func

    return wrapper


def is_db_ready(database="default"):
    """Determine whether the migrations for pubsub are up to date. Can
    be used to defer hitting the database until everything is ready.

    Implementation is inspired by the `./manage.py migrate --plan` command:

       https://github.com/django/django/blob/master/django/core/management/commands/migrate.py#L140-L150
    """
    global _DB_READY

    if not _DB_READY.get(database, False):
        executor = MigrationExecutor(connections[database])
        # find the pubsub migrations
        pubsub_migrations = [
            node for node in executor.loader.graph.leaf_nodes() if node[0] == "pubsub"
        ]
        # build a plan to run all the migrations
        plan = executor.migration_plan(pubsub_migrations)
        # if there's no plan then we're fully up to date
        _DB_READY[database] = not bool(plan)

    return _DB_READY[database]
