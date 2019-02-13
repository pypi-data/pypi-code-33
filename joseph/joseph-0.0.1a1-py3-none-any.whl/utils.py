import numpy as np
import pandas as pd
import ivolat3


def get_atm_strike(price, intervals):
    """ATMの権利行使価格を算出

    原資産価格からATMの権利行使価格を算出

    Parameters
    ----------
    price: int, float
        原資産価格
    intervals: int
        権利行使価格の刻み幅

    Returns
    -------
    int
        ATMの権利行使価格

    """
    fd = price // intervals
    lower = intervals * fd
    upper = lower + intervals
    di = {abs(lower - price): lower, abs(upper - price): upper}
    return di[min(di)]


def get_ntm_strike(price, atm, intervals):
    """ATMの次に近い権利行使価格を算出

    ATMのIVを算出するための権利行使価格

    Parameters
    ----------
    price: int, float
        原資産価格
    atm: int
        ATMの権利行使価格
    intervals: int
        権利行使価格の刻み幅

    Returns
    -------
    int
        ATMの次に近い権利行使価格
    """
    if price == atm:
        return atm
    lower = atm - intervals
    upper = atm + intervals
    diff_lower = abs(price - lower)
    diff_upper = abs(price - upper)
    return {diff_lower: lower, diff_upper: upper}[min(diff_lower, diff_upper)]


def interpolate(target, x, y):
    """線形補間

    与えられたデータ(x)をソートしてから線形補間

    target: float
        補完対象のx値
    x: 1-D sequence
        x値
    y: 1-D sequence
        y値

    """
    x, y = np.array(x), np.array(y)
    y = y[np.argsort(x)]
    x.sort()
    return np.interp(target, x, y)


def get_digit_from_fop_type(fop_type):
    """デリバティブの種別を番号に変換

    Call: 0
    Put: 1
    Futures: 2

    Parameters
    ----------
    fop_type : str, int
        (c, call, 0), (p, put, 1), (f, fut, futures, 2)

    Returns
    -------
    int
        Call: 0
        Put: 1
        Futures: 2

    """
    if isinstance(fop_type, str):
        fop_type = fop_type.lower()
    else:
        fop_type = int(fop_type)

    return {
        "c": 0,
        "call": 0,
        0: 0,
        "p": 1,
        "put": 1,
        1: 1,
        "f": 2,
        "fut": 2,
        "futures": 2,
        2: 2,
    }[fop_type]


def fill_zero_under_threshold(prices, right, threshold=2):
    """threshold未満のプレミアムがあればその外側の行使価格を0とする

    プレミアムの最小値がthreshold未満であった場合の権利行使価格をkとすると
    Put: k未満の権利行使価格のプレミアムを0
    Call: kより大きい権利行使価格のプレミアムを0

    Parameters
    ----------
    prices: pandas.Series
        index: 権利行使価格
        values: プレミアム
    
    right: str, int
        call(0) or put(1)

    Returns
    -------
    pandas.Series
        index: 権利行使価格
        values: プレミアム

    """
    if not prices.any():
        return prices
    
    prices_ = prices.copy()
    if prices_.min() > threshold:
        return prices_

    fop_type = get_digit_from_fop_type(right)
    idxmin_loc = prices_.index.get_loc(prices_.idxmin())

    if fop_type:
        prices_.iloc[:idxmin_loc] = 0
    else:
        prices_.iloc[idxmin_loc + 1 :] = 0

    return prices_


# https://en.wikipedia.org/wiki/Put–call_parity
def calc_parity(s, k, p=None, c=None, r=0, t=0):
    """パリティからオプションのプレミアムを算出

    p=を指定: コールのプレミアムを算出
    c=を指定: プットのプレミアムを算出

    Parameters
    ----------
    s: float
        原資産価格
    
    k: float
        権利行使価格
    
    p: float
        プットのプレミアム

    c: float
        コールのプレミアム

    r: float
        無リスク金利
    
    t: float
        満期までの期間(年)

    Returns
    -------
    float
        p != None: コールのプレミアム
        c != None: プットのプレミアム

    """
    if r * t:
        k = k * np.exp(-r * t)
    if p and c:
        raise ValueError
    if p or p == 0:
        return s - k + p
    elif c or c == 0:
        return k - s + c
    else:
        return np.nan


def calc_parity_from_series_data(s, price, right, r=0, t=0):
    """パリティからオプションのプレミアムを算出

    同限月複数のプレミアムを算出

    Parameters
    ----------
    s: float
        原資産価格
    
    prices: pandas.Series
        index: 権利行使価格
        values: プレミアム

    right: str, int
        call(0) or put(1)

    r: float
        無リスク金利
    
    t: float
        満期までの期間(年)

    Returns
    -------
    pandas.Series
        index: 権利行使価格
        values: プレミアム
    """
    right = get_digit_from_fop_type(right)
    vfunc = np.vectorize(calc_parity)
    k = price.index
    price_ = price.values
    if right:
        parity = vfunc(s, k, p=price_, r=r, t=t)
    else:
        parity = vfunc(s, k, c=price_, r=r, t=t)
    return pd.Series(parity, index=k)


def calc_iv_from_series_data(prices, s, r, q, t, right):
    """pandas.Seriesからインプライドボラティリティを算出

    ivolat3.ivolat関数を用いて同限月複数のIVを算出

    Parameters
    ----------
    prices: pandas.Series
        index: 権利行使価格
        values: プレミアム
    
    s: float
        原資産価格
    
    r: float
        無リスク金利
    
    q: float
        配当
    
    t: float
        満期までの期間(年)

    right: str, int
        call(0) or put(1)

    Returns
    -------
    pandas.Series
        index: 権利行使価格
        values: インプライドボラティリティ

    """
    if not prices.any():
        return prices
    
    right = get_digit_from_fop_type(right)
    prices_ = prices[prices.notnull() & (prices > 0)]
    func = {0: ivolat3.ivolat_call, 1: ivolat3.ivolat_put}[right]
    vfunc = np.vectorize(func)
    k = prices_.index.values
    p = prices_.values
    iv = pd.Series(vfunc(s, k, r, q, t, p), index=k)
    return iv.reindex(prices.index)


def calc_greeks_or_prem_from_series_data(func_name, iv, s, r, q, t, right=None):
    """pandas.Seriesからグリークスやプレミアムを算出

    ivolat3の関数を用いて同限月複数の値を算出

    Parameters
    ----------
    iv: pandas.Series
        index: 権利行使価格
        values: ボラティリティ
    
    s: float
        原資産価格
    
    r: float
        無リスク金利
    
    q: float
        配当
    
    t: float
        満期までの期間(年)

    right: str, int
        call(0) or put(1)

    Returns
    -------
    pandas.Series
        index: 権利行使価格
        values: 指定した関数の結果

    """
    if not iv.any():
        return iv
    
    if right:
        right = get_digit_from_fop_type(right)
    
    iv_ = iv[iv.notnull()]
    func = getattr(ivolat3, func_name)
    vfunc = np.vectorize(func)
    k = iv_.index.values
    result = pd.Series(vfunc(s, k, r, q, t, iv_, right), index=k)
    return result.reindex(iv.index)


def take_one_data(data):
    unique = data.unique()
    if len(unique) != 1:
        raise ValueError
    else:
        return unique[0]
    

def fill_otm(data, atm, right):
    right = get_digit_from_fop_type(right)
    if right:
        return data.sort_index().loc[:atm]
    else:
        return data.sort_index().loc[atm:][1:]