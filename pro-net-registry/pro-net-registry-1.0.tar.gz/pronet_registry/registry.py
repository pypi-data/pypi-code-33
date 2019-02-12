"""
pro-net-registry provides a Registry object which allows executing of long
running algorithms.
"""

import uuid
from threading import Lock, Timer, Thread
import queue

from pronet_dynamic_task.dynamic_task import DynamicTask
from pronet_task.task import Task
from pronet_worker.worker import Worker


# Single instance of the registry
_instance = None
# Lock for registry access
_lock = Lock()


def get_registry():
    """
    Retruns the Registry instance.

    This function implements a flavour of Singleton. If no instance is
    available a new instance is created, else the existing instance is
    returned.
    """
    global _instance
    global _lock
    _lock.acquire()
    if not _instance:
        _instance = Registry()
    _lock.release()
    return _instance


def _get_updates(registry):
    """
    Implementation of the task update thread.

    This method gets all available updates from the worker and updates
    the registered task objects.
    """
    global _lock
    for id, message, progress, step in registry._worker.updates():
        if id in registry._tasks:
            _lock.acquire()
            registry._tasks[id].update(
                message=message,
                progress=progress,
                step=step)
            registry._updates[id].put((message, progress, step))
            _lock.release()


def _get_results(registry):
    """
    Implementation of the task result updater thread.

    This method gets all available results from the worker and updates
    the registered tasks.
    """
    global _lock
    for task in registry._worker.next():
        if task.id() in registry._tasks:
            _lock.acquire()
            registry._tasks[task.id()] = task
            _lock.release()


class Registry(object):
    """
    This class implements a registry for tasks, i.e. it can be used to
    create new tasks, runs these tasks using a worker process pool and
    provides a in memory storage for the results.
    """

    def __init__(self, worker=None, updates=True, results=True):
        """
        Create, register and enqueue a new static task with the given data and
        the given algorithm object.

        :param worker: worker to use, if None a new worker is created.
        :type worker: pronet_worker.worker.Worker
        :param updates: Start thread to fetch updates? Default is True
        :type updates: boolean value
        :param results: Start thread to fetch results? Default is True
        :type results: boolean value
        """
        if worker is None:
            self._worker = Worker()
        else:
            self._worker = worker
        self._tasks = {}
        self._updates = {}
        if updates:
            # thread for getting the task updates and update
            # the thread local copies
            t = Thread(target=_get_updates, daemon=True, args=(self, ))
            t.start()
        if results:
            # thread for getting the task results and update
            # the thread local copies
            t = Thread(target=_get_results, daemon=True, args=(self, ))
            t.start()

    def create_static(self, algorithm, data=None):
        """
        Create, register and enqueue a new static task with the given data and
        the given algorithm object.

        :param algorithm: Algorithm object to use.
        :type algorithm: Algorithm object or module, i.e. has to provide an
        execute function
        :param data: Input data for the algorithm.
        :type data: any object, usually a dictionary.
        """
        if algorithm:
            id = uuid.uuid4()
            task = Task(id, algorithm, data)
            self._tasks[id] = task
            self._updates[id] = queue.Queue()
            self._worker.run(task)
            return id
        return None

    def create(self, algorithm, data=None):
        """
        Create, register and enqueue a new dynamic task with the given data and
        the given algorithm object.

        :param algorithm: Algorithm module name.
        :type algorithm: The module with this name will be loaded and executed.
        :param data: Input data for the algorithm.
        :type data: any object, usually a dictionary.
        """
        if algorithm:
            id = uuid.uuid4()
            task = DynamicTask(id, algorithm, data)
            self._tasks[id] = task
            self._updates[id] = queue.Queue()
            self._worker.run(task)
            return id
        return None

    def result(self, id):
        """
        Return the result for the task with the given id.

        This method raises and Attribute error if the id is unknown.
        """
        if id in self._tasks:
            return self._tasks[id].result()
        raise AttributeError('Unknown task id!')

    def state(self, id):
        """
        Return the state for the task with the given id.

        This method raises and Attribute error if the id is unknown.
        """
        if id in self._tasks:
            return self._tasks[id].state()
        raise AttributeError('Unknown task id!')

    def delete(self, id):
        """
        Delete the task with the given id.
        """
        if id in self._tasks:
            _lock.acquire()
            self._tasks.pop(id, None)
            self._updates.pop(id, None)
            _lock.release()

    def watch(self, id, timeout=1.0):
        """
        Generator method for task updates.
        """
        while id in self._tasks and self._tasks[id].running():
            try:
                yield self._updates[id].get(block=True, timeout=timeout)
            except queue.Empty:
                # used to check if task is still running
                pass
