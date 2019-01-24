# -*- coding: UTF-8 -*-

"""
analyst.kline - K线分析
====================================================================
"""
import talib
import os
import time
import pickle
from datetime import datetime, timedelta

from tma import cache_path
from tma.collector import ts


class KlineAnalyst:
    """K线技术分析

    K线类别：
    1min, 5min, 15min, 30min, 60min, D, W, M
    """

    def __init__(self, ts_code, start=None,
                 freq='60min', source='pro',
                 cache_interval=0):
        """

        :param ts_code: str
            tushare 股票代码；对于分钟线，也可以是指数代码。
        :param start: str
            开始时间，如 20180101
        :param freq: str
            K线级别，可选值 [1min, 5min, 15min, 30min, 60min, D, W, M]
        :param cache_interval: int
            数据缓存间隔，单位：秒，默认为 0
        """
        self.ts_code = ts_code
        self.start = start
        self.freq = freq
        self.source = source

        if not self.start:
            dt_now = datetime.now()
            if self.freq == 'M':
                st = dt_now - timedelta(days=365*10)
            elif self.freq == 'W':
                st = dt_now - timedelta(days=800)
            else:
                st = dt_now - timedelta(days=300)
            self.start = str(st.date()).replace('-', '')

        # 缓存文件
        self.pkl_cache = os.path.join(cache_path, "%s.%s.pkl" % (ts_code, freq))
        if os.path.exists(self.pkl_cache) and \
                time.time() - os.path.getmtime(self.pkl_cache) < cache_interval:
            self.kline = pickle.load(open(self.pkl_cache, 'rb'))

        else:
            self.kline = ts.klines(code=self.ts_code[:-3], start=self.start,
                                   freq=self.freq, source=self.source)
            self._basic_cal()
            self.ma('close', n=(5, 10, 20, 30, 60))
            self.macd('close')
            pickle.dump(self.kline, open(self.pkl_cache, 'wb'))

    def _basic_cal(self):
        k = self.kline
        # 计算涨跌幅
        k['pct_chg'] = round((k['close'] - k['pre_close']) / k['pre_close'], 4) * 100
        # 计算波动幅度
        k['pct_wave'] = round((k['high'] - k['low']) / k['pre_close'], 4) * 100
        self.kline = k

    # --------------------------------------------------------------------
    def ma(self, col, n=(5, 10)):
        """计算均线

        :param col: str
            字段名，通常使用 close 计算 MACD 指标
        :param n: int or tuple of int
            均线周期，默认值 5
        :return: None
        """
        if isinstance(n, int):
            n = [n]

        col_series = self.kline[col]
        for i in n:
            col_out = col + "_ma" + str(i)
            self.kline[col_out] = col_series.rolling(i).mean()

    # --------------------------------------------------------------------
    def macd(self, col):
        """计算 MACD 指标

        :param col: str
            字段名，通常使用 close 计算 MACD 指标
        :return: None
        """
        col_series = self.kline[col]
        macd, signal, hist = talib.MACD(col_series)
        self.kline[col + '_macd'] = macd
        self.kline[col + '_macd_signal'] = signal
        self.kline[col + '_macd_hist'] = hist
