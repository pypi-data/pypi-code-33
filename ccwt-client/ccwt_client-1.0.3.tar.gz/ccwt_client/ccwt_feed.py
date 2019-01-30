#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018/10/27 17:18    @Author  : xycfree
# @Descript:
from ccwt_client import logger
import datetime
import time
from ccwt_client.core import cli
from pyalgotrade.barfeed import dbfeed
from pyalgotrade.barfeed import membf
from pyalgotrade import bar
from pyalgotrade.utils import dt

log = logger.getLogger("ccwt_feed")


def normalize_instrument(instrument):
    return instrument.upper()


# mongo DB.
# Timestamps are stored in UTC.
class Database(dbfeed.Database):

    def __init__(self):
        pass

    @staticmethod
    def stamp_to_datetime(stamp, strformat="%Y-%m-%d %H:%M:%S"):
        """时间戳转日期格式
        """
        stamp = int(stamp)
        strf = time.strftime(strformat, time.localtime(stamp))
        dt_format = datetime.datetime.strptime(strf, strformat)
        return dt_format

    @staticmethod
    def datetime_toTimestamp(date_time):
        """日期格式转换为时间戳"""
        return int(time.mktime(date_time.timetuple()))

    def date_compare(self, frequency, before_bar, before_date_time, now_date_time):
        """ 日期比较，并填充bar数据
        :param before_bar: 上一个时间点的bar数据
        :param frequency: 数据频率
        :param before_date_time: 上一个时间点
        :param now_date_time: 当前时间点
        :return:
        """
        # log.info("date_compare: {}, {}, {}, {}".format(frequency, before_bar, before_date_time, now_date_time))
        li = []
        if frequency == bar.Frequency.SECOND:
            delta = datetime.timedelta(seconds=1)
            delta_1 = 1
        elif frequency == bar.Frequency.MINUTE:
            delta = datetime.timedelta(minutes=1)
            delta_1 = 60
        elif frequency == bar.Frequency.HOUR:
            delta = datetime.timedelta(hours=1)
            delta_1 = 60*60
        elif frequency == bar.Frequency.DAY:
            delta = datetime.timedelta(days=1)
            delta_1 = 60*60*24
        elif frequency == bar.Frequency.WEEK:
            delta = datetime.timedelta(days=7)
            delta_1 = 60*60*24*7
        elif frequency == bar.Frequency.MONTH:
            delta = datetime.timedelta(days=30)
            delta_1 = 60*60*24*30
        else:
            log.warning("穿入的frequency有误，请检查!!")
            delta = datetime.timedelta(seconds=-1)
            delta_1 = 1

        befor_date_stamp = self.datetime_toTimestamp(before_date_time)
        now_date_stamp = self.datetime_toTimestamp(now_date_time)

        temp_date = befor_date_stamp
        _times = (now_date_stamp - befor_date_stamp) // delta_1

        if _times > 1:
            log.info("_times is: {}".format(_times))
            for i in range(_times - 1):
                temp_date = temp_date + delta_1
                li.append(list([self.stamp_to_datetime(temp_date)] + before_bar[1:]))

        # while True:
        #     log.info("进入while循环...")
        #     if now_date_stamp == temp_date or _time_min < (now_date_stamp - temp_date) < _time_max:
        #         break
        #     else:
        #         li.append(list([self.stamp_to_datetime(temp_date)] + before_bar[1:]))
        #         temp_date = temp_date + delta_1
        return li


    def getBars(self, instrument, frequency, test_back=True, timezone='', start_date='', end_data=''):
        """  frequency 为 bar.Frequency.SECOND时获取ticker数据，其他的获取kline数据；
        :param instrument: exchange_symbol
        :param frequency: 频率
        :param timezone:
        :param start_date:
        :param end_data:
        :return:
        """
        period, ticker_flag = self.get_frequency_info(frequency)
        volume = 'base_volume' if ticker_flag else 'volume'
        limit = 1000 if test_back else ''
        # client获取数据
        col = get_data_info(instrument, period, ticker_flag, start_date, end_data, limit)
        log.info("getBars col is len: {}".format(len(col)))
        _tmp = []  # 临时bar数据，用于查看，打日志；
        ret = []  # bar数据
        map = {}  # 去重处理；

        if col:
            first_di = col[0]  # 第一条bar数据
            first_str_date_time = first_di.get('sys_time')  # 系统日期 str
            first_date_time = datetime.datetime.strptime(first_str_date_time, '%Y-%m-%d %H:%M:%S')  # 转换为日期格式
            first_bars = [first_date_time, first_di.get('open', 0) or first_di.get('preclose', 0), first_di.get('high', 0),
                          first_di.get('low', 0), first_di.get('close', 0), first_di[volume], None, frequency]  # 第一条bar数据
            map[first_str_date_time] = '1'
            ret.append(
                bar.BasicBar(first_bars[0], first_bars[1], first_bars[2], first_bars[3], first_bars[4], first_bars[5],
                             first_bars[6], first_bars[7])
                )  # 第一条bar数据加入
            _tmp.append(first_bars)
        else:
            log.info("getBars获取的数据为空!!!")
            return []

        for idx, row in enumerate(col[1:]):
            # 每遍历一次bar数据时，保留当前数据及时间；
            str_date_time = row.get('sys_time')
            # bars的时间，为了与上一个bar的时间进行比较，查看是否缺少数据，
            date_time = datetime.datetime.strptime(str_date_time, '%Y-%m-%d %H:%M:%S')
            # bars临时数据，为了填充上一时刻没有数据的情况
            _bars = [date_time, row.get('open', 0) or row.get('preclose', 0), row.get('high', 0),
                     row.get('low', 0), row.get('close', 0), row[volume], None, frequency]

            fill_bars = self.date_compare(frequency, first_bars, first_date_time, date_time)  # 获取需要填充的bar数据
            try:
                for b in fill_bars:
                    _str_date_time = b[0].strftime('%Y-%m-%d %H:%M:%S')
                    _date_time = b[0]
                    if _str_date_time not in map:
                        ret.append(
                            bar.BasicBar(b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7])
                        )
                        map[_str_date_time] = '1'
                        _tmp.append(b)
            except:
                pass

            try:
                if str_date_time not in map:
                    ret.append(
                        bar.BasicBar(_bars[0], _bars[1], _bars[2],_bars[3],_bars[4],_bars[5],_bars[6],_bars[7])
                    )
                    map[str_date_time] = '1'
                    _tmp.append(_bars)
            except Exception as e:
                log.warning("异常: {}".format(e))
                pass
            first_bars = _bars
            first_date_time = date_time
        log.info("======ret is len: {}======".format(len(ret)))
        log.info("=========_tmp top 2: {}， _tmp len: {}============".format(_tmp[:2], len(_tmp)))
        # log.info("========map: {}========".format(map))
        return ret

    def getBarsFuture(self, instrument, frequency, types, test_back=True, timezone='', start_date='', end_data=''):
        """  frequency 为 bar.Frequency.SECOND时获取ticker数据，其他的获取kline数据；
        :param types: 获取期货那类数据，ticker, kline, this_week_kline, this_week_ticker,
                next_week_kline, next_week_ticker, quarter_kline, quarter_ticker
        :param instrument: exchange_symbol
        :param frequency: 频率
        :param timezone:
        :param start_date:
        :param end_data:
        :return:
        """
        period, ticker_flag = self.get_frequency_info(frequency)
        log.info("getBarsFuture period:{}, ticker_flag:{}".format(period, ticker_flag))
        volume = 'base_volume' if ticker_flag else 'volume'
        # volume = 'volume'
        limit = 1000 if test_back else ''
        # client获取数据
        col = get_data_future_info(instrument, types, period, ticker_flag, start_date, end_data, limit)
        log.info("getBarsFuture col is len: {}".format(len(col)))

        _tmp = []  # 临时bar数据，用于查看，打日志；
        ret = []  # bar数据
        map = {}  # 去重处理；

        if col:
            first_di = col[0]  # 第一条bar数据
            first_str_date_time = first_di.get('sys_time')  # 系统日期 str
            first_date_time = datetime.datetime.strptime(first_str_date_time, '%Y-%m-%d %H:%M:%S')  # 转换为日期格式

            first_bars = [first_date_time, first_di.get('open', 0) or first_di.get('preclose', 0) or first_di.get('close', 0),
                          first_di.get('high', 0), first_di.get('low', 0), first_di.get('close', 0),
                          first_di[volume], None, frequency]  # 第一条bar数据
            map[first_str_date_time] = '1'
            ret.append(
                bar.BasicBar(first_bars[0], first_bars[1], first_bars[2], first_bars[3], first_bars[4], first_bars[5],
                             first_bars[6], first_bars[7])
            )  # 第一条bar数据加入
            _tmp.append(first_bars)
        else:
            log.info("getBars获取的数据为空!!!")
            return []

        for idx, row in enumerate(col[1:]):
            # 每遍历一次bar数据时，保留当前数据及时间；
            str_date_time = row.get('sys_time')
            # bars的时间，为了与上一个bar的时间进行比较，查看是否缺少数据，
            date_time = datetime.datetime.strptime(str_date_time, '%Y-%m-%d %H:%M:%S')
            # bars临时数据，为了填充上一时刻没有数据的情况
            _bars = [date_time, row.get('open', 0) or row.get('preclose', 0) or row.get('close', 0), row.get('high', 0),
                     row.get('low', 0), row.get('close', 0), row[volume], None, frequency]

            fill_bars = self.date_compare(frequency, first_bars, first_date_time, date_time)  # 获取需要填充的bar数据
            try:
                for b in fill_bars:
                    _str_date_time = b[0].strftime('%Y-%m-%d %H:%M:%S')
                    _date_time = b[0]
                    if _str_date_time not in map:
                        ret.append(
                            bar.BasicBar(b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7])
                        )
                        map[_str_date_time] = '1'
                        _tmp.append(b)
            except:
                pass

            try:
                if str_date_time not in map:
                    ret.append(
                        bar.BasicBar(_bars[0], _bars[1], _bars[2], _bars[3], _bars[4], _bars[5], _bars[6], _bars[7])
                    )
                    map[str_date_time] = '1'
                    _tmp.append(_bars)
            except Exception as e:
                log.warning("异常: {}".format(e))
                pass
            first_bars = _bars
            first_date_time = date_time
        log.info("======ret is len: {}======".format(len(ret)))
        log.info("=========_tmp top 2: {}， _tmp len: {}============".format(_tmp[:2], len(_tmp)))
        # log.info("========map: {}========".format(map))
        return ret

        # ========================================================== #
        # _tmp = []
        # ret = []
        # map = {}
        # for row in col:
        #     str_date_time = row.get('sys_time')
        #     date_time = datetime.datetime.strptime(str_date_time, '%Y-%m-%d %H:%M:%S')
        #     try:
        #         if str_date_time not in map:
        #             ret.append(
        #                 bar.BasicBar(date_time, row.get('open', 0) or row.get('colse', 0) or row.get('close', 0),
        #                              row.get('high', 0), row.get('low', 0),
        #                              row.get('colse', 0) or row.get('close', 0), row[volume], None, frequency))
        #             map[str_date_time] = '1'
        #             _tmp.append(
        #                 [date_time, row.get('open', 0) or row.get('colse', 0) or row.get('close', 0), row.get('high', 0),
        #                  float(row.get('low', 0)), row.get('colse', 0) or row.get('close', 0), row[volume], None, frequency])
        #     except Exception as e:
        #         log.warning("异常: {}".format(e))
        #         pass
        #
        # log.debug("======ret is len: {}======".format(len(ret)))
        # log.debug("=========_tmp top 2: {}, is len: {}============".format(_tmp[:2], len(_tmp)))
        # return ret
        # ========================================================== #
    def getBarsFutureIndex(self, instrument, frequency, types, test_back=True, timezone='', start_date='', end_data=''):
        """  frequency 为 bar.Frequency.SECOND时获取ticker数据，其他的获取kline数据；
        :param types: 获取期货那类数据，index
        :param instrument: exchange_symbol
        :param frequency: 频率
        :param timezone:
        :param start_date:
        :param end_data:
        :return:
        """
        period, ticker_flag = self.get_frequency_info(frequency)
        volume = 'base_volume' if ticker_flag else 'volume'
        limit = 1000 if test_back else ''
        # client获取数据
        col = get_data_future_index_info(instrument, types, start_date, end_data, limit)

        _tmp = []  # 临时bar数据，用于查看，打日志；
        ret = []  # bar数据
        map = {}  # 去重处理；

        if col:
            first_di = col[0]  # 第一条bar数据
            first_str_date_time = first_di.get('sys_time')  # 系统日期 str
            first_date_time = datetime.datetime.strptime(first_str_date_time, '%Y-%m-%d %H:%M:%S')  # 转换为日期格式

            first_bars = [first_date_time,
                          first_di.get('open', 0) or first_di.get('preclose', 0) or first_di.get('close', 0),
                          first_di.get('high', 0), first_di.get('low', 0), first_di.get('close', 0),
                          first_di.get('volume', 0), None, frequency]  # 第一条bar数据
            map[first_str_date_time] = '1'
            ret.append(
                bar.BasicBar(first_bars[0], first_bars[1], first_bars[2], first_bars[3], first_bars[4], first_bars[5],
                             first_bars[6], first_bars[7])
            )  # 第一条bar数据加入
            _tmp.append(first_bars)
        else:
            log.info("getBars获取的数据为空!!!")
            return []

        for idx, row in enumerate(col[1:]):
            # 每遍历一次bar数据时，保留当前数据及时间；
            str_date_time = row.get('sys_time')
            # bars的时间，为了与上一个bar的时间进行比较，查看是否缺少数据，
            date_time = datetime.datetime.strptime(str_date_time, '%Y-%m-%d %H:%M:%S')
            # bars临时数据，为了填充上一时刻没有数据的情况
            _bars = [date_time, row.get('open', 0) or row.get('preclose', 0) or row.get('close', 0), row.get('high', 0),
                     row.get('low', 0), row.get('close', 0), row.get(volume, 0), None, frequency]

            fill_bars = self.date_compare(frequency, first_bars, first_date_time, date_time)  # 获取需要填充的bar数据
            try:
                for b in fill_bars:
                    _str_date_time = b[0].strftime('%Y-%m-%d %H:%M:%S')
                    _date_time = b[0]
                    if _str_date_time not in map:
                        ret.append(
                            bar.BasicBar(b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7])
                        )
                        map[_str_date_time] = '1'
                        _tmp.append(b)
            except:
                pass

            try:
                if str_date_time not in map:
                    ret.append(
                        bar.BasicBar(_bars[0], _bars[1], _bars[2], _bars[3], _bars[4], _bars[5], _bars[6], _bars[7])
                    )
                    map[str_date_time] = '1'
                    _tmp.append(_bars)
            except Exception as e:
                log.warning("异常: {}".format(e))
                pass
            first_bars = _bars
            first_date_time = date_time
        log.info("======ret is len: {}======".format(len(ret)))
        log.info("=========_tmp top 2: {}， _tmp len: {}============".format(_tmp[:2], len(_tmp)))
        # log.info("========map: {}========".format(map))
        return ret

        # _tmp = []
        # ret = []
        # map = {}
        #
        # for row in col:
        #
        #     # _time_stamp = row.get('time_stamp', '') or row.get('timestamp', '')
        #     # log.info("==========_time_stamp: {}==========".format(_time_stamp))
        #     # dateTime, strDateTime = self.get_time_stamp_info(_time_stamp, timezone)
        #     # log.info('dateTime: {}, strDateTime: {}'.format(dateTime, strDateTime))
        #     str_date_time = row.get('sys_time')
        #     date_time = datetime.datetime.strptime(str_date_time, '%Y-%m-%d %H:%M:%S')
        #     try:
        #         if str_date_time not in map:
        #             _close = row.get('index', 0) or row.get('close', 0)
        #             ret.append(
        #                 bar.BasicBar(date_time, _close, _close, _close, _close, _close, None, frequency))
        #             map[str_date_time] = '1'
        #             _tmp.append(
        #                 [date_time, date_time, _close,_close,_close,_close,_close, None, frequency])
        #     except Exception as e:
        #         log.warning("异常: {}".format(e))
        #         pass
        #
        # log.debug("======ret is len: {}======".format(len(ret)))
        # log.debug("=========_tmp top 3: {}============".format(_tmp[:3]))
        # return ret

    def get_time_stamp_info(self, time_stamp, timezone=''):
        """ time_stamp转换为datetime
        :param time_stamp:
        :return:
        """
        try:
            dateTime = dt.timestamp_to_datetime(time_stamp // 1000)
            if timezone:
                dateTime = dt.localize(dateTime, timezone)
            strDateTime = dateTime.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            log.debug("时间戳转换失败: {}".format(e))
            try:
                dateTime = datetime.datetime.strptime(time_stamp, "%Y-%m-%dT%H:%M:%S")
            except:
                dateTime = datetime.datetime.strptime(time_stamp, "%Y-%m-%dT%H:%M:%S.%fZ")
            strDateTime = dateTime.strftime("%Y-%m-%d %H:%M:%S")
            # dateTime = dateTime.strftime("%Y-%m-%d %H:%M:%S")
        return dateTime, strDateTime

    def get_frequency_info(self, frequency):
        """获取高频数据"""
        period = ''
        ticker_flag = False

        if frequency == bar.Frequency.MINUTE:
            period = '1m'
        elif frequency == bar.Frequency.HOUR:
            period = '1h'
        elif frequency == bar.Frequency.DAY:
            period = '1d'
        elif frequency == bar.Frequency.WEEK:
            period = '1w'
        elif frequency == bar.Frequency.MONTH:
            period = '1M'
        elif frequency == bar.Frequency.SECOND:
            ticker_flag = True
        else:
            raise NotImplementedError()
        return period, ticker_flag


def get_data_info(instrument, period='', ticker_flag=False, start_date='', end_date='', limit='', **kwargs):
    """ 获取kline/ticker数据
    :param end_date: 截止日期
    :param start_date: 开始日期
    :param instrument: exchange_symbol
    :param period: kline
    :param ticker_flag: ticker
    :param kwargs:
    :return:
    """

    param = {
        'exchange': instrument.split('_', 1)[0], 'symbol': instrument.split('_', 1)[-1],
        # 'start_date': start_date, 'end_date': end_date, 'limit': limit
    }
    if limit:
        param['limit'] = limit
    else:
        param['start_date'] = start_date
        param['end_date'] = end_date

    if period:
        _method = 'kline'
        param['time_frame'] = period
        res = cli.kline(**param)
    elif ticker_flag:
        _method = 'ticker'
        res = cli.ticker(**param)
    else:
        raise NotImplementedError()
    # log.info("method:{}, res: {}".format(_method, res))

    if res and isinstance(res, list):
        _keys = [k for k in res[0].keys() if _method in k]
        datas = res[0].get(_keys[0])
        # log.info('Get data info is top 3: {}'.format(datas[:3]))
        return datas
    else:
        raise NotImplementedError()


def get_data_future_info(instrument, types, period='', ticker_flag=False, start_date='', end_date='', limit='',
                         **kwargs):
    """ 获取期货kline/ticker数据
    :param types: 获取期货那类数据，获取期货那类数据，ticker, kline, this_week_kline, this_week_ticker,
                next_week_kline, next_week_ticker, quarter_kline, quarter_ticker
    :param end_date: 截止日期
    :param start_date: 开始日期
    :param instrument: exchange_symbol
    :param period: kline
    :param ticker_flag: ticker
    :param kwargs:
    :return:
    """
    log.info("get_data_future_info param:{}, {}, {},{}".format(instrument, types, period, ticker_flag))
    param = {
        'exchange': instrument.split('_', 1)[0], 'symbol': instrument.split('_', 1)[-1],
        # 'start_date': start_date, 'end_date': end_date, 'limit': limit
    }
    if limit:
        param['limit'] = limit
    else:
        param['start_date'] = start_date
        param['end_date'] = end_date

    if ticker_flag and 'kline' in types:
        raise NotImplementedError("frequency为bar.Frequency.SECOND时，必须获取ticker数据...")
    elif ticker_flag:
        param['types'] = 'ticker'
    else:
        param['time_frame'] = period
        param['types'] = 'kline'

    if 'kline' in types:
        _method = 'kline'
    else:
        _method = 'ticker'

    if types in ['kline', 'ticker']:
        res = cli.future_kline_or_ticker(**param)
    elif types in ['this_week_kline', 'this_week_ticker']:
        res = cli.future_week_kline_ticker(**param)
    elif types in ['next_week_ticker', 'next_week_kline']:
        res = cli.future_next_week_kline_ticker(**param)
    elif types in ['quarter_kline', 'quarter_ticker']:
        res = cli.future_quarter_kline_ticker(**param)
    else:
        raise NotImplementedError()
    # log.info("获取期货数据: {}".format(res))
    if res and isinstance(res, list):
        _keys = [k for k in res[0].keys() if _method in k]
        log.info("获取期货数据列表中字典的key: {}".format(_keys))
        datas = res[0].get(_keys[0])
        # log.info('Get data info is top 3: {}'.format(datas[:3]))
        return datas
    else:
        raise NotImplementedError()


def get_data_future_index_info(instrument, types, start_date='', end_date='', limit='', **kwargs):
    """ 获取期货index数据
    :param types: 获取期货那类数据，获取期货那类数据，index
    :param end_date: 截止日期
    :param start_date: 开始日期
    :param instrument: exchange_symbol
    :param kwargs:
    :return:
    """
    param = {
        'exchange': instrument.split('_', 1)[0], 'symbol': instrument.split('_', 1)[-1],
        # 'start_date': start_date, 'end_date': end_date, 'limit': limit
    }
    res = cli.future_index(**param)

    log.info("获取期货指数数据: {}".format(res[:3]))
    if res and isinstance(res, list):
        _keys = [k for k in res[0].keys()]
        log.info("获取期货数据列表中字典的key: {}".format(_keys))
        datas = res[0].get(_keys[0])
        return datas
    else:
        raise NotImplementedError()


class Feed(membf.BarFeed):
    def __init__(self, frequency, dbConfig=None, maxLen=None):
        super(Feed, self).__init__(frequency, maxLen)
        self.db = Database()

    def barsHaveAdjClose(self):
        return False

    def loadBars(self, instrument, test_back, types='', timezone='', start_date='', end_date=''):
        """  获取交易所ticker/kline数据
        :param types: 是否为合约的标识，
        :param instrument:
        :param test_back: 回测标识，True: 表示回测，默认返回1000条数据， False: 获取时间段区间数据
        :param timezone: 时区
        :param start_date: 开始日期 与系统时间相比，不与交易所时间比较  yyyy-mm-dd hh:mm:ss or yyymmddhhmmss or yyyymmdd
        :param end_date: 截止日期 与系统时间相比，不与交易所时间比较  yyyy-mm-dd hh:mm:ss  yyymmddhhmmss or yyyymmdd
        :return:
        """
        if types is '':
            if not test_back:
                if not start_date and not end_date:
                    raise NotImplementedError('test_back is False, start_date and end_date not is empty!')
            # log.info("instrument: {}.".format(instrument))
            bars = self.db.getBars(instrument, self.getFrequency(), test_back, timezone, start_date, end_date)
            self.addBarsFromSequence(instrument, bars)
        else:
            self.loadBarsFuture(instrument, types, test_back, timezone, start_date, end_date)

    def loadBarsFuture(self, instrument, types, test_back, timezone='', start_date='', end_date='', ):
        """  获取交易所期货ticker/kline数据
        :param types: 获取期货那类数据，ticker, kline, this_week_kline, this_week_ticker,
                next_week_kline, next_week_ticker, quarter_kline, quarter_ticker
        :param instrument: exchange_symbol
        :param test_back: 回测标识，True: 表示回测，默认返回1000条数据， False: 获取时间段区间数据
        :param timezone: 时区
        :param start_date: 开始日期 与系统时间相比，不与交易所时间比较
        :param end_date: 截止日期 与系统时间相比，不与交易所时间比较
        :return:
        """
        if not test_back:
            if not start_date and not end_date:
                raise NotImplementedError('test_back is False, start_date and end_date not is empty!')
        # log.info("instrument: {}.".format(instrument))
        bars = self.db.getBarsFuture(instrument, self.getFrequency(), types, test_back, timezone, start_date, end_date)
        self.addBarsFromSequence(instrument, bars)

    def loadBarsFutureIndex(self, instrument, test_back, types='index', timezone='', start_date='', end_date='', ):
        """  获取交易所期货ticker/kline数据
        :param types: 获取期货那类数据，index
        :param instrument: exchange_symbol
        :param test_back: 回测标识，True: 表示回测，默认返回1000条数据， False: 获取时间段区间数据
        :param timezone: 时区
        :param start_date: 开始日期 与系统时间相比，不与交易所时间比较
        :param end_date: 截止日期 与系统时间相比，不与交易所时间比较
        :return:
        """
        if not test_back:
            if not start_date and not end_date:
                raise NotImplementedError('test_back is False, start_date and end_date not is empty!')
        # log.info("instrument: {}.".format(instrument))
        bars = self.db.getBarsFutureIndex(instrument, self.getFrequency(), types, test_back, timezone, start_date,
                                          end_date)
        self.addBarsFromSequence(instrument, bars)


if __name__ == '__main__':
    feed = Feed(bar.Frequency.SECOND)
    # feed.loadBars("binance_ADABTC", True)  # bitmex_XBTUSD  binance_ADABTC  okex_LIGHTBTC
    feed.loadBarsFutureIndex("okex_ltc",  True)
    # feed.loadBarsFuture("okex_ltc", 'this_week_ticker', test_back=True)

    # date_time = datetime.datetime.strptime('2018-12-27 00:07:23', '%Y-%m-%d %H:%M:%S')
    # date_time_1 = datetime.datetime.strptime('2018-12-27 00:10:20', '%Y-%m-%d %H:%M:%S')
    #
    # res = Database().date_compare(bar.Frequency.MINUTE,[date_time, 1, 1,1,2,1,2,3], date_time, date_time_1)
    # print(res)