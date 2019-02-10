import sys

from threading import Event, Lock, Thread
from queue import Queue, Full
from math import ceil

from bgez.core.utils.time import elapsed_time
from bgez.core.events import Subject
from bgez import logger

UNRESOLVED = object()

class TaskManagerState:
    '''Simple class defining the possible states of a TaskManager.'''

    CLOSED = 0
    CLOSING = 1
    WORKING = 2

    state_to_str = {
        CLOSED : "closed",
        CLOSING : "closing",
        WORKING : "working",
    }

class Result:
    '''
    An object returned immediately after a task was added in the a TaskManager and is resolved
    later by a Worker. On resolving, the Result calls the optionnal callback with itself as only
    argument if one was set. This callback is either set at creation in the TaskManager or by
    calling set_callback() on the Result object itself. Its value property is a ResultPromise
    object until it's resolved.
    '''

    def __init__(self, callback=None):
        self._value = UNRESOLVED
        self._done = Event()
        self._callback = callback

    def is_resolved(self):
        '''Returns whether the .'''
        return self._value is not UNRESOLVED

    def wait_value(self, timeout=None):
        '''
        Blocks until the Result is resolved or the timeout occurs, in which case a TimeoutError
        exception is raised.
        '''
        res = self._done.wait(timeout)
        if not res:
            raise TimeoutError(f"A wait() call timed out. Used timeout: {timeout}")
        return self.value

    def set_callback(self, callback):
        '''
        Sets the Result object's callback to the given callback which must be a callable or else
        a ValueError exception is raised. If a callback is set or changed after the Result is
        resolved, it will immediately be called. This callback must have only one argument, a
        Result object.
        '''
        if not callable(callback):
            raise ValueError("Can't use a non-callable as callback.")
        self._callback = callback
        if self._done.is_set():
            self._callback(self)
    then = set_callback

    def _resolve(self, work_result):
        '''Resolves the Result with work_result.'''
        self._value = work_result
        self._done.set()

    def __repr__(self):
        state = "unresolved" if self._value is UNRESOLVED else "resolved"
        return f"<{self.__class__.__name__} object [{state}]>"

    @property
    def value(self):
        if isinstance(self._value, Exception):
            raise self._value
        return self._value

class Worker:
    '''
    A thread wrapper made to work alongside a TaskManager, but can be individually used.
    At creation, takes a Queue instance as task_queue and starts running right away. It gets
    a task from the queue, runs it and, if provided, calls the callback with result as only
    argument. A task is valid if it's a list respecting the following patern:
    - [callback, function_to_run, *args, **kargs]
    Any task disrespecting this patern might cause unexpected behaviours, except for one, a
    None task, which makes the Worker exit and become unusable.
    '''

    def __init__(self, task_queue):
        self._available = False
        self._task_queue = task_queue
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()

    def is_alive(self):
        '''Returns whether the underlying Thread is still alive (running the Worker run()).'''
        return self._thread.is_alive()

    def join(self, timeout=None):
        '''
        Blocks until the underlying Thread is stopped or a timeout occurs. Returns whether
        the underlying Thread is stopped.
        '''
        self._thread.join(timeout)
        return not self.is_alive()

    def _run(self):
        '''
        The method that will be executed by the underlying Thread. If an exception occured,
        the exception object is given as result to the callback, otherwise it's re-raised.
        When exited, the underlying Thread finishes and the Worker becomes unsuables.
        '''
        while True:
            self._available = True
            task = self._task_queue.get()
            self._available = False

            if task is None:
                return self._task_queue.task_done()
            callback, func, args, kargs = task

            try:
                result = func(*args, **kargs)
            except Exception as error:
                if callback is None:
                    logger.exception("", exc_info=error)
                result = error

            if callback is not None:
                callback(result)
            self._task_queue.task_done()

    def __repr__(self):
        alive = "alive" if self.is_alive() else "stopped"
        available = "available" if self._available else "unavailable"
        return f"<{self.__class__.__name__} [{alive} & {available}]>"

    @property
    def is_available(self):
        '''Returns whether the Worker is available for work or if it's running.'''
        return self._available

class TaskManager:
    '''
    A TaskManager dispatches tasks amongst his Workers. It uses pool_size Workers and can
    queue tasks up to max_tasks_queued. Once set, these parameters can't be changed, you would
    need to create a new TaskManager. For examples, see taskmanager_test.py.
    '''

    def __init__(self, pool_size=5, max_tasks_queued=10):
        super().__init__()
        self.lock = Lock()
        self.on_close = Subject()
        self._pool_size = pool_size

        self._callback_queue = Queue()
        self._state = TaskManagerState.WORKING
        self._max_tasks_queued = max_tasks_queued

         # The actual queue size is bigger to keep room for one exit task per Worker
        self._task_queue = Queue(max_tasks_queued + pool_size)
        self._workers = self._create_workers()
        self._tasks_planned = 0

    def as_task(self, callback=None):
        '''
        Used as decorator when a TaskManager is already available. Can take a callable as argument
        and adds a task using add_task. See add_task for more details.
        '''
        def tasked(func):
            def task_wrapper(*args, **kargs):
                return self.add_task(func, *args, callback=callback, **kargs)
            return task_wrapper
        return tasked

    def add_task(self, func_to_run, *args, callback=None, **kargs):
        '''
        Adds the given func_to_run as a task to be run with given args and kargs and immediately
        returns a Result object. On task's end, the Result object's value is set and the callback
        added to the callback list. This callback can be set or changed later via the Result object's
        set_callback() method. Can raise a Full exception if the task-queue is full or a ValueError
        exception if the given callback is neither a callable nor None.
        Note: The given callback won't be asynchronously by the Worker, but by the TaskManager
        when its method process() is called.
        '''
        if self._task_queue.qsize() >= self._max_tasks_queued:
            raise Full("The task queue is already full, can't add more tasks.")
        if callback is not None and not callable(callback):
            raise ValueError("A task's callback must be a callable or None.")

        with self.lock:
            self._tasks_planned += 1
        result_obj = Result(callback)

        # Worker's callback
        def run_async(res):
            with self.lock:
                self._tasks_planned -= 1
            result_obj._resolve(res)
            if callback is not None:
                # Register the user-defined callback to be called by the TaskManager process
                self._callback_queue.put_nowait((callback, result_obj))

        task = [run_async, func_to_run, args, kargs]
        self._task_queue.put_nowait(task)
        return result_obj

    def close(self, timeout=None):
        '''
        Puts an exit task in the task-queue for every Worker. Workers will have to consume the
        whole task-queue until they find an exit task. Any further task added after this call
        won't be executed as the Workers will be done consuming tasks.
        - Returns True if timeout is None or all threads or if all Workers are stopped.
        - Returns False if not all Workers were stopped before timeout.
        '''
        if self._state == TaskManagerState.CLOSED or self._state == TaskManagerState.CLOSING:
            logger.warning("Close attempt on a closing or already closed TaskManager.")
            return True

        self._state = TaskManagerState.CLOSING
        for i in range(self._pool_size):
            self._task_queue.put(None)

        if timeout is not None:
            for worker in self._workers:
                elapsed, stopped = elapsed_time(worker.join, timeout)
                timeout = max(timeout - elapsed, 0)
                if not stopped:
                    if timeout == 0:
                        return False
            self._state = TaskManagerState.CLOSED
        return True

    def __call__(self):
        '''Calls every registered user-defined callback. Needs to be called by the mainloop.'''
        while not self._callback_queue.empty():
            callback, result = self._callback_queue.get_nowait()
            callback(result)
            self._callback_queue.task_done()

        if self.closed:
            self._state = TaskManagerState.CLOSED
            self.on_close.notify(self)

    def _create_workers(self):
        '''Instanciates and stores a Worker object according to pool_size .'''
        return [Worker(self._task_queue) for _ in range(self._pool_size)]

    def __repr__(self):
        return f"<{self.__class__.__name__} [{TaskManagerState.state_to_str[self._state]}] pool_size={self._pool_size}>"

    @property
    def pool_size(self):
        '''Returns the number of Workers the TaskManager is managing.'''
        return self._pool_size

    @property
    def max_tasks_queued(self):
        '''Returns the maximum number of tasks that can be queued before the queue overflows.'''
        return self._max_tasks_queued

    @property
    def state(self):
        '''Returns the current state of the task manager.'''
        return self._state

    @property
    def closed(self):
        '''Equivalent to checking whether the TaskManager's state is CLOSED.'''
        return self._state == TaskManagerState.CLOSED or \
            all(not worker.is_alive() for worker in self._workers)

    @property
    def available_workers(self):
        '''Returns the number of workers available for work.'''
        return max(self._pool_size - self._tasks_planned, 0)
