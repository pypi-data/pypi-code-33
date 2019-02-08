from multiprocessing import Process
from .task_queue import TaskQueue
from pickle import loads, dumps
from types import MethodType
from .engine import Engine
from redis import Redis
from time import sleep
from uuid import uuid1
import gevent


class Manager:
    def __init__(self, name=None, redis_socket='localhost:6379'):
        self._name = name if name else uuid1()
        self._redis_socket = redis_socket.split(':')
        self.processes = []
        self._is_start = False
        self._redis = Redis(*self._redis_socket)
        self._pipeline = self._redis.pipeline()

    @property
    def name(self):
        return self._name

    def add_processes(self, *engines):
        for engine in engines:
            engine.manager_name = self.name
            self.processes.append(engine)

    def add_engines(self, *engine_names):
        for engine_name in engine_names:
            engine = Engine(name=engine_name)
            engine.manager_name = self.name
            self.processes.append(engine)

    def add_task(self, engine_name, exe_func, *params):
        assert self.processes, 'Engine is not exits!'
        for engine in self.processes:
            if engine.name == engine_name:
                engine.add_task(exe_func, *params)
                break
        else:
            raise Exception('Engine is not exits!')

    def start(self):
        assert not self._is_start
        self._is_start = True
        assert self.processes
        assert int(
            self._redis.info('server')['redis_version'][0]) >= 4, 'The redis version is too low and requires redis4.0+.'
        for engine in self.processes:
            self._pipeline.hsetnx(f'manager-{self.name}', engine.name, 'Ready')  # todo: name 相同时异常处理
        self._pipeline.execute()

        if self._waiting_for_start():
            self._waiting_for_stop()

    def _waiting_for_start(self):
        while True:
            is_run = self._redis.get('is_run')
            if is_run == b'1':
                for engine in self.processes:
                    if engine.tasks:
                        Process(target=_create_process, args=(engine, self._redis_socket)).start()
                        self._pipeline.hset(f'manager-{engine.manager_name}', engine.name, 'Running')
                        self._pipeline.incr('active_engine_count')
                    else:
                        self._pipeline.hset(f'manager-{engine.manager_name}', engine.name, 'Done')

                self._pipeline.execute()
                return True
            elif is_run == b'-1':
                self._redis.flushall()
                self._is_start = False
                return False
            sleep(0.5)

    def _waiting_for_stop(self):
        while True:
            self._pipeline.hgetall(f'manager-{self.name}')
            self._pipeline.scard('_')
            for engine in self.processes:
                self._pipeline.scard(engine.name)
            engine_status, public_task_count, *engines_task_count = self._pipeline.execute()
            for engine, engine_task_count in zip(self.processes, engines_task_count):
                # engine_task_count 对应 engine 剩余任务数量
                if engine_status[engine.name.encode()] == b'Done':
                    if engine_task_count and engine_task_count > 0:
                        self._pipeline.spop(engine.name, 1000)
                    if public_task_count and engine_task_count < engine.pool_size:
                        self._pipeline.spop('_', engine.pool_size)

                    if len(self._pipeline):
                        task_list = self._pipeline.execute()
                        if task_list:
                            engine.tasks = []
                            for tasks in task_list:
                                for task in tasks:
                                    engine.add_task(*loads(task))
                            Process(target=_create_process, args=(engine, self._redis_socket)).start()
                            self._pipeline.hset(f'manager-{engine.manager_name}', engine.name, 'Running')
                            self._pipeline.incr('active_engine_count')
                            self._pipeline.execute()

            self._pipeline.get('is_run')
            self._pipeline.get('active_engine_count')
            is_run, active_engine_count = self._pipeline.execute()
            if (is_run == b'1' and active_engine_count == b'0') or is_run == b'-1':  # 任务完成/停止
                self._redis.flushall()
                self._is_start = False
                break
            if is_run is None:  # 任务已停止
                self._is_start = False
                break
            sleep(0.5)


def _create_process(engine, redis_config):
    engine.redis = Redis(*redis_config)
    engine.task_set = {}
    engine.switch_engine = MethodType(_switch_engine, engine)
    engine.add_task(_forever)
    engine.run()


def _forever():
    pipe = engine.redis.pipeline()
    while True:
        # 获取其他进程发送过来的任务
        pipe.spop(engine.name, 1000)
        pipe.scard('_')

        # 向其他进程发送任务
        for engine_name, task_queue in engine.task_set.items():
            pipe.sadd(engine_name, *map(dumps, task_queue.tasks))
        engine.task_set = {}
        tasks, public_task_count, *_ = pipe.execute()

        if tasks:
            for task in tasks:
                engine.add_task(*loads(task))

        # 从公共任务库中获取任务
        if public_task_count and engine.task_count < engine.pool_size:
            tasks = engine.redis.spop('_', engine.pool_size)
            if tasks:
                for task in tasks:
                    engine.add_task(*loads(task))

        # 无任务时结束进程
        if engine.task_count == 1:
            pipe.hset(f'manager-{engine.manager_name}', engine.name, 'Done')
            pipe.decr('active_engine_count')
            pipe.execute()
            break
        gevent.sleep(0.5)  # todo: time.sleep（阻塞进程/挂起进程）


def _switch_engine(engine, engine_name='_'):
    if engine_name in engine.task_set:
        return engine.task_set[engine_name]
    else:
        task_queue = TaskQueue()
        engine.task_set[engine_name] = task_queue
        return task_queue
