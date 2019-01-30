#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018/10/29 18:56    @Author  : xycfree
# @Descript:

from pyalgotrade.bar import Frequency
from ccwt_client.strategy.MyStrategy import Feed,  MyStrategy
def run_my_strategy():
    feed = Feed(Frequency.MINUTE)
    feed.loadBars("bitmex_XBTUSD")

    myStrategy = MyStrategy(feed, "bitmex_XBTUSD")
    myStrategy.run()

if __name__ == '__main__':
    run_my_strategy()