# -*- coding: UTF-8 -*-
import os
from pathlib import Path
import shutil

# 元信息
# --------------------------------------------------------------------

__name__ = 'tma'
__version__ = "0.3.3"
__author__ = "zengbin"


# 设置用户文件夹
# --------------------------------------------------------------------

data_path = os.path.join(os.path.expanduser('~'), ".tma")
cache_path = os.path.join(data_path, "cache")
Path(cache_path).mkdir(parents=True, exist_ok=True)


def clean_cache():
    shutil.rmtree(cache_path)
    Path(cache_path).mkdir(parents=True, exist_ok=True)


# API - 列表
# --------------------------------------------------------------------
from tma import utils, share, plate, collector, analyst, pool

from tma.utils import push2wx, send_email
from tma.utils import OrderedAttrDict
from tma.utils import is_trade_day, in_trade_time, recent_trade_days

from tma.pool import StockPool
from tma.share import Share

from tma.collector.xueqiu import open_xueqiu
from tma.collector import ts
from tma.collector.cninfo import get_announcements

from tma.collector.ts import (get_share_concepts, get_today_market,
                              get_klines, get_news)
from tma.analyst.kline import KlineAnalyst
from tma.analyst.rank import TfidfDocRank
from tma.analyst.market import get_limit_arrived

# module介绍
# --------------------------------------------------------------------

__doc__ = """
TMA - Tools for Market A - A股工具集
"""
