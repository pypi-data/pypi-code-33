# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018/11/9 14:36
from threading import Thread

from .utils.time_extension import Timer


def deprecated(new_fn=None, version=1.0):
    """
    标记为弃用 decorator
    :param new_fn: 新的替代函数
    :param version: 被移除版本
    :return 包装函数
    """
    if new_fn is not None:
        assert callable(new_fn)

    def function_wrapper(fn):
        assert callable(fn)

        def wrapper(*args, **kwargs):
            params = {
                'newline': '\n',
                'fn_module': fn.__module__,
                'fn_name': fn.__name__,
                'future': 'the future' if version is None else 'version {}'.format(str(version))
            }
            message_fmt = '{newline}' \
                          'some of your code has used "{fn_name}" from {fn_module},' \
                          '{newline}' \
                          'this is marked as deprecated in current version, ' \
                          'and maybe will be removed in {future}'

            if new_fn is not None:
                params['new_fn_module'] = new_fn.__module__
                params['new_fn_name'] = new_fn.__name__
                message_fmt += '{newline}' \
                               'use "{new_fn_name}" from {new_fn_module} instead'
            message = message_fmt.format(**params)

            from warnings import warn
            warn(message)

            return fn(*args, **kwargs)

        return wrapper

    return function_wrapper


def async_call(daemon=False, name=None):
    """
    异步调用 decorator
    :param daemon: 是否为守护进程
    :param name: 线程名称
    :return 包装函数
    """

    def function_wrapper(fn):
        """
        函数修饰器
        :param fn: 被调用函数
        """
        assert callable(fn)

        def wrapper(*args, **kwargs):
            t = Thread(target=fn, args=args, kwargs=kwargs)
            t.setDaemon(daemon)
            if name is not None:
                t.setName(name)
            t.start()

        return wrapper

    return function_wrapper


def timed(description=None):
    """
    计时标记
    :param description: 计时描述
    :return: 包装函数
    """

    def function_wrapper(fn):
        """
            标记为统计运行时间的函数
            :param fn: 被测函数
            """
        assert callable(fn)

        def wrapper(*args, **kwargs):
            _description = fn.__name__
            if description is not None and not callable(description):
                _description = description

            timer = Timer()
            timer.display_start('{} start at'.format(_description))
            result = fn(*args, **kwargs)
            timer.display_finish('{} complete at'.format(_description))
            timer.display_cost(_description)
            return result

        return wrapper

    if callable(description):
        return function_wrapper(fn=description)

    return function_wrapper
