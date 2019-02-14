# coding=utf-8
from __future__ import print_function

from suanpan.arguments import Int, String
from suanpan.mstorage.redis import RedisMStorage
from suanpan.proxy import Proxy


class MStorageProxy(Proxy):
    MAPPING = {"redis": RedisMStorage}
    ARGUMENTS = [
        String("mstorage-type", default="redis"),
        String("mstorage-redis-host", default="localhost"),
        Int("mstorage-redis-port", default=6379),
    ]


mstorage = MStorageProxy()
