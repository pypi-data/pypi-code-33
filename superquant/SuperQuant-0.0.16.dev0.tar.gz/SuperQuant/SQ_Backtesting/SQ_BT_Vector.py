import pandas as pd
import numpy as np
import random
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn
seaborn.set(palette='deep',style='darkgrid')
import QUANTAXIS as QA


class SQ_BT_Vector_main():
    def __init__(self, data=None, commision_coef=0.00025, fac='close', freq='1Day'):
        '''
        :param data: DataFrame, 列含[fac,'SQ_position'], 索引为单时间序列
        :param commision_coef:
        :param fac:
        :param freq:
        '''
        self.BT = data.copy()
        self.commision_coef = commision_coef
        self.fac = fac
        self.freq = freq

    def get_result(self):
        self.BT_statistic = dict()
        self.BT['return'] = self.BT[self.fac].pct_change().shift(-1)
        self.BT['strategy'] = self.BT['SQ_position'] * self.BT['return']

        self.BT['strategy'] = np.where(self.BT['SQ_position'] != self.BT['SQ_position'].shift(1),
                                       self.BT['strategy'] - (self.commision_coef / 2), self.BT['strategy'])

        if self.freq == '1Day':
            self.BT['cum_strategy'] = (self.BT['strategy'] + 1).cumprod()
            self.BT['cum_strategy'] = self.BT['cum_strategy'].fillna(method='ffill')

            fig = plt.figure(figsize=(20, 10))
            figp = fig.subplots(1, 1)
            figp.xaxis.set_major_locator(ticker.MultipleLocator(50))
            figp.plot(self.BT['cum_strategy'])

            annual_rtn = pow(self.BT['cum_strategy'].iloc[-1] / self.BT['cum_strategy'].iloc[0], 250 / len(self.BT)) - 1
            self.BT['ex_pct_close'] = self.BT['strategy'] - 0.02 / 252

            P1 = round(self.BT[self.BT['strategy'] > 0].shape[0] / self.BT[self.BT['strategy'] != 0].shape[0] * 100, 2)
            P2 = round(annual_rtn * 100, 2)
            P3 = round(SQ_BT_Vector_maximum_down(self.BT[['cum_strategy']].values)[0][0] * 100, 2)
            P4 = round(self.BT[self.BT['strategy'] > 0]['strategy'].mean() / abs(
                self.BT[self.BT['strategy'] < 0]['strategy'].mean()), 2)
            P5 = round((self.BT['ex_pct_close'].mean() * math.sqrt(252)) / self.BT['ex_pct_close'].std(), 2)
            P6 = round(self.BT.shape[0] / self.BT[self.BT['strategy'] != 0].shape[0], 2)

        print('胜率: ' + str(P1) + '%')
        print('年化收益率：' + str(P2) + '%')
        print('最大回撤：' + str(P3) + '%')
        print('平均盈亏比：' + str(P4))
        print('夏普比率：' + str(P5))
        print('交易频率：' + str(P6))

        self.BT_statistic['胜率'] = str(P1) + '%'
        self.BT_statistic['年化收益率'] = str(P2) + '%'
        self.BT_statistic['最大回撤'] = str(P3) + '%'
        self.BT_statistic['平均盈亏比'] = str(P4)
        self.BT_statistic['夏普比率'] = str(P5)
        self.BT_statistic['交易频率（天）'] = str(P6)


def SQ_BT_Vector_maximum_down(dataframe):
    '''
    :param dataframe: DataFrame[fac].values
    :return:
    '''
    data = list(dataframe)
    index_j = np.argmax(np.maximum.accumulate(data) - data)  # 结束位置
    index_i = np.argmax(data[:index_j])  # 开始位置
    d = data[index_j] - data[index_i]  # 最大回撤
    return d, (index_j - index_i)