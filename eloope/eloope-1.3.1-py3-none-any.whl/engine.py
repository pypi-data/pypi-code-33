from gevent.pool import Pool
from uuid import uuid1


class Engine:
    def __init__(self, name=None, pool_size=50):
        self._name = name if name else uuid1()
        self.manager_name = None
        assert isinstance(pool_size, int)
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

    @property
    def pool_size(self):
        return self._pool_size

    def run(self):
        assert not self._is_run
        self._task_pool = Pool(self._pool_size)
        for task in self.tasks:
            task[0].__globals__.update({'engine': self})
            self._task_pool.spawn(*task)
        self._is_run = True
        self._task_pool.join()
        self._task_pool = None
        self._is_run = False

    def add_task(self, exe_func, *params):
        if self._is_run:
            exe_func.__globals__.update({'engine': self})
            self._task_pool.spawn(exe_func, *params)
        else:
            self.tasks.append((exe_func, *params))
