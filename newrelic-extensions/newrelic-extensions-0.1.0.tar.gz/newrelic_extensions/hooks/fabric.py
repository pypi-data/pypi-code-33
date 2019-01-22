import importlib

from newrelic.agent import wrap_function_trace

from newrelic_extensions.hooks.base import BasePatch


class InstrumentFabric(BasePatch):
    required_modules = ['fabric.connection']

    def patch_context(self):
        module = importlib.import_module('fabric.connection')

        wrap_function_trace(module, 'Connection.run')
        wrap_function_trace(module, 'Connection.sudo')

    def instrument(self, project_packages=None):
        self.patch_context()
