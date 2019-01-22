#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018/8/21 下午2:21
# @Author  : datachain

import logging
import math
import time
from qbase.enum import enum
from qbase.dao import okexResultMapper, positionMapper
import qbase.okex.futures_api as future
from qbase.common import emailUtil


class Transation:

    log = None

    def __init__(self):
        self.log = logging.getLogger()

    def okexFuturesPriceAvg(self, account, symbol, tradeType):
        result = {"buyPriceAvg":0,"sellPriceAvg":0}
        if tradeType != 3 and tradeType != 4:
            return enum.TransactionResult.OK.value

        for i in range(5):
            try:
                okcoinFuture = future.FutureAPI(account.accessKey, account.secretKey, account.passphrase, use_server_time=True)
                positionResult = okcoinFuture.get_specific_position(symbol)
                # 不是全仓账号
                # if not json.loads(positionResult)[u'result']:
                #     if json.loads(positionResult)[u'error_code'] == 20022:
                #         positionResult = okcoinFuture.future_position_4fix(symbol, 'quarter', 10)
                okexPosition = positionResult
                result[u"buyPriceAvg"] = okexPosition[u'holding'][0][u'long_avg_cost']
                result[u"sellPriceAvg"] = okexPosition[u'holding'][0][u'short_avg_cost']
                ok = enum.TransactionResult.OK.value
                ok[u'data'] = result
                return ok
            except Exception as e:
                #记录
                self.log.error("！！！！！！！！！！！！查询仓位平均价异常！！！！！！！！！！！！")
                self.log.error(e)
                sub = '%s %s tradeType:%s 查询仓位平均价异常-----第%s次' % (account.future_account, symbol, tradeType, i)
                emailUtil.sendMail(subject=sub, text=str(e))
                time.sleep(i*0.3)
        return enum.TransactionResult.Fail.value

    def okexErrorFrozen(self,position , tradeType ,num):
        if tradeType == 1 or tradeType == 2:
            if position.symbol == 'eos_usd' or position.symbol == 'eth_usd':
                position.baseCoinFrozen += num * 10
            elif position.symbol == 'btc_usd':
                position.baseCoinFrozen += num * 100
        elif tradeType == 3:
            position.tradeCoinFrozen += num
        elif tradeType == 4:
            position.nullCoinFrozen += num

        positionMapper.setPositionFroze(position)

    def okexFuturesServer(self, account, position, num, tradeType):
        """
        OKEx 期货交易
        :param account:
        :param position:
        :param num:
        :param tradeType:
        :return:
        """
        # tradeType 交易类型 1 开多 2开空  3 平多 4平空
        amountNum = 0 #交易数量
        resultData = {"buyPriceAvg": 0, "sellPriceAvg": 0, "orderId": ""}
        contractName = position.openContract

        if tradeType == 1 or tradeType == 2:
            if tradeType == 1:
                position.tradeContract = contractName
                trade = '开多'
            else:
                position.nullContract = contractName
                trade = '开空'

            if position.symbol == 'eos_usd' or position.symbol == 'eth_usd':
                amountNum = math.floor((position.baseCoin - position.baseCoinFrozen) / 10)
            elif position.symbol == 'btc_usd':
                amountNum = math.floor((position.baseCoin - position.baseCoinFrozen) / 100)
            self.log.info('买入 %s  数量 %s 交易类型 : %s ' % (position.symbol, amountNum, trade))
        elif tradeType == 3 or tradeType == 4:
            if tradeType == 3:
                trade = '平多'
                contractName = position.tradeContract
                amountNum = position.tradeCoin - position.tradeCoinFrozen
            else:
                trade = '平空'
                contractName = position.nullContract
                amountNum = position.nullCoin - position.nullCoinFrozen
            self.log.info('卖出 %s  数量 %s 交易类型 : %s ' % (position.symbol, amountNum, trade))

        if amountNum < 1:
            #异常交易
            self.log.error('交易币数量不足  %s  %s' %(position.symbol , amountNum))
            return enum.TransactionResult.CoinNumFail.value
        #当前交易币小于 交易量 则交易所有交易币
        if num >= amountNum:
            num = amountNum


        if tradeType == 3 or tradeType == 4:
            # okcoinFuture = future.FutureAPI(account.accessKey, account.secretKey, account.passphrase, use_server_time=True)
            okexPriceAvgResult = self.okexFuturesPriceAvg(account, position.openContract, tradeType)
            if okexPriceAvgResult[u'code'] != 1000:
                return okexPriceAvgResult
            resultData[u"buyPriceAvg"] = okexPriceAvgResult[u'data'][u'buyPriceAvg']
            resultData[u"sellPriceAvg"] = okexPriceAvgResult[u'data'][u'sellPriceAvg']

        for i in range(10):
            try:
                okcoinFuture = future.FutureAPI(account.accessKey, account.secretKey, account.passphrase, use_server_time=True)
                resultJson = okcoinFuture.take_order(client_oid='', instrument_id=position.openContract, otype=tradeType, price='', size=str(int(num)), match_price='1', leverage='10')
                break
                # resultJson = okcoinFuture.future_trade(position.symbol, contractType='quarter', price='', amount=num,
                #                                        tradeType=tradeType, matchPrice='1', leverRate='10')
            except Exception as e:
                #记录
                self.log.error("！！！！！！！！！！！！okex交易抛出异常！！！！！！！！！！！！")
                self.log.error(e)
                sub = '%s %s %s tradeType:%s okex交易抛出异常-----第%s次' % (position.account, position.strategy, position.symbol, tradeType, i)
                emailUtil.sendMail(subject=sub, text=str(e))
                if e.code == 32019:
                    time.sleep(i*3)
                    continue
                self.okexErrorFrozen(position, tradeType, num)
                return enum.TransactionResult.Fail.value

        if resultJson == '' or resultJson is None:
            self.log.error("！！！！！！！！！！！！okex交易返回异常 result为空！！！！！！！！！！！！")
            self.okexErrorFrozen(position, tradeType, num)
            sub = '%s %s %s tradeType:%s 下单出错' % (position.account, position.strategy, position.symbol, tradeType)
            emailUtil.sendMail(subject=sub, text='okex交易返回异常 result为空！')
            return enum.TransactionResult.Fail.value
        if not resultJson[u'result']:
            self.log.error("********************okex交易失败********************")
            self.log.error(resultJson)
            sub = '%s %s %s tradeType:%s okex交易失败' % (position.account, position.strategy, position.symbol, tradeType)
            emailUtil.sendMail(subject=sub, text=str(resultJson))
            return enum.TransactionResult.Fail.value
        else:
            if resultJson[u'order_id'] == '':
                #记录
                self.log.error("！！！！！！！！！！！！okex交易返回异常 result中orderId为空！！！！！！！！！！！！")
                self.okexErrorFrozen(position, tradeType, num)
                sub = '%s %s %s tradeType:%s okex交易返回异常 result中orderId为空' % (position.account, position.strategy, position.symbol, tradeType)
                emailUtil.sendMail(subject=sub, text=str(resultJson))
                return enum.TransactionResult.ResultOrderIdFail.value
            else:
                self.log.info(resultJson)
                resultOrder = enum.TransactionResult.OK.value

                resultData[u"orderId"] = resultJson[u"order_id"]
                resultOrder[u'data'] = resultData
                return resultOrder

    def okexResult(self,account , position ,mapData ,tradeType, num):
        okcoinFuture = future.FutureAPI(account.accessKey, account.secretKey, account.passphrase, use_server_time=True)
        self.log.info('查询OKEx交易结果 订单ID %s' %mapData[u"orderId"])
        i = 1
        state = -10
        #循环5次 如果没有成功就撤单   如果撤单失败记录异常冻结
        while i < 6:
            time.sleep(0.5 * i)
            i += 1
            self.log.info('查询OKEx交易结果 第 %s 次 | 订单ID %s ' % (i, mapData[u"orderId"]))
            try:
                # orderResultJson = okcoinFuture.future_orderinfo(position.symbol, contractType='quarter',
                #                                                 orderId=mapData[u"orderId"],
                #                                                 status="2", currentPage="1", pageLength="50")
                orderResultJson = okcoinFuture.get_order_info(order_id=mapData[u'orderId'], instrument_id=position.openContract)
                state = int(orderResultJson[u'status'])
                if state == 2:
                    break
            except Exception as e:
                # 记录
                self.log.error("！！！！！！！！！！！！okex交易结果查询异常！！！！！！！！！！！！")
                self.log.error(e)
                sub = '%s %s %s tradeType:%s okex交易结果查询异常---第%s次' % (position.account, position.strategy, position.symbol, tradeType, i)
                emailUtil.sendMail(subject=sub, text=str(e))

        self.log.info('查询交易结果  %s' % orderResultJson)

        isError = False
        if orderResultJson == '' or orderResultJson is None or state == 0 or state == 1:
            try:
                # cancelResult = okcoinFuture.future_cancel(position.symbol, contractType='quarter', orderId=mapData[u"orderId"])
                cancelResult = okcoinFuture.revoke_order(instrument_id=position.openContract, order_id=mapData[u'orderId'])
                time.sleep(0.5)
                if cancelResult[u'result'] or (not cancelResult[u'result'] and int(cancelResult[u'error_code']) == 32029):
                    self.log.info("********************okex交易撤单成功  订单ID %s ********************" % mapData[u"orderId"])
                    # orderResultJson = okcoinFuture.future_orderinfo(position.symbol, contractType='quarter',
                    #                                                 orderId=mapData[u"orderId"],
                    #                                                 status="2", currentPage="1", pageLength="50")
                    orderResultJson = okcoinFuture.get_order_info(order_id=mapData[u'orderId'], instrument_id=position.openContract)
                else:
                    orderResultJson = okcoinFuture.get_order_info(order_id=mapData[u'orderId'], instrument_id=position.openContract)
                    state = int(orderResultJson[u'status'])
                    if state != 2:
                        self.okexErrorFrozen(position, tradeType, num)
                        self.log.error(cancelResult)
                        self.log.error("！！！！！！！！！！！！okex交易撤单失败！！！！！！！！！！！！")
                        sub = '%s %s %s tradeType:%s okex交易撤单失败' % (position.account, position.strategy, position.symbol, tradeType)
                        emailUtil.sendMail(subject=sub, text=str(orderResultJson))
                        isError = True
            except Exception as e:
                self.okexErrorFrozen(position, tradeType, num)
                self.log.error(e)
                self.log.error("！！！！！！！！！！！！okex交易撤单异常！！！！！！！！！！！！")
                sub = '%s %s %s tradeType:%s okex交易撤单异常' % (position.account, position.strategy, position.symbol, tradeType)
                emailUtil.sendMail(subject=sub, text=str(e))
                isError = True

        if orderResultJson == '' or orderResultJson is None:
            self.okexErrorFrozen(position, tradeType, num)
            self.log.error(cancelResult)
            self.log.error("！！！！！！！！！！！！okex交易查询交易结果失败！！！！！！！！！！！！")
            sub = '%s %s %s tradeType:%s okex交易查询交易结果失败' % (position.account, position.strategy, position.symbol, tradeType)
            emailUtil.sendMail(subject=sub, text=str(cancelResult))
            return enum.TransactionResult.Fail.value

        resultJson = orderResultJson
        okexResultJson = resultJson
        # 记录交易结果到表中
        okexResultMapper.insertOkexResult(position.id, okexResultJson)

        if isError:
            return enum.TransactionResult.Fail.value

        type = int(okexResultJson[u'type'])

        dealPrice = int(okexResultJson[u'contract_val'])
        #卖出/买入数量
        dealAmount = float(okexResultJson[u'filled_qty'])
        priceAvg = float(okexResultJson[u'price_avg'])
        fee = float(okexResultJson[u'fee'])

        #有交易成交更新仓位
        if dealAmount > 0:
            #扣除手续费
            position.baseCoin += fee

            if type == 1 or type == 2 :
                position.baseCoin -= dealAmount * dealPrice
                if type == 1:
                    position.tradeCoin += dealAmount
                else:
                    position.nullCoin += dealAmount
            elif type == 3 or type == 4:
                if type == 3:
                    openPriceAvg = float(mapData[u'buyPriceAvg'])  # 查仓位的结算基准价
                    profitCoin = dealPrice / openPriceAvg - dealPrice / priceAvg
                    position.tradeCoin -= dealAmount
                else :
                    openPriceAvg = float(mapData[u'sellPriceAvg'])  # 查仓位的结算基准价
                    profitCoin = dealPrice / priceAvg - dealPrice / openPriceAvg
                    position.nullCoin -= dealAmount

                position.baseCoin += dealAmount * dealPrice + dealAmount * profitCoin * priceAvg

            positionMapper.setPosition(position)
        return enum.TransactionResult.OK.value

    def send(self, exchange, account, position, num, tradeType):
        """
        发送 买入/卖出 代币申请
        :param exchange: 交易所
        :param strategy: 策略
        :param symbol:  币种
        :param accountType: 交易账号类型
        :param isbuy:  买入/卖出表示 1买入 2卖出
        :param tradeType:   交易类型  okex 买入使用  1开多   2开空
        :return:
        """
        if type(exchange).__name__ != 'Exchange':
            raise RuntimeError('exchange must be an Exchange enum')

        self.log.info('-----------------------------------------------------------------')
        self.log.info(u"交易所 : %s " % exchange.value)
        self.log.info(u"交易用户 : %s " % account.accessKey)
        if position is None:
            self.log.info(" %s 没有可以交易的仓位" % account.accessKey)
            return enum.TransactionResult.NoCanPositionFail.value
        elif exchange == enum.Exchange.OKEx:
            okexServerResult = self.okexFuturesServer(account, position, num, tradeType)
            if okexServerResult[u'code'] != 1000:
                return okexServerResult

            self.okexResult(account, position, okexServerResult[u'data'], tradeType, num)
            return enum.TransactionResult.OK.value
