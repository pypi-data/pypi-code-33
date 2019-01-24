# -*- coding: UTF-8 -*-
"""
Tushare数据接口封装
====================================================================
"""
import os
import time
from datetime import datetime, timedelta
from tqdm import tqdm
import pandas as pd
import tushare as ts

from tma import data_path, cache_path

pro = ts.pro_api()


def to_ts_code(code):
    if code.startswith("6"):
        return code + ".SH"
    else:
        return code + ".SZ"


# --------------------------------------------------------------------

def get_market_basic(cache=True, use_cache=False):
    """返回A股所有股票的基础信息"""
    FILE_BASIC = os.path.join(cache_path, "market_basic.csv")

    if os.path.exists(FILE_BASIC):
        now_t = time.time()
        modify_t = os.path.getmtime(FILE_BASIC)

        if use_cache and now_t - modify_t < 3600 * 12:
            basic_df = pd.read_csv(FILE_BASIC, dtype={"code": str})
            return basic_df

    basic_df = ts.get_stock_basics()
    basic_df.reset_index(inplace=True)
    basic_df['code'] = basic_df['code'].astype(str)
    if cache:
        basic_df.to_csv(FILE_BASIC, encoding='utf-8', index=False)
    return basic_df


def get_all_codes():
    """返回A股所有股票的代码"""
    basic_df = get_market_basic(cache=True, use_cache=True)
    return list(basic_df['code'])


# --------------------------------------------------------------------

def get_indices():
    """指数行情接口"""
    return ts.get_index()


def get_price(code):
    """获取一只股票的最新价格

    :param code: str
        股票代码，如：600122
    :return: float
    """
    data = ts.get_realtime_quotes(code)
    return float(data.loc[0, 'price'])


def get_ticks(code, source="spider", date=None, cons=None):
    """返回date日期的分笔数据

    :param source:
    :param code: str: 股票代码，如 603655
    :param date: str: 日期，如 2018-03-15
    :param cons: tushare的api连接
    :return:
    """
    if not date:
        date = datetime.now().date().__str__()
    TODAY = datetime.now().date().__str__()

    # 统一 ticks 的输出结果
    def _unify_out(ticks, date):
        ticks = ticks[['time', 'price', 'volume', 'type']]
        ticks['datetime'] = ticks['time'].apply(lambda x: datetime.strptime(date + " " + x, "%Y-%m-%d %H:%M:%S"))
        ticks['vol'] = ticks['volume']
        type_convert = {
            "买盘": 0,
            "卖盘": 1,
            "中性盘": 2,
            "0": 2
        }
        ticks['type'] = ticks["type"].apply(lambda x: type_convert[str(x)])
        ticks.drop(['time', 'volume'], axis=1, inplace=True)
        ticks.sort_values('datetime', inplace=True)
        ticks.reset_index(drop=True, inplace=True)
        return ticks[['datetime', 'price', 'vol', 'type']]

    if source == "spider" and date == TODAY:
        ticks = ts.get_today_ticks(code=code)
        ticks = _unify_out(ticks, date=TODAY)
    elif source == "spider" and date != TODAY:
        ticks = ts.get_tick_data(code=code, date=date)
        ticks = _unify_out(ticks, date=date)
    else:
        if not cons:
            cons = ts.get_apis()
        ticks = ts.tick(code=code, conn=cons, date=date)
    return ticks


ticks = get_ticks


def get_bars(codes):
    """获取codes的实时quotes"""
    return ts.get_realtime_quotes(codes)


bars = get_bars


def get_klines(code, freq="D", start=None, source='pro'):
    """获取K线数据

    :param source: str
        可选值 pro，old
    :param code: str 股票代码
    :param start: str 默认为 None
        开始日期。值为None时，默认获取全部。 如 20180101
    :param freq: str 默认为 "D"
        [1min, 5min, 15min, 30min, 60min, D, W, M]
        K线周期，可选值 D=日k线 W=周 M=月 5min=5分钟 15min=15分钟 30min=30分钟 60min=60分钟
    :return: pd.DataFrame
          code      股票代码
          dt        时间
          pre_close 上次收盘价
          open      开盘价
          close     收盘价
          high      最高价
          low       最低价
          volume    成交量（手）
          amount    成交额（万元）
    """
    valid_freq = ['1min', '5min', '15min', '30min', '60min', 'D', 'W', 'M']
    assert freq in valid_freq, "freq value error, must be one of %s" % str(valid_freq)

    cols = ['code', 'dt', 'pre_close', 'open', 'close', 'high', 'low', 'volume', 'amount']

    end = datetime.now().date()
    if start is None:
        delta = timedelta(days=100)
        start = end - delta
    else:
        start = datetime.strptime(start, "%Y%m%d")

    if source == 'pro':
        ts_code = to_ts_code(code)
        start = str(start).replace('-', "")
        end = str(end).replace('-', "")
        if freq.endswith('min'):
            k = pro.mins(ts_code=ts_code, start_time=start, end_time=end, freq=freq)
            k['trade_date'] = k['trade_time']
        elif freq == 'D':
            k = pro.daily(ts_code=ts_code, start_date=start, end_date=end)
        elif freq == 'W':
            k = pro.weekly(ts_code=ts_code, start_date=start, end_date=end)
        elif freq == 'M':
            k = pro.monthly(ts_code=ts_code, start_date=start, end_date=end)
        else:
            raise ValueError("freq value error, must be one of %s" % str(valid_freq))

        # 数据规范
        k.sort_values('trade_date', inplace=True, ascending=True)
        k['pre_close'] = k['close'].shift(1)
        k.rename(columns={'ts_code': 'code',
                          'trade_date': 'dt',
                          'vol': 'volume'},
                 inplace=True)
        k['amount'] = k['amount'].apply(lambda x: round(x/10, 4))
        k.reset_index(drop=True, inplace=True)

    elif source == 'old':
        k = ts.get_k_data(code=code, start=str(start), ktype=freq.replace("min", ""))
        k['pre_close'] = k['close'].shift(1)
        k['code'] = k['code'].apply(to_ts_code)
        k['amount'] = k['volume'] * k['close']
        k.rename(columns={'date': 'dt'},
                 inplace=True)

    else:
        raise ValueError("source value error, must be one of (pro, old)")

    k = k[cols]
    k.reset_index(drop=True, inplace=True)
    return k


klines = get_klines


# 全市场行情
# --------------------------------------------------------------------

def filter_tp(tm):
    """停盘股过滤

    :param tm: return of function today_market
    :return:
    """
    tm1 = tm[tm['volume'] != 0.0]
    tm1.reset_index(drop=True, inplace=True)
    return tm1


def filter_st(tm):
    """ST股过滤

    :param tm: return of function today_market
    :return:
    """
    fst = tm['name'].apply(lambda x: True if "ST" not in x else False)
    tm1 = tm[fst]
    tm1.reset_index(drop=True, inplace=True)
    return tm1


def get_today_market(filters=None, save=True,
                     use_latest=False, interval=600):
    """返回最近一个交易日所有股票的交易数据

    :param filters: list 默认为 ['tp', 'st']
        需要应用的过滤规则，可选 "tp"、"st"。tp表示过滤停盘股，st表示过滤st股。
    :param save: bool 默认为 True
        是否缓存到user目录下
    :param use_latest: bool 默认为 False
        是否使用最近缓存的数据
    :param interval: int 默认 600
        更新行情的最小间隔（单位：s），即：如果 CACHE_PATH 路径下的latest_market的修改时间
        与当前时间的间隔小于interval设定的数值，且use_latest为True，
        将使用latest_market.csv中的行情
    :return: pd.DataFrame
        最新的市场行情
    """
    if filters is None:
        filters = ['tp', 'st']
    tm_csv = os.path.join(cache_path, 'latest_market.csv')
    if use_latest and os.path.exists(tm_csv) \
            and time.time() - os.path.getmtime(tm_csv) < interval:
        tm = pd.read_csv(tm_csv, encoding='utf-8', dtype={"code": str})
        return tm

    tm = ts.get_today_all()
    if filters is None:
        return tm
    filters = [x.lower() for x in filters]
    if "tp" in filters:
        tm = filter_tp(tm)
    if "st" in filters:
        tm = filter_st(tm)
    if save:
        tm.to_csv(tm_csv, index=False, encoding='utf-8')
    return tm


def get_hist_market(date):
    """历史行情数据

    :param date: str:
        指定日期，如 "2018-03-19"
    :return:
    """
    hm = ts.get_day_all(date)
    hm['date'] = date
    return hm


def get_news(start_date, end_date):
    """
    如果是某一天的数据，可以输入日期 20181120 或者 2018-11-20，
    比如要想取2018年11月20日的新闻，可以设置start_date='20181120',
    end_date='20181121' （大于数据一天）

    如果是加时间参数，可以设置：start_date='2018-11-20 09:00:00',
    end_date='2018-11-20 22:05:03'
    """
    sources = ["sina", "wallstreetcn", "10jqka", "eastmoney", "yuncaijing"]

    news = []
    for src in sources:
        df = pro.news(src=src, start_date=start_date, end_date=end_date)
        for i, row in df.iterrows():
            new = row["title"].strip() + row["content"].strip()
            news.append(new)
    return news


def get_share_concepts(ts_code=None, cache_interval=30*24*60*60):
    """获取股票的全部概念列表

    :param ts_code: str
        股票代码，如 600122 或 600122.SH
    :param cache_interval: int
        缓存有效期，默认为 30天
    :return: pd.DataFrame
        ts_code
        concept
        name
    """
    cache_file = os.path.join(data_path, 'share_concepts.csv')

    if os.path.exists(cache_file) and \
            time.time() - os.path.getmtime(cache_file) < float(cache_interval):
        shares_df = pd.read_csv(cache_file, encoding='utf-8')
    else:
        concept = pro.concept()
        shares = []

        for _, row in tqdm(concept.iterrows(), desc='get share concept', ncols=88):
            time.sleep(1)
            df = pro.concept_detail(id=row['code'], fields='ts_code,name')
            df['concept'] = row['name']
            shares.append(df)

        shares_df = pd.concat(shares, ignore_index=True)
        shares_df.to_csv(cache_file, index=False, encoding='utf-8')

    if ts_code:
        if len(ts_code) == 6:
            ts_code = to_ts_code(ts_code)
        shares_df = shares_df[shares_df['ts_code'] == ts_code]
    return shares_df

