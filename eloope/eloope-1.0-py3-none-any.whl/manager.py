from redis.exceptions import ResponseError
from multiprocessing import Process
from .task_queue import TaskQueue
from pickle import loads, dumps
from types import MethodType
from .engine import Engine
from redis import Redis
from uuid import uuid1
from time import sleep
import gevent


class Manager:
    def __init__(self, name=None, host='localhost', port=6379):
        self._name = name if name else uuid1()
        self._redis_config = (host, port)
        self.processes = []
        self._redis = Redis(*self._redis_config, decode_responses=True)

    @property
    def name(self):
        return self._name

    def add_processes(self, *engines):
        self.processes.extend(engines)

    def add_engines(self, *engine_names):
        self.processes.extend([Engine(name=name) for name in engine_names])

    def start(self):
        assert self.processes
        pipe = self._redis.pipeline()
        for engine in self.processes:
            pipe.hsetnx(f'manager-{self.name}', engine.name, 'Ready')  # todo: name 相同时异常处理
        pipe.execute()

        while True:
            is_run = self._redis.get('is_run')
            if is_run == '1':
                for engine in self.processes:
                    Process(target=_create_process, args=(engine, self._redis_config, self.name)).start()
                break
            sleep(0.5)

        while True:
            pipe.get('is_run')
            pipe.hgetall(f'manager-{self.name}')
            for engine in self.processes:
                pipe.scard(engine.name)
            is_run, engine_status, *engines_task_count = pipe.execute()
            for engine, engine_task_count in zip(self.processes, engines_task_count):
                if engine_status[engine.name] == 'Done' and engine_task_count > 0:
                    Process(target=_create_process, args=(engine, self._redis_config, self.name)).start()

            if is_run == '-1':
                break
            sleep(0.5)

    def add_task(self, engine_name, exe_func, *params):
        assert self.processes, 'Engine is not exits!'
        for engine in self.processes:
            if engine.name == engine_name:
                engine.add_task(exe_func, *params)
                break
        else:
            raise Exception('Engine is not exits!')


def _create_process(engine, redis_config, manager_name):
    redis = Redis(*redis_config)
    redis.hset(manager_name, engine.name, 'Running')
    engine.redis = redis
    engine.manager_name = manager_name
    engine.task_set = {}
    engine.switch_engine = MethodType(_switch_engine, engine)
    engine.add_task(_forever_get_tasks, engine)
    engine.run()


def _forever_get_tasks(engine):
    pipe = engine.redis.pipeline()
    while True:
        # 获取其他进程发送过来的任务
        try:
            results = engine.redis.spop(engine.name, 1000)
        except ResponseError:
            pipe.smembers(engine.name)
            pipe.delete(engine.name)
            results, _ = pipe.execute()
        if results:
            for result in results:
                tasks = loads(result)
                for task in tasks:
                    engine.add_task(*task)

        # 向其他进程发送任务
        for engine_name, task_queue in engine.task_set.items():
            pipe.sadd(engine_name, dumps(task_queue.tasks))
        engine.task_set = {}
        pipe.execute()

        # 无任务时结束进程
        if engine.task_count == 1:
            engine.redis.hset(f'manager-{engine.manager_name}', engine.name, 'Done')
            break
        gevent.sleep(0.5)  # todo: time.sleep（阻塞进程/挂起进程）


def _switch_engine(engine, engine_name):
    if engine_name in engine.task_set:
        return engine.task_set[engine_name]
    else:
        task_queue = TaskQueue()
        engine.task_set[engine_name] = task_queue
        return task_queue
