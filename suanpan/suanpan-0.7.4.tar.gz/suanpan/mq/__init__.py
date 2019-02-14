# coding=utf-8
from __future__ import print_function

from suanpan.arguments import Bool, Int, String
from suanpan.mq.redis import RedisMQ
from suanpan.proxy import Proxy


class MQProxy(Proxy):
    MAPPING = {"redis": RedisMQ}
    ARGUMENTS = [
        String("mq-type", default="redis"),
        String("mq-redis-host", default="localhost"),
        Int("mq-redis-port", default=6379),
        Bool("mq-redis-realtime", default=False),
    ]


mq = MQProxy()
