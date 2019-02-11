"""
A Worker is a process pool for executing pro-net-tasks.
"""


import multiprocessing
import os


def _runner(tasks, results, updates, single_task=False):
    """
    This runner is used by the pool processes to
    run the tasks.

    :param results: The queue for the finished task objects.
    :type results: multiprocessing.Queue
    :param updates: The queue for the task progress updates.
    :type updates: multiprocessing.Queue
    """
    while True:
        task = tasks.get(True)
        try:
            if task:
                task.set_update_queue(updates)
                task.run()
        except:
            if task:
                # finish task with error message in
                # case of exceptions
                task.error('Exception occurred!')
        finally:
            if task:
                # the update queue must be removed before
                # giving the executed task back.
                task.set_update_queue(None)
                results.put(task)
            tasks.task_done()
        if single_task:
            break


class Worker(object):
    """
    A worker is a process pool for executing tasks.
    """

    def __init__(self, runner=_runner, pool=None):
        """
        Create a new process pool and the required Queues.

        The process count is twice the CPU core count.
        """
        self._queue = multiprocessing.JoinableQueue()
        self._results = multiprocessing.SimpleQueue()
        self._updates = multiprocessing.SimpleQueue()
        self._done = []
        count = multiprocessing.cpu_count() * 2
        if pool is not None:
            self._pool = pool
        else:
            self._pool = multiprocessing.Pool(count, runner, (
                self._queue,
                self._results,
                self._updates))
        self._run = True

    def run(self, task):
        """
        Queue the given task and run as soon as possible.
        """
        self._queue.put(task)

    def add(self, tasks):
        """
        Queue all given task and run as soon as possible.
        """
        for t in tasks:
            self._queue.put(t)

    def join(self):
        """
        Finish all tasks in the queue and shut down the pool.
        """
        self._run = False
        self._queue.close()
        self._queue.join()
        self._pool.terminate()
        self._pool.join()

    def results(self):
        """
        Get list of all already finished tasks.
        """
        while not self._results.empty():
            self._done.append(self._results.get())
        return self._done

    def next(self):
        """
        Iterator for finished tasks.
        """
        for r in self._done:
            yield r
        while self._results_pending():
            r = self._results.get()
            self._done.append(r)
            yield r

    def _results_pending(self):
        """
        Check if there are more pending results.

        As long as the pool is running this is always True.
        It gets False if the pool is shutdown and no more results
        pending in the result queue.
        """
        if self._run:
            return True
        elif not self._results.empty():
            return True
        else:
            return False

    def updates(self):
        """
        Iterator for task updates.
        """

        while self._updates_pending():
            yield self._updates.get()

    def _updates_pending(self):
        """
        Check if there are more pending updates.

        As long as the pool is running this is always True.
        It gets False if the pool is shutdown and no more updates
        pending in the update queue.
        """
        if self._run:
            return True
        elif not self._updates.empty():
            return True
        else:
            return False
