"""
常用工具
"""
import datetime
import os
import random
from threading import Thread

from dophon_mq import properties
from dophon_mq.function_unit.SizeableTPE import SizeableThreadPoolExecutor


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def full_0(string: str, num_of_zero: int) -> str:
    if len(string) < num_of_zero:
        string = string.rjust(num_of_zero, '0')
    return string


def get_msg_mark():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S') + full_0(
        str(random.randint(0, 999999999999)), 6)


# 消息池(初步为本地缓存目录)
msg_pool = os.path.expanduser('~') + '/.dophon_msg_pool/'

if not os.path.exists(msg_pool):
    os.mkdir(msg_pool)

remote_msg_pool = os.path.expanduser('~') + '/.dophon_remote_msg_pool/'

if not os.path.exists(remote_msg_pool):
    os.mkdir(remote_msg_pool)


def join_threadable(f):
    def method(*args, **kwargs):
        Thread(target=f, args=args, kwargs=kwargs).start()

    return method


max_workers = properties.msg_queue_max_num

# pool = ThreadPoolExecutor(max_workers=max_workers)
pool = SizeableThreadPoolExecutor(max_workers=max_workers)

trace_manager = {}


def threadable():
    def method(f):
        def target_args(*args, **kwargs):
            # pool.update_worker_size()
            # 采用线程池操作,减缓cpu压力
            # pool.submit(f, *args, **kwargs)

            # 采用新线程处理
            Thread(target=f,args=args,kwargs=kwargs).start()

        return target_args

    return method


def encode_ack_info(d: dict) -> str:
    """
    把确认信息字典编码
    :param d:
    :return:
    """
    res = []
    for item in d.items():
        res.append('%s:%s' % item)
    return ','.join(res)


def decode_ack_info(s: str) -> dict:
    """
    把确认信息字典解码
    :param s:
    :return:
    """
    res = s.split(',')
    obj = {}
    for item in res:
        k, v = item.split(':')
        obj[k] = str(v)
    return obj


def get_os_type():
    return os.name == 'nt'
