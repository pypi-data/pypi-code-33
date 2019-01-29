#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    :  下午2:10
# @Author  : datachain

import logging
import threading,time
from qbase.dao import positionMapper
from qbase.transaction import transactions

def unlock(lock):
    lock.notify()
    lock.release()
    time.sleep(0.1)

class Buy(threading.Thread):
    def __init__(self, lockCon,exchange , account, accountNo, strategy, symbol ,signal,positionSignal):
        threading.Thread.__init__(self)
        self.lockCon = lockCon
        self.exchange = exchange
        self.account = account
        self.accountNo = accountNo
        self.strategy = strategy
        self.symbol = symbol
        self.signal = signal
        self.positionSignal = positionSignal
        self.log = logging.getLogger()
        self.setName(str(accountNo) + "-" + str(strategy) + "-" + str(symbol) + "-buy")



    def run(self):
        while True:
            self.lockCon.acquire()
            if not self.positionSignal.isBuy and not self.positionSignal.isSell:
                unlock(self.lockCon)
                self.log.info("buy:isBuy[%s],isSell[%s]" %(self.positionSignal.isBuy ,self.positionSignal.isSell))
                break
            if not self.signal.isBuy:
                unlock(self.lockCon)
                self.log.debug("buy:isBuy[%s]" % self.positionSignal.isBuy)
                continue

            position = positionMapper.getPosition(self.accountNo, self.strategy,self.symbol)

            # 购买类型不是 1 并且也不是 2
            if self.signal.buyTradeType != 1 and self.signal.buyTradeType != 2:
                unlock(self.lockCon)
                self.positionSignal.isBuy = False
                continue
            #发起交易
            result = transactions.Transation().send(self.exchange, self.account, position, self.signal.buyNum, self.signal.buyTradeType)
            self.log.info(result)
            if (result[u'code'] == 2001 or result[u'code'] == 2002) and not self.positionSignal.isSell :
                unlock(self.lockCon)
                self.positionSignal.isBuy = False
                continue

            self.positionSignal.isBuy = True
            unlock(self.lockCon)




class Sell(threading.Thread):
    def __init__(self, lockCon,exchange , account, accountNo, strategy, symbol ,signal,positionSignal):
        threading.Thread.__init__(self)
        self.lockCon = lockCon
        self.exchange = exchange
        self.account = account
        self.accountNo = accountNo
        self.strategy = strategy
        self.symbol = symbol
        self.signal = signal
        self.positionSignal = positionSignal
        self.log = logging.getLogger()
        self.setName(str(accountNo) + "-" + str(strategy) + "-" + str(symbol) + "-sell")

    def run(self):
        while True:
            self.lockCon.acquire()
            if not self.positionSignal.isBuy and not self.positionSignal.isSell:
                unlock(self.lockCon)
                self.log.info("sell:isBuy[%s],isSell[%s]" % (self.positionSignal.isBuy, self.positionSignal.isSell))
                break
            if not self.signal.isSell:
                unlock(self.lockCon)
                self.log.debug("sell:isSell[%s]" % self.positionSignal.isSell)
                continue

            position = positionMapper.getPosition(self.accountNo, self.strategy, self.symbol)

            if self.signal.sellTradeType != 1 and self.signal.sellTradeType != 2:
                unlock(self.lockCon)
                self.positionSignal.isSell = False
                continue
                # 发起交易
            tradeType = self.signal.sellTradeType + 2
            result = transactions.Transation().send(self.exchange, self.account, position, self.signal.sellNum, tradeType)
            self.log.info(result)
            if result[u'code'] == 2001 or result[u'code'] == 2002:
                unlock(self.lockCon)
                self.positionSignal.isSell = False
                continue
            unlock(self.lockCon)

