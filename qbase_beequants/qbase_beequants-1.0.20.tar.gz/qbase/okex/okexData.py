#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-8-6 15:40:03
# @Author  : datachain

import websocket
import time
import json
import zlib
import threading
import logging

from qbase.common import mmaper
from qbase.okex import futures_api
from qbase.common import until

log = logging.getLogger()

# TODO 从配置中取参数

# 币币交易
WS_SPOT_URL = "wss://okexcomreal.bafang.com:10441/websocket"
# 合约交易
WS_FUTURES_URL = "wss://okexcomreal.bafang.com:10441/websocket"

klinFormat = {'id': 1234567890, 'open': 9999999999.9999999999, 'close': 9999999999.9999999999, 'low': 9999999999.9999999999, 'high': 9999999999.9999999999, 'amount': 9999999999.9999999999, 'vol': 9999999999.9999999999, 'count': 999999999999}

def klinDataCopy(res, des):
    des[u'id'] = res[u'id']
    des[u'open'] = res[u'open']
    des[u'close'] = res[u'close']
    des[u'low'] = res[u'low']
    des[u'high'] = res[u'high']
    des[u'amount'] = res[u'amount']
    des[u'vol'] = res[u'vol']
    des[u'count'] = res[u'count']

def klineData(datas):
    """
        "id": K线id,
        "amount": 成交量,
        "count": 成交笔数,
        "open": 开盘价,
        "close": 收盘价,当K线为最晚的一根时，是最新成交价
        "low": 最低价,
        "high": 最高价,
        "vol": 成交额, 即 sum(每一笔成交价 * 该笔的成交量)
    """
    # [时间 ,开盘价,最高价,最低价,收盘价,成交量(张),成交量(币)]
    dest = {}
    if len(datas) >= 7:
        id = int(datas[0])
        dest["id"] = id//1000
        dest["open"] = float(datas[1])
        dest["high"] = float(datas[2])
        dest["low"] = float(datas[3])
        dest["close"] = float(datas[4])
        dest["amount"] = float(datas[5])
        dest["vol"] = float(datas[6])
        dest["count"] = 0
    return dest
def getKLineDataFrommarket(intrustment_id, interval, dataNum, transactionType = "futures"):

    """
    获取k线数据并放入mmap
    :param instrustment_id: str  合约名称eg. BTC-USD-181228
    :param interval:  int  k线周期，单位秒,必须是60，300，3600 等符合OK的数据
    :param dataNum:  int 存储数据量  eg. 20 存储20个周期数据
    :param transactionType:  str 交易类型
                            "spot": 币币交易
                            "futures": 合约交易
                            默认合约交易
    """
    symbol = intrustment_id[0:3].lower()
    log = logging.getLogger()
    # init a mmap with write mode
    mmapSize = klinFormat.__sizeof__() * (dataNum + 1)
    mpW = mmaper.Mmaper('mmapData/' + transactionType + "_" + symbol + '_' + str(interval) + '.dat', mmapSize, 'W')
    Future = futures_api.FutureAPI('','','',True)
    pastData = Future.get_kline(intrustment_id,interval)
    pastData = pastData[1:dataNum]
    pastData.reverse()
    pastresultData=[klineData(x) for x in pastData]
    while True:
        time.sleep(1)
        if int(time.time()) % interval == 5:
            try:
                while 1:
                    Future = futures_api.FutureAPI('','','',True)
                    Data = Future.get_kline(intrustment_id,interval)
                    Data = Data[1:dataNum]
                    Data.reverse()
                    resultData=[klineData(x) for x in Data]
                    if resultData[-1]['id'] - pastresultData[-1]['id'] == interval:
                        mpW.writeDataToMmap(json.dumps(resultData).ljust(mmapSize, '\x00').encode())
                        pastresultData = resultData.copy()
                        break
                    time.sleep(1)
            except Exception as e:
                log.info(e)
    # close the map
    mpW.closeMmap()

def getKLineDataFrommarke2(intrustment_id, interval, dataNum, type='quarter', transactionType = "futures"):

    """
    获取k线数据并放入mmap
    :param instrustment_id: str  合约名称eg. BTC-USD-181228
    :param interval:  int  k线周期，单位秒,必须是60，300，3600 等符合OK的数据
    :param dataNum:  int 存储数据量  eg. 20 存储20个周期数据
    :param type: str v1 websocket 需要，this_week, next_week, quarter
    :param transactionType:  str 交易类型
                            "spot": 币币交易
                            "futures": 合约交易
                            默认合约交易
    """
    symbol = intrustment_id[0:3].lower()
    if interval < 3600:
        period = '%dmin' % (interval/60)
    elif interval < 24*3600:
        period = '%dhour' % (interval/3600)
    elif interval < 7 * 24 * 3600:
        period = '%dday' % (interval/3600/24)
    else:
        period = 'week'
    # 定义日志
    log = logging.getLogger()
    # init a mmap with write mode
    mmapSize = klinFormat.__sizeof__() * (dataNum + 1)
    mpW = mmaper.Mmaper('mmapData/' + transactionType + "_" + symbol + '.dat', mmapSize, 'W')

    Future = futures_api.FutureAPI('','','',True)
    pastData = Future.get_kline(intrustment_id,interval)
    pastData = pastData[0:dataNum]
    pastData.reverse()
    resultData=[klineData(x) for x in pastData]

    if transactionType == "spot":
        log.info('spot is not supported')
        return
        # 币币交易
        channel = "ok_sub_spot_%s_usdt_kline_1min" % (symbol)
        subKline = "{'event':'addChannel','channel':'%s'}" % channel
        wsUrl = WS_SPOT_URL

    else:
        # 合约交易
        channel = "ok_sub_futureusd_%s_kline_%s_%s" % (symbol, type, period)
        subKline = "{'event':'addChannel','channel':'%s'}" % channel
        wsUrl = WS_FUTURES_URL

    def on_message(ws, message):
        data = inflate(message)
        for x in json.loads(data):
            if "channel" in x and x.get("channel") == channel:
                for datas in x.get("data"):
                    # 推送过来的K线数据
                    kline_data = klineData(datas)
                    print(kline_data)
                    if kline_data['id'] == resultData[-1]['id']:
                        resultData[-1] = kline_data.copy()
                    else:
                        mpW.writeDataToMmap(json.dumps(resultData).ljust(mmapSize, '\x00').encode())
                        resultData.pop(0)
                        resultData.append(kline_data)

    def on_error(ws, error):
        log.error("websocket errer")
        log.error(error)

    def on_close(ws):
        log.info("websocket closed")
        time.sleep(3)
        service()

    def on_open(ws):
        def run(*args):
            ws.send(subKline)
            while True:
                time.sleep(30)
                ws.send("{'event':'ping'}")

        # log.info("connection time is " + str(datetime.now()))
        threading.Thread(target=run, name='LoopThread').start()


    def service():
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp(wsUrl,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)

        ws.on_open = on_open
        ws.run_forever()

    service()

    # close the map
    mpW.closeMmap()

def getKLineDataFrommarket1(symbol, interval, dataNum, transactionType = "futures", unit="hour"):
    """
    获取k线数据并放入mmap
    :param symbol:  币种 eg. eos btc
    :param interval:    k线周期，以unit参数为单位
    :param dataNum: 存储数据量  eg. 20 存储20个周期数据
    :param transactionType: 交易类型
                            "spot": 币币交易
                            "futures": 合约交易
                            默认合约交易
    :param unit: 单位 默认min min/hour/day
    """
    # 定义日志
    log = logging.getLogger()
    # init a mmap with write mode
    mmapSize = klinFormat.__sizeof__() * (dataNum + 1)
    mpW = mmaper.Mmaper('mmapData/' + transactionType + "_" + symbol + '.dat', mmapSize, 'W')

    nextWholeTime = 0  # 下一个整点时间

    tmpResultData = {'id': 0, 'open': 0, 'close': 0, 'low': 0, 'high': 0, 'amount': 0, 'vol': 0,
                     'count': 0}  # 推送数据临时缓存区
    lastMinResultData = {'id': 0, 'open': 0, 'close': 0, 'low': 0, 'high': 0, 'amount': 0, 'vol': 0,
                         'count': 0}  # 1分钟KLin数据
    lastResultData = {'id': 0, 'open': 0, 'close': 0, 'low': 0, 'high': 0, 'amount': 0, 'vol': 0,
                      'count': 0}  # 最后一个周期的临时数据
    resultData = []

    if transactionType == "spot":
        # 币币交易
        channel = "ok_sub_spot_%s_usdt_kline_1min" % (symbol)
        subKline = "{'event':'addChannel','channel':'%s'}" % channel
        wsUrl = WS_SPOT_URL

    else:
        # 合约交易
        channel = "ok_sub_futureusd_%s_kline_quarter_1min" % (symbol)
        subKline = "{'event':'addChannel','channel':'%s'}" % channel
        wsUrl = WS_FUTURES_URL

    def on_message(ws, message):
        nonlocal nextWholeTime
        data = inflate(message)
        for x in json.loads(data):
            if "channel" in x and x.get("channel") == channel:
                for datas in x.get("data"):
                    # 推送过来的K线数据
                    kline_data = klineData(datas)

                    # 初始化缓存变量
                    if lastResultData[u'id'] == 0:
                        klinDataCopy(kline_data, lastResultData)
                    if lastMinResultData[u'id'] == 0:
                        klinDataCopy(kline_data, lastMinResultData)
                    if tmpResultData[u'id'] == 0:
                        klinDataCopy(kline_data, tmpResultData)
                    # 首次将取下一个整点时间
                    if nextWholeTime == 0:
                        nextWholeTime = until.getWholeTime(kline_data[u'id'], interval)
                    # 判断数据重复推送，如果重复推送不处理
                    if tmpResultData != kline_data:
                        # 将推送数据缓存到临时缓存区
                        klinDataCopy(kline_data, tmpResultData)
                        # 如果没到整点处理上一个周期数据
                        if tmpResultData[u'id'] < nextWholeTime:
                            # 判断是否是同一分钟的推送
                            if lastMinResultData[u'id'] == tmpResultData[u'id']:
                                # 如果是一分钟，更新一分钟数据
                                lastMinResultData[u'close'] = tmpResultData[u'close']
                                lastMinResultData[u'low'] = min(lastMinResultData[u'low'], tmpResultData[u'low'])
                                lastMinResultData[u'high'] = max(lastMinResultData[u'high'], tmpResultData[u'high'])
                                lastMinResultData[u'amount'] = tmpResultData[u'amount']
                                lastMinResultData[u'vol'] = tmpResultData[u'vol']
                                lastMinResultData[u'count'] = tmpResultData[u'count']
                                # 更新最后动态数据lastResultData
                                lastResultData[u'close'] = lastMinResultData[u'close']
                                lastResultData[u'low'] = min(lastResultData[u'low'], lastMinResultData[u'low'])
                                lastResultData[u'high'] = max(lastResultData[u'high'], lastMinResultData[u'high'])
                            else:
                                # 更新最后动态数据lastResultData
                                lastResultData[u'amount'] += lastMinResultData[u'amount']
                                lastResultData[u'vol'] += lastMinResultData[u'vol']
                                lastResultData[u'count'] += lastMinResultData[u'count']
                                # 新的一分钟，全量刷新一分钟数据
                                lastMinResultData[u'id'] = tmpResultData[u'id']
                                lastMinResultData[u'open'] = tmpResultData[u'open']
                                lastMinResultData[u'close'] = tmpResultData[u'close']
                                lastMinResultData[u'low'] = tmpResultData[u'low']
                                lastMinResultData[u'high'] = tmpResultData[u'high']
                                lastMinResultData[u'amount'] = tmpResultData[u'amount']
                                lastMinResultData[u'vol'] = tmpResultData[u'vol']
                                lastMinResultData[u'count'] = tmpResultData[u'count']
                        # 超过下一个整点，固定上一个周期KLin值，重新开始下一个周期
                        else:
                            log.info(lastResultData)
                            if len(resultData) < dataNum:
                                resultData.append(json.loads(json.dumps(lastResultData)))
                            else:
                                del resultData[0]
                                resultData.append(json.loads(json.dumps(lastResultData)))
                            # 将本次的Klin数据放到到下一个周期
                            klinDataCopy(kline_data, lastResultData)
                            klinDataCopy(kline_data, lastMinResultData)
                            klinDataCopy(kline_data, tmpResultData)
                            nextWholeTime = until.getWholeTime(lastResultData[u'id'], interval)
                        # 刷新周后一个周期
                        if len(resultData) == 0:
                            resultData.append(json.loads(json.dumps(lastResultData)))
                        else:
                            resultData[len(resultData) - 1] = json.loads(json.dumps(lastResultData))
                        mpW.writeDataToMmap(json.dumps(resultData).ljust(mmapSize, '\x00').encode())

    def on_error(ws, error):
        log.error("websocket errer")
        log.error(error)

    def on_close(ws):
        log.info("websocket closed")
        time.sleep(3)
        service()

    def on_open(ws):
        def run(*args):
            ws.send(subKline)
            while True:
                time.sleep(30)
                ws.send("{'event':'ping'}")

        # log.info("connection time is " + str(datetime.now()))
        threading.Thread(target=run, name='LoopThread').start()


    def service():
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp(wsUrl,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)

        ws.on_open = on_open
        ws.run_forever()

    service()

    # close the map
    mpW.closeMmap()

# 解压消息
def inflate(message):
    try:
        decompress = zlib.decompressobj(
                -zlib.MAX_WBITS  # see above
        )
        inflated = decompress.decompress(message)
        inflated += decompress.flush()
        inflated = inflated.decode('utf-8', errors='ignore')
    except:
        inflated = message
    return inflated

def getWSdata(symbol, interval, transactionType = "futures", dataNum = 5):
    """
    获取k线数据并放入mmap
    :param symbol:  币种 eg. eos btc
    :param interval:    k线周期，以unit参数为单位
    :param dataNum: 存储数据量  eg. 20 存储20个周期数据
    :param transactionType: 交易类型
                            "spot": 币币交易
                            "futures": 合约交易
                            默认合约交易
    :param unit: 单位 默认min min/hour/day
    """
    # 定义日志
    log = logging.getLogger()
    # init a mmap with write mode
    mmapSize = klinFormat.__sizeof__() * (dataNum + 1)
    if interval < 3600:
        period = '%dmin' % (interval//60)
    elif interval < 24*3600:
        period = '%dhour' % (interval//3600)
    elif interval < 7 * 24 * 3600:
        period = '%dday' % (interval//3600//24)
    else:
        period = 'week'

    mpW = mmaper.Mmaper('mmapData/' + transactionType + "_" + symbol + '_' + str(interval) + '_WS.dat', mmapSize, 'W')

    if transactionType == "spot":
        # 币币交易
        channel = "ok_sub_spot_%s_usdt_kline_1min" % (symbol)
        subKline = "{'event':'addChannel','channel':'%s'}" % channel
        wsUrl = WS_SPOT_URL

    else:
        # 合约交易
        channel = "ok_sub_futureusd_%s_kline_quarter_%s" % (symbol, period)
        subKline = "{'event':'addChannel','channel':'%s'}" % channel
        wsUrl = WS_FUTURES_URL

    def on_message(ws, message):
        data = inflate(message)
        for x in json.loads(data):
            if "channel" in x and x.get("channel") == channel:
                result_data = klineData(x.get('data')[0])
                print(result_data)
                mpW.writeDataToMmap(json.dumps(result_data).ljust(mmapSize, '\x00').encode())

    def on_error(ws, error):
        log.error("websocket errer")
        log.error(error)

    def on_close(ws):
        log.info("websocket closed")
        time.sleep(3)
        service()

    def on_open(ws):
        def run(*args):
            ws.send(subKline)
            while True:
                time.sleep(20)
                ws.send("{'event':'ping'}")

        # log.info("connection time is " + str(datetime.now()))
        threading.Thread(target=run, name='LoopThread').start()


    def service():
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp(wsUrl,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)

        ws.on_open = on_open
        ws.run_forever()

    service()

    # close the map
    mpW.closeMmap()
if __name__ == "__main__":
    getWSdata('btc',7200)