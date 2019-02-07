#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time   : 2018/12/21 4:57 PM 
# @Author : xbzheng

import os
from kafkatool.config.kconf import (
    KConf, KConsumerConf, KProducerConf, DEFAULT_PRODUCER_CONFIG, DEFAULT_CONSUMER_CONFIG
)

nodes = [
    "47.110.54.206:9092",
    "47.110.52.44:9092",
    "47.110.34.37:9092",
    "47.110.41.120:9092"
]
servers = ','.join(nodes)

producer_config = KProducerConf(
    {
        'bootstrap.servers': servers,
    }
)

consumer_config = KConsumerConf(
    {
        'bootstrap.servers': servers
    }
)

# file path
cur_dir = os.path.dirname(os.path.realpath(__file__))

test_conf = os.path.join(cur_dir, 'test.yaml')
test_consume_conf = os.path.join(cur_dir, 'test_consume.yaml')
test_produce_conf = os.path.join(cur_dir, 'test_produce.yaml')
