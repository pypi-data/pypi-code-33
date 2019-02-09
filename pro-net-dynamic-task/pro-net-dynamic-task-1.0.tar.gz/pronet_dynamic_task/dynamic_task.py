"""
A dynamic task is a meta object for tracking of long running algorithms.
It extends pronet_task.task.Task by the ability to dynamic load a algorithm
using importlib.
"""

from pronet_task.task import Task, State
from importlib import util


class DynamicTask(Task):
    """
    Meta data object for algorithm progress tracking with dynamic
    library loading.
    """

    def run(self):
        """
        Run the task.

        Call this method to load the library execute the algorithm.
        """
        spec = util.find_spec(self._algorithm)
        if spec is None:
            self.error("Algorithm {} not found!".format(self._algorithm))
        else:
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self._state = State.RUNNING
            try:
                module.execute(self._input, self)
            except Exception as e:
                self.error("Algorithm {} not valid!".format(self._algorithm))
