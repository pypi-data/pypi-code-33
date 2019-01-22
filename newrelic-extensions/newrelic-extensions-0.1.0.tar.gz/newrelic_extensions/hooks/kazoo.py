import importlib

from newrelic.common.object_wrapper import wrap_function_wrapper
from newrelic.api.datastore_trace import DatastoreTrace
from newrelic.api.transaction import current_transaction

from newrelic_extensions.hooks.base import BasePatch


def wrap_kazoo(wrapped, instance, args, kwargs):
    transaction = current_transaction()
    host, port, db = (None, None, None)
    operation = wrapped.__name__

    if transaction is None or not args:
        return wrapped(*args, **kwargs)

    if instance._connection and instance._connection._socket:
        host, port = instance._connection._socket.getsockname()

    with DatastoreTrace(
            transaction,
            product='Zookeeper',
            target=None,
            operation=operation,
            host=host,
            port_path_or_id=port,
            database_name=db):
        return wrapped(*args, **kwargs)


class InstrumentKazoo(BasePatch):
    required_modules = ['kazoo.client']

    def patch_client(self):
        module = importlib.import_module('kazoo.client')

        wrap_function_wrapper(module, 'KazooClient.get', wrap_kazoo)
        wrap_function_wrapper(module, 'KazooClient.set', wrap_kazoo)
        wrap_function_wrapper(module, 'KazooClient.exists', wrap_kazoo)

    def instrument(self, project_packages=None):
        self.patch_client()
