# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018/11/14 16:30
import io
import subprocess
import warnings

import six

from .utils.file_operation import write_file_contents

NOHUP = 'nohup'
BG_MARK = '&'


def shell_invoke(command, **kwargs):
    """
    Shell命令调用
    :param command: 命令
    :param kwargs: 关键字参数

    Args:
        log_prefix: 日志路径前缀
        debug: 是否为调试模式
        daemon: 是否在主线程退出之后仍然运行
        on_error: 用于处理出现错误时的函数
            接收参数 e subprocess.CalledProcessError
    :return: 返回码
    """
    log_prefix = kwargs.pop('log_prefix', None)
    debug = kwargs.pop('debug', True)
    daemon = kwargs.pop('daemon', False)
    on_error = kwargs.pop('on_error', None)
    if on_error is not None and not callable(on_error):
        raise TypeError('on_error must be of callable, but got {}'.format(type(on_error)))

    command = command.strip()
    if command == '' or command.startswith(NOHUP) or command.endswith(BG_MARK):
        raise ValueError('command should be a string not start with nohup and not end with &, '
                         'but got "{}"'.format(command))

    stdout, stderr = None, None
    if log_prefix is not None:
        write_file_contents('{}.cmd'.format(log_prefix), command)
        stdout = io.open('{}.out'.format(log_prefix), mode='w', encoding='utf-8')
        stderr = stdout if debug else io.open('{}.err'.format(log_prefix), mode='w', encoding='utf-8')

    if daemon:
        command = '{} {} {}'.format(NOHUP, command, BG_MARK)

    try:
        return subprocess.check_call(command, shell=True, stdout=stdout, stderr=stderr)
    except subprocess.CalledProcessError as e:
        if on_error:
            on_error(e)
        else:
            raise


def executable_exists(executable):
    """
    检测可执行文件是否存在
    :param executable: 可执行文件
    :return: 检测结果, 若存在，返回True, 否则返回False
    """
    try:
        subprocess.check_call('which {} >/dev/null'.format(executable), shell=True)
    except subprocess.CalledProcessError:
        return False
    return True


def _python_invoke(command, **kwargs):
    """
    Python命令调用
    :param command: 命令
    :param kwargs: 关键字参数

    Args:
        version: Python版本号, 默认为3
        log_prefix: 日志路径前缀
        debug: 是否为调试模式
        daemon: 是否在主线程退出之后仍然运行
        on_error: 错误处理函数
        interpreter: Python解释器
    :return: 返回码
    """
    command = command.strip()
    if command == '' or command.startswith('python'):
        raise ValueError('python command should be a string not start with python')

    interpreter = kwargs.pop('interpreter', None)
    if interpreter is None:
        version = kwargs.pop('version', 3)
        if not (version == 2 or version == 3):
            raise ValueError('only support python2 and python3')
        interpreter = 'python{}'.format(version)
        if not executable_exists(interpreter):
            alternative = 'python'
            params = {
                'interpreter': interpreter,
                'alternative': alternative
            }
            message = '{interpreter} not exists, so use {alternative} as interpreter, ' \
                      'ensure that {alternative} is actually the same as {interpreter}'.format(**params)
            warnings.warn(message)
            interpreter = 'python'

    command = '{} -u {}'.format(interpreter, command)
    return shell_invoke(command, **kwargs)


def python2_invoke(command, **kwargs):
    kwargs['version'] = 2
    return _python_invoke(command, **kwargs)


def python3_invoke(command, **kwargs):
    kwargs['version'] = 3
    return _python_invoke(command, **kwargs)


python_invoke = python2_invoke if six.PY2 else python3_invoke
