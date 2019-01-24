# coding:utf-8
import os
import time
import pickle

import tma
from tma.collector import ts
from tma.analyst.kline import KlineAnalyst
import tma.utils as u


class Share:
    def __init__(self, code, cache_interval=0):
        """

        :param code: str
            600122 或 600122.SH
        :param cache_interval: int
            缓存有效期（单位：s），默认为 0
        """
        if len(code) == 6:
            code = ts.to_ts_code(code)
        self.ts_code = code
        self._real_time()

        # cache
        cache_file = os.path.join(tma.cache_path, "%s.pkl" % self.ts_code)
        if os.path.exists(cache_file) and time.time() - os.path.getmtime(cache_file) < cache_interval:
            print("load cached data of %s from %s " % (self.ts_code, cache_file))
            cache = pickle.load(open(cache_file, 'rb'))
            self.ka_30min, self.ka_60min, self.ka_d, self.ka_w, \
                self.concepts, self.indicators = cache
        else:
            self._concepts()
            self._klines()
            self._indicators()

            cache = [
                self.ka_30min, self.ka_60min, self.ka_d, self.ka_w,
                self.concepts, self.indicators
            ]
            pickle.dump(cache, open(cache_file, 'wb'))

    def _real_time(self):
        b = ts.bars(self.ts_code[:6])
        if len(b) == 1:
            for col in ['price', 'pre_close', 'high', 'low']:
                b[col] = b[col].apply(float)
            # 计算涨跌幅
            b['pct_chg'] = round((b['price'] - b['pre_close']) / b['pre_close'], 4) * 100
            # 计算波动幅度
            b['pct_wave'] = round((b['high'] - b['low']) / b['pre_close'], 4) * 100
            self.name = b.iloc[0]['name']
            self.price = b.iloc[0]['price']
            self.pre_close = b.iloc[0]['pre_close']
            self.pct_chg = b.iloc[0]['pct_chg']
            self.pct_wave = b.iloc[0]['pct_wave']
        else:
            self.name = self.price = self.pre_close = None
            self.pct_chg = self.pct_wave = None

    def _concepts(self):
        """获取概念列表"""
        share_concepts = ts.get_share_concepts(self.ts_code)
        self.concepts = list(share_concepts['concept'])

    def _klines(self):
        ts_code = self.ts_code
        self.ka_30min = KlineAnalyst(ts_code, freq='30min', cache_interval=60*15, source='old')
        self.ka_60min = KlineAnalyst(ts_code, freq='60min', cache_interval=60*30, source='old')
        self.ka_d = KlineAnalyst(ts_code, freq='D', cache_interval=60*60*2, source='pro')
        self.ka_w = KlineAnalyst(ts_code, freq='W', cache_interval=60*60*72, source='pro')

    def announcements(self, start=None):
        """获取公告列表

        :param start: str
            开始时间，如："20170810"，默认值为今日向前推 180天 的日期
        :return:
        """
        df = tma.get_announcements(self.ts_code[:6], start=start)
        ann = []
        for _, row in df.iterrows():
            ann.append({
                "date": row['date'],
                'title': row['title'],
                "url": row['url']
            })
        return ann

    def _indicators(self):
        self.indicators = u.OrderedAttrDict()
        ts_code = self.ts_code
        ka_60min = self.ka_60min
        ka_d = self.ka_d
        ka_w = self.ka_w

        try:
            fi = ts.pro.fina_indicator(ts_code=ts_code, fields="ts_code,end_date,roe_yearly")
            latest_fi = fi.iloc[0]
            v_i001 = float(latest_fi["roe_yearly"])
        except:
            v_i001 = 0
        self.indicators['I001'] = u.OrderedAttrDict({
            "name": "I001",
            "desc": "年化净资产收益率",
            "type": "float",
            "value": v_i001
        })

        try:
            latest_60min_macd = list(ka_60min.kline.close_macd_hist[-3:])[::-1]
            v_i002 = latest_60min_macd[0] > latest_60min_macd[1] > latest_60min_macd[2]
        except:
            v_i002 = False
        self.indicators['I002'] = u.OrderedAttrDict({
            "name": "I002",
            "desc": "60分钟线MACD柱子呈现正向增大趋势",
            "type": "binary",
            "value": v_i002
        })

        try:
            latest_30d_amount = [x * 1000 for x in ka_d.kline.amount.iloc[-30:]]
            v_i003 = round(sum(latest_30d_amount) / 30 / 10000, 4)
        except:
            v_i003 = 0
        self.indicators['I003'] = u.OrderedAttrDict({
            "name": "I003",
            "desc": "最近30个交易日的日均成交量（万元）",
            "type": "float",
            "value": v_i003
        })

        try:
            v_i004 = round(sum(ka_w.kline.pct_chg.iloc[-2:]), 4)
        except:
            v_i004 = 0
        self.indicators['I004'] = u.OrderedAttrDict({
            "name": "I004",
            "desc": "周线级别上，最近两根K线的累计涨跌幅",
            "type": "float",
            "value": v_i004
        })

        try:
            v_i005 = sum(ka_d.kline.iloc[-30:]['pct_wave'] > 5)
        except:
            v_i005 = 0
        self.indicators['I005'] = u.OrderedAttrDict({
            "name": "I005",
            "desc": "最近30个交易日，波动幅度大于5个点的交易日数量",
            "type": "int",
            "value": v_i005
        })

    def __repr__(self):
        return "<Share Object: %s>" % self.ts_code

