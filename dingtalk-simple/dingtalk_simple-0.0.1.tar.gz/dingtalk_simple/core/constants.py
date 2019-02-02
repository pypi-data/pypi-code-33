# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from enum import Enum

class CallbackType(Enum):
    """回调内容枚举"""
    CHECK_URL = "check_url"  # 校验url
