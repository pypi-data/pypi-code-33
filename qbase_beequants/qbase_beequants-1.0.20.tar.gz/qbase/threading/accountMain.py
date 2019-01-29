#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018/8/22 下午1:38
# @Author  : datachain
from qbase.dao import accountMapper
from qbase.threading import transaction
from qbase.enum import enum
from qbase.entity import signal
import threading

class AccountMain(threading.Thread):
    def __init__(self , exchange , accountType , strategy , symbol , mainSignal):
        if type(exchange).__name__ != 'Exchange':
            raise RuntimeError('exchange must be an Exchange enum')
        if type(accountType).__name__ != 'AccountType':
            raise RuntimeError('accountType must be an AccountType enum')
        threading.Thread.__init__(self)
        self.exchange = exchange
        self.accountType = accountType
        self.strategy = strategy
        self.symbol = symbol
        self.mainSignal = mainSignal
        self.cv = mainSignal.lockCon
        self.cv.acquire()
        self.start()

    def run(self):
        positionSignalList = []
        while True:
            self.cv.acquire()

            if type(self.exchange).__name__ != 'Exchange':
                raise RuntimeError('exchange must be an Exchange enum')
            accountList = accountMapper.getAccountByExchange(str(self.exchange.value))

            for i in range(len(accountList)):
                # 是否启动过
                isStart = False
                account = accountList.iloc[i]

                positionSignalId = str(account.id) + self.strategy + self.symbol
                for pSignal in positionSignalList:
                    if not pSignal.isBuy and not pSignal.isSell:
                        positionSignalList.remove(pSignal)
                        continue
                    if pSignal.id == positionSignalId:
                        isStart = True
                        break

                if isStart:
                    continue

                lockCon = threading.Condition()

                threads = []
                if type(self.accountType).__name__ != 'AccountType':
                    raise RuntimeError('accountType must be an AccountType enum')
                if self.accountType == enum.AccountType.Spot:
                    accountNo = account.spotAccount
                elif self.accountType == enum.AccountType.Futures:
                    accountNo = account.futuresAccount
                else:
                    accountNo = account.otherAccount

                positionSignal = signal.PositionSignal(positionSignalId).setPositionSignal(self.mainSignal)

                threads.append(transaction.Sell(lockCon,self.exchange,account, accountNo, self.strategy, self.symbol, self.mainSignal, positionSignal))
                threads.append(transaction.Buy(lockCon, self.exchange,account, accountNo, self.strategy, self.symbol, self.mainSignal, positionSignal))

                positionSignalList.append(positionSignal)
                for t in threads:
                    t.start()


