import importlib

from newrelic.agent import application, BackgroundTask, wrap_background_task, wrap_function_trace
from newrelic.common.object_names import callable_name
from newrelic.common.object_wrapper import wrap_function_wrapper
from pike.discovery import py

from newrelic_extensions.hooks.base import BasePatch


def wrap_task(wrapped, instance, args, kwargs):
    task, *_ = args
    task_name = callable_name(task)
    app = application()

    with BackgroundTask(app, task_name):
        return wrapped(*args, **kwargs)


class InstrumentZag(BasePatch):
    required_modules = ['zag']

    def patch_zag_engine(self):
        module = importlib.import_module('zag.engines.action_engine.executor')

        wrap_function_wrapper(module, '_execute_task', wrap_task)
        wrap_function_wrapper(module, '_revert_task', wrap_task)


    def patch_zag_tasks_in_projects(self, project_packages):
        task_module = importlib.import_module('zag.task')

        to_patch = [
            cls
            for package in project_packages
            for child in py.get_child_modules(py.get_module_by_name(package))
            for cls in py.get_all_inherited_classes(child, task_module.Task)
        ]

        for cls in to_patch:
            module = py.get_module_by_name(cls.__module__)
            wrap_function_trace(module, '{0}.pre_execute'.format(cls.__name__))
            wrap_function_trace(module, '{0}.execute'.format(cls.__name__))
            wrap_function_trace(module, '{0}.post_execute'.format(cls.__name__))
            wrap_function_trace(module, '{0}.pre_revert'.format(cls.__name__))
            wrap_function_trace(module, '{0}.revert'.format(cls.__name__))
            wrap_function_trace(module, '{0}.post_revert'.format(cls.__name__))

    def instrument(self, project_packages=None):
        self.patch_zag_engine()
        self.patch_zag_tasks_in_projects(project_packages or [])
