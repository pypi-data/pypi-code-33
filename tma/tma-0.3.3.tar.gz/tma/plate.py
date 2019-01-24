# coding: utf-8
import traceback

from tma.share import Share


class Plate(object):
    """概念板块对象"""
    def __init__(self, name, shares, cache_interval=0):
        """

        :param name: str
            板块名称
        :param shares: list of str / list of Share obj
            板块的股票列表，如 ['600122', '002235']
        :param cache_interval: int
            缓存有效时长（单位：s），默认值为 0
        """
        self.name = name
        self.shares = []
        total_shares = len(shares)
        for i, code in enumerate(shares, 1):
            if isinstance(code, str):
                try:
                    self.shares.append(Share(code, cache_interval=cache_interval))
                    print("%i/%i: success on %s" % (i, total_shares, code))
                except:
                    traceback.print_exc()
                    print("create share object fail on %s" % code)
            elif isinstance(code, Share):
                self.shares.append(code)
            else:
                raise ValueError('share must be str or Share obj')

    def strength(self, indicator, method='avg'):
        """计算板块强弱

        :param indicator: str
            计算所依据的指标
        :param method: str
            指标聚合的方法，可选值 ['avg', 'sum']
        :return:
        """
        res = []
        for share in self.shares:
            res.append(share.indicators[indicator].value)

        if method == 'avg':
            s = round(sum(res)/len(res), 4)
        elif method == 'sum':
            s = sum(res)
        else:
            raise ValueError
        return s

    def __getitem__(self, item):
        return self.shares[item]

    def __len__(self):
        return len(self.shares)




