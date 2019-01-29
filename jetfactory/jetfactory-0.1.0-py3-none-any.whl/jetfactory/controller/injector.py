# -*- coding: utf-8 -*-

from functools import partial
from jetfactory.utils import request_ip
from enum import Enum


class Injector(Enum):
    remote_addr = partial(request_ip)
    request_full = 'request_full'
