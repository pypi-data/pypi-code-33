from types import FunctionType
from gevent.pool import Pool
from uuid import uuid1


class Engine:
    def __init__(self, name=None, pool_size=50):
        self._name = name if name else uuid1()
        self.manager_name = None
        self._pool_size = pool_size
        self._task_pool = None
        self._is_run = False
        self.redis = None
        self.tasks = []

    @property
    def name(self):
        return self._name

    @property
    def is_run(self):
        return self._is_run

    @property
    def task_count(self):
        return len(self._task_pool)

    def run(self):
        assert not self._is_run
        self._task_pool = Pool(self._pool_size)
        for task in self.tasks:
            self._task_pool.spawn(self._package_function(*task))
        self._is_run = True
        self._task_pool.join()

    def add_task(self, exe_func, *params):
        if self._is_run:
            self._task_pool.spawn(self._package_function(exe_func, *params))
        else:
            self.tasks.append((exe_func, *params))

    def _package_function(self, exe_func, *params):
        func_globals = exe_func.__globals__
        func_globals.update({'engine': self})
        execute_function = FunctionType(exe_func.__code__, func_globals, exe_func.__name__, params)
        return execute_function
