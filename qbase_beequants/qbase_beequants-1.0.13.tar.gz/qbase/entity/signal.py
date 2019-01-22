#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018/8/22 下午5:59
# @Author  : datachain
import threading
class Signal:
    isBuy = False
    buyTradeType = 0 #买什么  1多区  2空区
    buyNum = 0 #买多少
    isSell = False
    sellTradeType = 0  #卖什么  1多区 2空区
    sellNum = 0 #卖多少
    lockCon = threading.Semaphore(1)

    def awaken(self):
        self.lockCon.release()

    def __init__(self):
        pass

    def setBuy(self,isbuy , tradeType, buyNum):
        self.isBuy = isbuy
        self.buyTradeType = tradeType
        self.buyNum = buyNum

    def setSell(self,isSell , tradeType, sellNum):
        self.isSell = isSell
        self.sellTradeType = tradeType
        self.sellNum = sellNum



class PositionSignal:
    id = ''
    isBuy = False
    isSell = False

    def __init__(self ,id):
        self.id = id

    def setPositionSignal(self,signal):
        self.isBuy = signal.isBuy
        self.isSell = signal.isSell
        return self

    def getPositionSignal(self):
        return self