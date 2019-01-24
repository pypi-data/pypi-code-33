# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018/11/19 11:22
import signal
from os import kill

from .file_operation import file_exists
from .file_operation import load_file_contents
from .file_operation import remove_file


def kill_process(pid_path, signum=None):
    """
    向pid_path文件内容中的PID发送信号
    :param pid_path: pid文件路径
    :param signum: 信号值
    """
    if not file_exists(pid_path):
        return None

    if signum is None:
        signum = signal.SIGKILL

    # 读取PID文件
    pid = int(load_file_contents(pid_path)[0].strip())

    # 向该进程发送信号
    try:
        kill(pid, signum)
    except OSError as e:
        if len(e.args) != 2 or e.args[1] != 'No such process':
            raise

    # 移除PID文件
    remove_file(pid_path)
