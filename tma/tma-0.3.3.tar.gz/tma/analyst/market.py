# -*- coding: UTF-8 -*-

"""
analyst.market - 市场行情分析
====================================================================
"""
import pandas as pd
from tma.collector import ts


def get_limit_arrived():
    """获取实时涨停板、跌停板股票列表。非交易时间段，获取的是最后一个交易时刻的结果。

    计算规则
    涨停板： 当前价格 > 昨日收盘价 * 1.095
    跌停板： 当前价格 < 昨日收盘价 * 0.905
    """
    m = ts.get_today_market(use_latest=True, interval=600)

    m = m[[
        'code', 'name', 'changepercent', 'trade',
        'open', 'high', 'low', 'settlement', 'volume'
    ]]
    la = []
    for i in m.index:
        data = m.loc[i]
        if data['volume'] == 0.0:
            continue

        # 涨停板观察
        if data['high'] > data['settlement'] * 1.095:
            if data['high'] > data['trade']:  # 盘中触及涨停板
                x = dict(data)
                x['kind'] = "盘中触及涨停板"
                la.append(x)
            elif data['high'] == data['low']:  # 一字涨停板
                x = dict(data)
                x['kind'] = "一字涨停板"
                la.append(x)
            elif data['high'] == data['trade']:  # 涨停板
                x = dict(data)
                x['kind'] = "涨停板"
                la.append(x)
            else:
                continue

        # 跌停板观察
        if data['low'] < data['settlement'] * 0.905:
            if data['trade'] > data['low']:  # 盘中触及跌停板
                x = dict(data)
                x['kind'] = "盘中触及跌停板"
                la.append(x)
            elif data['high'] == data['low']:  # 一字跌停板
                x = dict(data)
                x['kind'] = "一字跌停板"
                la.append(x)
            elif data['low'] == data['trade']:  # 跌停板
                x = dict(data)
                x['kind'] = "跌停板"
                la.append(x)
            else:
                continue

    df_la = pd.DataFrame(la)
    df_la = df_la[['code', 'name', 'trade', 'open', 'high', 'low',
                   'kind', 'changepercent']]
    df_la = df_la.sort_values('kind')
    return df_la





