#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum


class Signal(Enum):
    """
    买卖信号枚举
    """
    LONG = "1"
    SHORT = "-1"
    CLOSE_LONG = "-2"
    CLOSE_SHORT = "2"
    NO_SIGNAL = "0"


class check_pro_los:

    def __init__(self, loss=None, profit=[]):

        '''
        :param loss: 最大亏损 float
        :param profit: 盈利回撤 list  [[0.02 1],[0.05, 0.3]]
        '''

        self.loss = loss
        self.profit = profit
        self.high = 0
        self.low = float('inf')

    def check(self, lastPrice, buyPrice, lastSignal):
        shift = 0.00000001
        max_benefit = 0
        max_retrive = 0
        max_loss = 0
        signal = Signal.NO_SIGNAL
        # print('buy:', buyPrice,'last:', lastPrice)
        # 多头
        if lastSignal == Signal.LONG:
            # 止损
            if self.loss is not None:
                if lastPrice < self.low:
                    self.low = lastPrice
                    # print('LONG  low:', self.low)
                max_loss = self.low / buyPrice - 1
                if max_loss < self.loss:
                    signal = Signal.CLOSE_LONG
            # 止盈
            if len(self.profit) != 0:
                if lastPrice > self.high:
                    self.high = lastPrice
                    # print('LONG  high:', self.high)
                max_benefit = self.high / buyPrice - 1
                max_retrive = (self.high - lastPrice + shift) / (self.high - buyPrice + shift)
                for cond in self.profit:
                    if max_benefit < cond[0]:
                        break
                if max_benefit > self.profit[0][0] and max_retrive > cond[1]:
                    signal = Signal.CLOSE_LONG

        # 空头
        elif lastSignal == Signal.SHORT:
            # 止损
            if self.loss is not None:
                if lastPrice > self.high:
                    self.high = lastPrice
                    # print('SHORT  high:', self.high)
                max_loss = 1 - self.high / buyPrice
                if max_loss < self.loss:
                    signal = Signal.CLOSE_SHORT
            # 止盈
            if len(self.profit) != 0:
                if lastPrice < self.low:
                    self.low = lastPrice
                    # print('SHORT  low:', self.low)
                max_benefit = 1 - self.low / buyPrice
                max_retrive = (lastPrice - self.low + shift) / (buyPrice - self.low + shift)
                for cond in self.profit:
                    if max_benefit < cond[0]:
                        break
                if max_benefit > self.profit[0][0] and max_retrive > cond[1]:
                    signal = Signal.CLOSE_SHORT
        if signal != Signal.NO_SIGNAL:
            self.high = 0
            self.low = float('inf')
        return signal, max_benefit, max_retrive, max_loss


