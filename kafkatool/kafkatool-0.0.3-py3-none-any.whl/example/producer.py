#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time   : 2018/12/24 4:02 PM 
# @Author : xbzheng

from kafkatool.client.producer import Producer
from kafkatool.config.kconf import KProducerConf
from kafkatool.client.sede import json_ser

import time
import datetime

producer_config = KProducerConf({'acks': 'all'}, './producer_conf.yaml')
p = Producer(producer_config, on_delivery=None, value_ser=json_ser)

v = {
    "sid": "479234495095063758",
    "nm": "天兑商票、陈明良13165897890",
    "head": "727806c74cb4fe17d1877ff9720b97e5.jpg",
    "sex": 1,
    "prov": "上海",
    "city": "虹口",
    "sig": "刹那间的才记忆深刻",
    "pno": "13165897890",
    "gn": "启智投资（承兑交流2）",
    "tp": 0,
    "text": "【泽天保理】【上海天兑】 【神龙汽车】【上海建工】【中建系】【中铁系】【中铁武汉铁路局】【中交系】【中冶系】【中车系】【航天科工系】【兵工系】【医院】【研究所】【研究院】【攀钢系】【河钢系】【太钢系】【武钢系】【宝钢系】【山钢系】【华菱钢铁】【海信】【中石油】【国网】【国电投】【西安西电】【东方电气】【龙湖】【金科】【恒大】【保利】【万科】【华润全系】【中铁上海】【中铁武汉】【中国重汽】【合肥美菱】【深圳比亚迪】【澳柯玛股份】【中联科工】【海信全系】【北方工业】【青岛啤酒】【南方晨光】【山东济南轨道】等等！ 【中国航空工业集团公司洛阳光电研究所】 …… …… 各类商票都可发来碰碰 13165897890",
    "url": "",
    "st": "2018-12-25 15:33:46",
    "tags": {
        "gg": 1,
        "cs": 1,
        "wz": 0,
        "sn": 1,
        "cz": 1,
        "cw": 1,
        "sp": 1
    }
}

start = time.time()
cnt = 600000
topic = 'test01'
try:
    while True:
        p.produce(topic, v)
        cnt -= 1
        if cnt == 0:
            break
finally:
    # you need to close producer manually
    p.close()
    end = time.time()
    print(f"total time: {(end-start)} seconds")
