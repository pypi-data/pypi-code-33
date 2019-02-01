# coding=utf-8
from __future__ import print_function

from suanpan.mq.redis import RedisMQ
from suanpan.proxy import Proxy


class MQProxy(Proxy):
    MAPPING = {"redis": RedisMQ}


mq = MQProxy()
