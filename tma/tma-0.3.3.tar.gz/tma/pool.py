# coding: utf-8
import os
from datetime import datetime
import pandas as pd
from pathlib import Path

from tma import data_path
from tma.collector.ts import bars


class StockPool:
    def __init__(self, name, pool_path=None):
        self.name = name
        if pool_path is None:
            self.pool_path = os.path.join(data_path, name)
        else:
            self.pool_path = pool_path

        # 三级股票池缓存文件
        Path(self.pool_path).mkdir(exist_ok=True, parents=True)
        self.path = os.path.join(self.pool_path, '%s.pool' % self.name)
        self.path_hist = self.path.replace(".pool", ".pool.hist")

        # 如果pool_path路径下已经有名称为name的股票池，恢复；否则，新建
        if os.path.exists(self.path):
            self.restore()
        else:
            self.shares = []

    # 三级股票池的保存与恢复
    # --------------------------------------------------------------------
    def save(self):
        """把股票池中的股票保存到文件"""
        shares = [str(dict(share)) + "\n" for share in self.shares]
        with open(self.path, 'w', encoding='utf-8') as f:
            f.writelines(shares)

    def restore(self):
        """从文件中恢复股票池"""
        with open(self.path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        self.shares = [eval(x) for x in lines]

    @property
    def shares_hist(self):
        """查看选股历史"""
        with open(self.path_hist, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return [eval(x) for x in lines]

    # 添加股票
    # --------------------------------------------------------------------
    def add(self, codes, reason):
        """添加多只股票到股票池

        Note: 每只股票可以多个入选理由，因此存在多条记录。

        :param codes: str or list
            股票代码
        :param reason: str
            选股逻辑
        :return: None
        """
        dt = datetime.now().date().__str__().split(".")[0]
        if isinstance(codes, str):
            codes = [codes]
        for code in codes:
            share = dict()
            share['code'] = code
            share['dt'] = dt
            share['reason'] = reason
            self.shares.append(share)
        self.save()

    # 查看股票
    # --------------------------------------------------------------------
    def check(self, code):
        """查看股票

        :param code: 股票代码
        :type code: str
        :return: 股票池中对应code、level的所有数据
        :rtype: list
        """
        shares_l = self.shares
        shares = [x for x in shares_l if x['code'] == code]
        return shares

    # 删除股票
    # --------------------------------------------------------------------
    def remove(self, code):
        """删除股票

        :param code: str
            股票代码
        :return: None
        """
        shares_l = self.shares
        removed = [share for share in shares_l if share['code'] == code]
        removed = [str(dict(share)) + "\n" for share in removed]
        with open(self.path_hist, 'a', encoding='utf-8') as f:
            f.writelines(removed)

        shares_l = [share for share in shares_l if share['code'] != code]
        self.shares = shares_l
        self.save()

    # 检查各级股票池的表现
    # --------------------------------------------------------------------
    def check_performance(self):
        """查看股票池的表现"""
        shares_l = self.shares
        codes_l = list(set([x['code'] for x in shares_l]))
        batch_num = int(len(codes_l) / 800) + 1

        res = []
        for i in range(batch_num):
            codes = codes_l[i * 800: (i + 1) * 800]
            res.append(bars(codes))
        codes_bar = pd.concat(res, ignore_index=True)

        # 计算赚钱效应
        codes_bar['price'] = codes_bar['price'].astype(float)
        codes_bar['pre_close'] = codes_bar['pre_close'].astype(float)
        codes_bar['change'] = codes_bar['price'] - codes_bar['pre_close']
        up_nums = len(codes_bar[codes_bar['change'] > 0])
        down_nums = len(codes_bar[codes_bar['change'] <= 0])
        total_nums = len(codes_bar)

        return {
            "up_nums": up_nums,
            "down_nums": down_nums,
            "total_nums": total_nums,
            "up_rate": round(up_nums / total_nums, 4)
        }

    def __repr__(self):
        return "<StockPool Object of %s>" % self.name
