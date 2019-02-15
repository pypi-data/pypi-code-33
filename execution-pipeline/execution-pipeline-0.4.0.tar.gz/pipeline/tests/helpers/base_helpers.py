from pipeline import execution_pipeline

from pipeline.cache.mock import MockCache
from pipeline.cache.redis import RedisCache
from pipeline.cache.memcache import MemCache

from pipeline.validators import ExceptionHandler

mock_cache = MockCache()
redis_cache = RedisCache()
mem_cache = MemCache()


def do_thing_before(params):
    params['arg1'] = 'this argument is always changed'
    return params


def do_thing_after(response):
    if isinstance(response, dict):
        response['added'] = 'yup'
    return response


def do_another_thing_after(response):
    assert response['added'] == 'yup'  # the one that is first in the pipeline happens first.
    response['also_added'] = 'also yup'
    return response


def handle_this_error(e, response=None):
    # print(f"oh no, Bob! {e}")
    return "Don't worry, we handled a TypeError."


def handle_that_error(e, response=None):
    # print(f"oh no, Bob! {e}")
    return "Don't worry, we handled MyException."


class MyException(BaseException):
    pass


class FailedTestError(BaseException):
    pass


error_handlers = [
    ExceptionHandler(TypeError, handle_this_error),
    ExceptionHandler(MyException, handle_that_error),
    # {"exception_class": TypeError, "handler": handle_this_error},
    # {"exception_class": MyException, "handler": handle_that_error},
]


class A:

    @execution_pipeline(pre=[do_thing_before])
    def __init__(self, arg1='okay'):
        self.stored = arg1

    @execution_pipeline(pre=[do_thing_before], post=[do_thing_after])
    def fun_boys(self, arg1, arg4, arg2, arg3, thing=None):
        # print(arg1, arg2, arg3, thing)
        return dict()

    @execution_pipeline(pre=[do_thing_before], post=[do_thing_after, do_another_thing_after], error=error_handlers)
    def fun_boys1(self, arg1, arg4, arg2, arg3, thing=None):
        return {'thing': thing}

    @execution_pipeline(pre=[do_thing_before], post=[do_thing_after], error=error_handlers)
    def fun_boys2(self, arg1, arg4, arg2, arg3, thing=None):
        raise MyException('Something went wrong!')


class MC:
    def __init__(self):
        self.changed_value = 0

    @execution_pipeline(cache=mock_cache)
    def fun_boys3(self, arg1, arg4, arg2, arg3, thing=None):
        return self.changed_value


class RC:
    def __init__(self):
        self.changed_value = 0

    @execution_pipeline(cache=redis_cache)
    def fun_boys3(self, arg1, arg4, arg2, arg3, thing=None):
        return self.changed_value


class MMC:
    def __init__(self):
        self.changed_value = 0

    @execution_pipeline(cache=mem_cache)
    def fun_boys3(self, arg1, arg4, arg2, arg3, thing=None):
        return self.changed_value


# ensuring that we are referring to the same cache when we have a shared cache scenario
shared_cache = execution_pipeline(cache=redis_cache)


class DistinctClass1:

    @shared_cache
    def avoid_collision(self, ugly_arg):
        return 100


class DistinctClass2:
    @shared_cache
    def avoid_collision(self, ugly_arg):
        return 200
